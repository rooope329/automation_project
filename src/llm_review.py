from abc import ABC, abstractmethod
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv
import time
from pathlib import Path
import os

#変数のインポート
from src.consts import USER_PROMOT_TEMPLATE
from src.consts import SYSTEM_PROMPT_TEMPLATE

dotenv_path = "./.env"
load_dotenv(dotenv_path)

SYSTEM_PROMPT = SYSTEM_PROMPT_TEMPLATE
USER_PROMPT = USER_PROMOT_TEMPLATE

#llm用のクラス定義
class BaseLLM(ABC):
    @abstractmethod
    def _get_models(self):
        """各社モデルのインスタンス""(ChatBedorock等）)"""
        pass
    
    def request_review(self, system_prompt, user_prompt, news_body):
        """OCRのリクエスト"""
        model = self._get_models()
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", user_prompt)

            ]
        )
        output_parser = JsonOutputParser()
        chain = prompt | model | output_parser
        response = chain.invoke({"news_content": news_body})
        return response
class GroqBase(BaseLLM):
    def __init__(self, model_id):
        self.model_id = model_id
    def _get_models(self):
        """Groqのモデルインスタンスを返す"""
        model = ChatGroq(
            model=self.model_id
            )
        return model
    
class Groq_Llama_Scout(GroqBase):
    def __init__(self):
        # 2026年現在、無料枠で最も「ちょうどいい」最新モデル
        super().__init__("meta-llama/llama-4-scout-17b-16e-instruct")

def llm_process(groq_llama_scout, news_path):
    '''llmの処理を実施する用の関数'''
    # 記事を読み込んで、llmに渡す
    try:
        with open (news_path, "r", encoding="utf-8") as f:
            news_body = f.read()
    except Exception as e:
        print(f"記事の読み込みに失敗しました: {e}")
        return None
    # llmに依頼
    try:
        # 処理前に5秒ほど待機
        time.sleep(10)
        per_review_result = groq_llama_scout.request_review(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=USER_PROMPT,
            news_body=news_body
        )
        return per_review_result
    except Exception as e:
        print(f"レビューのリクエストに失敗しました: {e}")
        return None

def give_importance(news_path, importance):
    '''ファイルパスに重要度を追加する関数'''
    path_obj = Path(news_path)
    importnce = importance if importance is not None else "0"

    # 重要度を追加したパス名を作成
    parent_dir = path_obj.parent
    old_file_name = path_obj.name
    new_file_name = f"{importnce}_{old_file_name}"
    new_path = parent_dir / new_file_name
    # ファイル名を変更
    try:
        os.rename(news_path, new_path)
        print(f"ファイル名を変更しました: {new_path}")
    except Exception as e:
        print(f"ファイル名の変更に失敗しました: {e}")


def llm_review(downloads_path):
    try:
        #Groqのインスタンスを作成
        groq_llama_scout = Groq_Llama_Scout()
        #ニュースをループしてレビューを依頼
        for news_dict in downloads_path:
            news_path = news_dict["article_path"]
            review_result = llm_process(groq_llama_scout, news_path)
            if review_result is None:
                news_dict["importance"] = "0"
                continue
            print(f"レビュー結果: {review_result} (記事：{news_path})")
            # レビュー結果に基づいて削除対象を判定
            # 元のdictに、is_errorとimportantの情報を追加
            news_dict["importance"] = review_result.get("important", "0")
            # ファイルパスに重要度を追加
            give_importance(news_path, news_dict["importance"])
        return downloads_path
    except Exception as e:
        raise Exception(f"llm処理に失敗しました")
        
        

        
        



    