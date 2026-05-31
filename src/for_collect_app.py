from src.downloads import download_main
from src.llm_review import llm_review
from src.consts import BASE_OUTPUT_PATH
from src.consts import CSV_OUTPUT_PATH
from datetime import date, datetime
from datetime import timedelta
from typing import List
import pandas as pd
import traceback
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def get_date(start_offset_days: int, duratuion_days:int) -> List[str:]:
    '''
    スタート日と期間を受け取り、date型のリストを渡す
    '''
    if start_offset_days < 0 or duratuion_days < 0:
        raise ValueError("日付データで想定外の値が入力されました")
    today = datetime.now().date()
    date_list = [today - timedelta(days=i) for i in range(start_offset_days, start_offset_days + duratuion_days)]
    return date_list
    
def main(OUTPUT_PATH) -> None: 
  
  '''
  アプリケーションのメイン処理
  １：ダウンロード処理
  ２：llm処理
  ３：CSV出力
  '''
  # 1：ダウンロード処理
  # 日付のリストを取得
  date_list = get_date(0,4)
  #ダウンロード処理
  downloads = download_main(date_list, OUTPUT_PATH)
  if not downloads:
    raise Exception("対象記事が１件もありません。確認してください")

  # 2 : llm処理
  processed_path_list = llm_review(downloads)
  # 3 : csv出力
  # 収集したデータから、書き込む情報をまとめてデータフレーム型に変換する
  collected_date_list = []
  for download_data in processed_path_list:
     per_data = {
        "date": download_data["date"],
        "source": download_data["search_kind"],
        "keyword": download_data["keyword"],
        "importance": download_data["importance"],
        "title": download_data["article_title"],
        "file_path": download_data["article_path"]
     }
     collected_date_list.append(per_data)

  # 過去のデータフレームに、新しく収集したデータフレームをくっつける
  old_process_csv = pd.read_csv(CSV_OUTPUT_PATH, encoding="utf-8", header=0)
  new_process_csv = pd.DataFrame(collected_date_list)

  #2つをconcatして、上書き保存
  process_csv = pd.concat([old_process_csv, new_process_csv], ignore_index=True)
  process_csv.to_csv(CSV_OUTPUT_PATH, index=False, encoding="utf-8")
  print(f"CSV出力完了：{CSV_OUTPUT_PATH}")
  print(f"{min(date_list)}から{max(date_list)}までのデータを収集しました")

  #dataフォルダ内の日経xTECH内のフォルダを時系列順にsortする。

def execute():
  try:
     main(BASE_OUTPUT_PATH)
  except Exception as e:
     print(traceback.format_exc())

if __name__ == "__main__":
   execute()



  



