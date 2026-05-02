from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
import re
import os
from datetime import datetime
import time
import requests
from bs4 import BeautifulSoup
from readability import Document
from markdownify import markdownify

def get_session(p):
  response = requests.get(
                "http://host.docker.internal:9223/json/version",
                headers={"Host": "localhost"}
            )
  data = response.json()
  ws_url = data.get('webSocketDebuggerUrl')
  ws_url = ws_url.replace("localhost", "host.docker.internal:9223")
  browser = p.chromium.connect_over_cdp(
      ws_url,
      headers = {"Host": "localhost"}
  )
  # すでに開いているページ（日経の画面）を取得
  context = browser.new_context()

    # 3. そのシークレットコンテキスト内に新しいページを作成
  page = context.new_page()
  return page


def Login(page):
  try:
    page.goto("https://xtech.nikkei.com/")
  except Exception as e:
    raise Exception("ページの読み込みに遷移に失敗しました。") from e
  try:
    page.wait_for_selector('.btnFunc.-login')
    page.click('.btnFunc.-login')
    page.get_by_test_id("email").fill("30298008a@gmail.com", timeout=5000)
    page.click('button[data-testid="submit"]')
  except Exception as e:
    raise Exception("メールアドレスの入力または送信に失敗しました") from e
  try:
    page.wait_for_selector("input[data-testid='password']")
    page.get_by_test_id("password").fill("30293029aA", timeout=5000)
    page.click('button[data-testid="submit"]')
    return page
  except Exception as e:
    raise Exception("パスワードの入力または送信に失敗しました") from e

def navigate_to_it_page(page, detail_keyword):
  try:
    page.wait_for_timeout(1000)
    page.wait_for_selector('.l-header_search_field')
    page.fill('.l-header_search_field', detail_keyword)
    page.click('.l-header_search_submit')
    return page
  except Exception as e:
    print(f"{detail_keyword}の検索フィールドへの入力または送信に失敗しました: {e}")
    return None

def get_total_page(page, detail_keyword):
  try:
    page.wait_for_load_state('domcontentloaded')
    target_element = page.locator('ul.pagination_list')
    total_page_locator = target_element.locator('li.pagination_list_item').last
    total_page = total_page_locator.locator('a').inner_text().strip()
    total_page_int = int(re.sub(r'\D', '', total_page))
    print(f"{detail_keyword}の総ページ数: {total_page_int}")
    return page, total_page_int
  except Exception as e:
    print(f"{detail_keyword}の総ページ数の取得に失敗しました: {e}")
    return page, None

def roop_page(page, detail_keyword):
  page, total_page = get_total_page(page, detail_keyword)
  if total_page is None:
     total_page = 5
  return page, total_page

def get_contents(page):
  # ページから必要な内容を抽出するロジックをここに実装
  # 例: 記事のタイトル、URL、公開日などを抽出
  contents = page.content()
  return contents

