import os
import re
import time
import requests
from datetime import datetime, timedelta
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from readability import Document
from markdownify import markdownify
from playwright.sync_api import sync_playwright

def get_session(p):
    """起動済みのDockerブラウザに接続し、新しいページセッションを返す"""
    response = requests.get(
        "http://host.docker.internal:9223/json/version",
        headers={"Host": "localhost"}
    )
    data = response.json()
    ws_url = data.get('webSocketDebuggerUrl').replace("localhost", "host.docker.internal:9223")
    
    browser = p.chromium.connect_over_cdp(ws_url, headers={"Host": "localhost"})
    context = browser.new_context()
    return context.new_page()

def login(page):
    """日経クロステックへのログイン処理"""
    try:
        page.goto("https://xtech.nikkei.com/")
    except Exception as e:
        raise Exception(f"ページの読み込みに失敗しました: {e}")

    try:
        page.wait_for_selector('.btnFunc.-login')
        page.click('.btnFunc.-login')
        page.get_by_test_id("email").fill("30298008a@gmail.com", timeout=5000)
        page.wait_for_timeout(5000) # ログイン完了の暗黙的な待機
        page.click('button[data-testid="submit"]')
    except Exception as e:
        raise Exception(f"メールアドレスの処理に失敗しました: {e}")

    try:
        page.wait_for_selector("input[data-testid='password']")
        page.get_by_test_id("password").fill("30293029aA", timeout=5000)
        page.wait_for_timeout(5000) 
        page.click('button[data-testid="submit"]')
        page.wait_for_timeout(1000) 
        return page
    except Exception as e:
        raise Exception(f"パスワードの処理に失敗しました: {e}")

def search_keyword(page, keyword):
    """指定したキーワードで記事を検索する"""
    try:
        page.wait_for_timeout(1000)
        page.wait_for_selector('.l-header_search_field')
        page.fill('.l-header_search_field', keyword)
        page.click('.l-header_search_submit')
        return page
    except Exception as e:
        print(f"{keyword} の検索処理に失敗しました: {e}")
        return None

def get_target_page_count(page, keyword, fallback_pages=5):
    """検索結果の総ページ数を取得する"""
    try:
        page.wait_for_load_state('domcontentloaded')
        target_element = page.locator('ul.pagination_list')
        total_page_text = target_element.locator('li.pagination_list_item').last.locator('a').inner_text().strip()
        total_pages = int(re.sub(r'\D', '', total_page_text))
        print(f"{keyword} の総ページ数: {total_pages}")
        return total_pages
    except Exception as e:
        print(f"{keyword} の総ページ数取得に失敗したため、デフォルト値({fallback_pages}ページ)を使用します: {e}")
        return fallback_pages

def collect_target_urls(page, target_dates, base_output_path, keyword):
    """一覧ページから条件に合う記事のURLを収集する"""
    try:
      page.wait_for_selector('li.articleList_item', state='visible', timeout=10000)
    except TimeoutError as e:
      pass
        
    page.wait_for_load_state('domcontentloaded')
    get_targets = []
    should_stop_flag = False
    oldest_date = min(target_dates)
    
    article_section = page.locator('section.l-section.searchResult')
    article_ul = article_section.locator('ul.articleList.-lg')
    articles = article_ul.locator('li.articleList_item:not([class="articleList_item"])').all()
    if not articles:
        return get_targets, should_stop_flag

    for article in articles:
        page.wait_for_timeout(500)
        
        date_text = article.locator('time.articleList_item_date').inner_text().strip()
        article_date = datetime.strptime(date_text, '%Y.%m.%d').date()
        
        # 探索期間より古い記事が出たらフラグを立てて終了
        if article_date < oldest_date:
            should_stop_flag = True
            break
            
        if article_date in target_dates:
            h3_tag = article.locator('h3.articleList_item_title.-articleTitle')
            a_tag = h3_tag.locator('a').get_attribute('href')
            if a_tag:
                date_dir_name = str(article_date).replace('-', '')
                output_dir = os.path.join(base_output_path, date_dir_name, keyword)
                get_targets.append({
                    'url': urljoin("https://xtech.nikkei.com/", a_tag),
                    'date': article_date,
                    'output_dir': output_dir
                })
                
    return get_targets, should_stop_flag

