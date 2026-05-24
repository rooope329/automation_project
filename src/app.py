from src.consts import BASE_OUTPUT_PATH
from src.consts import CSV_OUTPUT_PATH
from datetime import date, datetime
from datetime import timedelta
from typing import List
import pandas as pd
import traceback
import os

# 🔍 【検証用コード】Pythonから見えている真実のパスを特定する
print("====================================")
print(f"🔎 Pythonが探している絶対パス: {os.path.abspath(CSV_OUTPUT_PATH)}")
print(f"📁 その親フォルダ（data）は存在するか?: {os.path.exists(BASE_OUTPUT_PATH)}")
if os.path.exists(BASE_OUTPUT_PATH):
    print(f"📂 親フォルダの中にあるファイル一覧: {os.listdir(BASE_OUTPUT_PATH)}")
print("====================================")

# エラーが起きていた元のコード
import pandas as pd

headers = ["date", "keyword", "article_title", "file_path", "importance"]
empty_df = pd.DataFrame(columns=headers)
empty_df.to_csv(CSV_OUTPUT_PATH, index=False, encoding="utf-8")