def extract_data(page, date_info,out_path, page_num, detail_keyword):
  # データ抽出のロジックをここに実装
  # 例: 記事のタイトル、URL、公開日などを抽出

  # そのカテゴリのループの継続フラグ
  should_stop_flug = False
  path_data = []
  get_targets = []
  oldest_date = min(date_info)
  articles = page.locator('li.articleList_item.nxt_charge').all()  
  context = page.context
  if not articles:
    print(f"ページ{page_num}に記事が見つかりませんでした。")
    return page, path_data
  for i, article in enumerate(articles):
    print(f"記事{i + 1}を処理中...")
    page.wait_for_timeout(500)  # 各記事の処理前に少し待機
    #記事の保存ファイルのパスを作成
    article_date = article.locator('time.articleList_item_date').inner_text().strip()
    article_date = datetime.strptime(article_date, '%Y.%m.%d').date()
    # 記事の日付が指定された日付より古い場合はスキップ
    if article_date < oldest_date:
      should_stop_flug = True
      break
    if article_date in date_info:
        output_path_dir = os.path.join(out_path, str(article_date).replace('-', ''), detail_keyword)
        if not os.path.exists(output_path_dir):
            os.makedirs(output_path_dir)
        h3_tag = article.locator('h3.articleList_item_title.-articleTitle')
        a_tag = h3_tag.locator('a').get_attribute('href')
        if a_tag:
          full_a_tag = urljoin("https://xtech.nikkei.com/", a_tag)
          target_dict = {
            'url': full_a_tag,
            'date': article_date,
            "output_path_dir": output_path_dir
          }
          get_targets.append(target_dict)
        else:
          continue
    else:
      continue
  
  #　新しいタブで記事が保存されるループ
  context = page.context
  for i, target_dict in enumerate(get_targets):
    print(f"記事{i + 1}を新しいタブで保存中: {target_dict['url']}")
    new_tag = context.new_page()
    try:
      url = target_dict['url']
      article_date = target_dict['date']
      output_path_dir = target_dict['output_path_dir']
      # DOMが表示されるまで待つ
      new_tag.goto(url, wait_until='domcontentloaded', timeout=20000)
      new_tag.wait_for_timeout(1000)
      ariticle_content = new_tag.content()
      # BeautifulSoupを使用して、指定されたクラスを持つdivタグをfigureタグに変換
      soup = BeautifulSoup(ariticle_content, 'html.parser')
      for target_div in soup.find_all('div', class_=re.compile(r'bpbox_center|bpimage_center|bpimage_image')):
        target_div.name = 'figure'
      # motified_contentをDocumentに渡してタイトルと要約を抽出し、Markdown形式で保存
      motified_content = str(soup)
      markdown_content = Document(motified_content)
      title = markdown_content.title()
      summary = markdown_content.summary()
      markdown_content = f"# {title}\n\n{markdownify(summary)}"
      article_path = os.path.join(output_path_dir, f'article_{page_num}_{i + 1}.md')
      with open(article_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    # 保存した記事のパスをpath_dataに追加
      path_info = {
        'keyword': detail_keyword,
        'page_num': page_num,
        'date': article_date,
        'article_num': i + 1,
        'article_path': article_path
      }
      path_data.append(path_info)
    except Exception as e:
      print(f"記事{i + 1}の内容の保存に失敗しました: {e}")
    finally:
      new_tag.close()
      
  return page, path_data, should_stop_flug

def download(date_info,output_path):
  try:
    # 出力ディレクトリが存在しない場合は作成
    if not os.path.exists(output_path):
      os.makedirs(output_path)
    with sync_playwright() as p:
      page = get_session(p)
      #　メアドとパスワードを入力してログイン
      try:
          page = Login(page)
      except Exception as e:
        print('ログインに失敗しました:', e)
        raise Exception(f"ログインに失敗したためリトライします: {e}")
      #　ダウンロードファイルの保存をリストに格納
      downloads_path_list = []
      # カテゴリごとに関連ページに遷移
      for detail_keyword in ['IT', 'AI', 'Sier', '日立', 'DX']:
          search_page = navigate_to_it_page(page, detail_keyword)
          if search_page is None:
            print(f"{detail_keyword}のページへの遷移に失敗しました。次のキーワードに進みます。")
            continue
          #検索に成功したタイミングでページの内容を更新
          print(f"{detail_keyword}の検索に成功しました。{detail_keyword}のダウンロードを開始します。")
          page = search_page
          #各キーワードでのページ遷移数を取得
          page, total_page = roop_page(page, detail_keyword)
          #カテゴリごとに1ページずつループ
          for page_num in range(1, total_page + 1):
            print(f"{detail_keyword}のダウンロード中：{page_num}/{total_page}")
            page.wait_for_timeout(1000)
            page, downloads_path, should_break = extract_data(page, date_info, output_path, page_num, detail_keyword)
            if should_break:
                print(f"{detail_keyword}のページ{page_num}で指定された日付より古い記事が見つかりました。次のキーワードに進みます。")
                break
            downloads_path_list.extend(downloads_path)
            next_link = page.locator('li.pagination_list_item.-current + li.pagination_list_item a')
            if not next_link.is_visible():
              #次のページのリンクがない場合は終了
              break
            else:
              next_link.click()
              page.wait_for_load_state('domcontentloaded')
          print(f"{detail_keyword}のダウンロードを完了しました。")
      print("すべてのダウンロードが完了しました。")
      return downloads_path_list
  except Exception as e:
    print(f"ダウンロード中にエラーが発生しました: {e}")
    raise Exception("ダウンロード処理に失敗しました") from e
    
          

def main(date_info, output_path):
    max_reries = 3
    retry_interval = 5
    for attempt in range(max_reries):
        try:
            download(date_info, output_path)
            break  # If successful, exit the retry loop
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_reries - 1:
                time.sleep(retry_interval)
            else:
                print("All retry attempts failed.")
                raise Exception("ログインやURL遷移に失敗しました。確認してください") from e

if __name__ == "__main__":
    from datetime import datetime, timedelta

    # 今日（2026年4月26日）を基準にする
    today = datetime.now().date()

# 今日から7日前までのリストを作成（今日を含めて8日間分）
    date_list = [today - timedelta(days=i) for i in range(8)]
    output_path = 'test_downloads'
    main(date_list, output_path)