def download_article_content(context, target, page_num, article_num, keyword):
    """1件の記事を新しいタブで開き、Markdownとして保存する"""
    url = target['url']
    article_date = target['date']
    output_dir = target['output_dir']
    
    print(f"記事{article_num}を保存中: {url}")
    new_tab = context.new_page()
    
    try:
        new_tab.goto(url, wait_until='domcontentloaded', timeout=20000)
        new_tab.wait_for_timeout(1000)
        
        # HTMLの整形
        soup = BeautifulSoup(new_tab.content(), 'html.parser')
        for target_div in soup.find_all('div', class_=re.compile(r'bpbox_center|bpimage_center|bpimage_image')):
            target_div.name = 'figure'
        
        # Markdownへの変換
        doc = Document(str(soup))
        title = doc.title()
        summary = doc.summary()
        
        if not summary or len(summary) < 20:
            print(f"❌ 記事{article_num} の本文抽出に失敗したためスキップします。")
            return None

        full_markdown_content = f"# {title}\n\n{markdownify(summary)}"
        
        #　次のタブがある場合の処理
        '''
          次タブに移る
          「記事が読める場合は、記事の内容をMarkdown形式で保存する」処理を実装
          「記事が読めない場合（有料記事）は、スキップする」処理を実装
        '''
        next_tab = new_tab.locator("li.pagination_list_item.-current + li.pagination_list_item a")
        #　ページ数
        tabpage_num = 1
        while next_tab.is_visible():
            next_tab.click()
            print(f"記事{article_num} に次のタブが存在します。次のタブに移ります。")
            #　次タブに無料記事があれば保存
            new_tab.wait_for_load_state('domcontentloaded')
            new_tab.wait_for_timeout(1000)
            paywall_indicator = new_tab.locator('section.paywall.-gray')
            if paywall_indicator.count() > 0 and paywall_indicator.is_visible():
                print(f"記事{article_num} の次のタブは有料記事のためスキップします。")
                break
            else:
                # HTMLの整形
                print(f"記事{article_num} の次のタブは無料記事です。保存します。")
                content = new_tab.content()
                soup = BeautifulSoup(content, 'html.parser')
                for target_div in soup.find_all('div', class_=re.compile(r'bpbox_center|bpimage_center|bpimage_image')):
                    target_div.name = 'figure'
                # Markdownへの変換
                doc = Document(str(soup))
                summary = doc.summary()
                if not summary or len(summary) < 20:
                    print(f"❌ 記事{article_num} の次のタブの本文抽出に失敗したためスキップします。")
                    break
                tabpage_num += 1
                full_markdown_content += f"\n\n## {tabpage_num}ページ目\n\n{markdownify(summary)}"

        # 保存先ディレクトリを作成し、書き込み
        os.makedirs(output_dir, exist_ok=True)
        article_path = os.path.join(output_dir, f'article_{article_num}.md')
        
        with open(article_path, 'w', encoding='utf-8') as f:
            f.write(full_markdown_content)
            
        return {
            'keyword': keyword,
            'page_num': page_num,
            'date': article_date,
            'article_num': article_num,
            'article_path': article_path
        }
        
    except Exception as e:
        print(f"❌ 記事{article_num} ({url}) の保存に失敗しました: {e}")
        return None
        
    finally:
        new_tab.close()

def process_single_page(page, target_dates, base_output_path, page_num, keyword):
    """1ページ分の処理を統括する（URL収集 → 記事保存）"""
    path_data = []
    
    # 1. URL収集
    get_targets, should_stop_flag = collect_target_urls(page, target_dates, base_output_path, keyword)
    
    if not get_targets:
        if not should_stop_flag:
            print(f"ページ{page_num}に保存対象の記事はありませんでした。")
        return page, path_data, should_stop_flag

    # 2. 記事保存
    context = page.context
    for i, target in enumerate(get_targets):
        result = download_article_content(context, target, page_num, i + 1, keyword)
        if result:
            path_data.append(result)
            
    return page, path_data, should_stop_flag

def download(target_dates, output_path):
    """メインの巡回・ダウンロードフロー"""
    os.makedirs(output_path, exist_ok=True)
    downloads_path_list = []

    with sync_playwright() as p:
        page = get_session(p)
        
        try:
            page = login(page)
        except Exception as e:
            raise Exception(f"ログインに失敗したため処理を中断します: {e}")

        keywords = ['IT', 'AI', 'Sier', '日立', 'DX']
        for keyword in keywords:
            search_page = search_keyword(page, keyword)
            if not search_page:
                print(f"{keyword} のページ遷移をスキップします。")
                continue
                
            print(f"{keyword} の検索成功。ダウンロードを開始します。")
            page = search_page
            total_pages = get_target_page_count(page, keyword)
            
            for page_num in range(1, total_pages + 1):
                print(f"{keyword} のダウンロード中：{page_num}/{total_pages}")
                page.wait_for_timeout(1000)
                
                # ここで統合された process_single_page を呼び出す
                page, paths, should_break = process_single_page(page, target_dates, output_path, page_num, keyword)
                downloads_path_list.extend(paths)
                
                if should_break:
                    print(f"⏩ {keyword} のページ{page_num}で対象期間外に到達しました。次のキーワードへ進みます。")
                    break
                    
                next_link = page.locator('li.pagination_list_item.-current + li.pagination_list_item a')
                if not next_link.is_visible():
                    break
                
                next_link.click()
                page.wait_for_load_state('domcontentloaded')
                
            print(f" {keyword} の処理が完了しました。")
            
    print("🎉 すべてのダウンロード処理が完了しました。")
    return downloads_path_list

def main(target_dates, output_path):
    max_retries = 3
    retry_interval = 5
    
    for attempt in range(max_retries):
        try:
            download(target_dates, output_path)
            break
        except Exception as e:
            print(f"⚠️ 実行失敗 (試行 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_interval)
            else:
                print("❌ 全ての再試行に失敗しました。")
                raise

if __name__ == "__main__":
    today = datetime.now().date()
    # 今日を含めた直近8日間のリストを作成
    date_list = [today - timedelta(days=i) for i in range(30)]
    output_dir = 'test_downloads'
    
    main(date_list, output_dir)