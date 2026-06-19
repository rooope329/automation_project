from abc import ABC, abstractmethod
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
import time
from pathlib import Path
import os

#変数のインポート
from src.consts import USER_PROMOT_TEMPLATE
from src.consts import SYSTEM_PROMPT_TEMPLATE

SYSTEM_PROMPT = SYSTEM_PROMPT_TEMPLATE
USER_PROMPT = USER_PROMOT_TEMPLATE
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# llm用のクラス定義
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
            , groq_api_key=GROQ_API_KEY
            )
        return model
    
class Groq_Llama_Scout(GroqBase):
    def __init__(self):
        super().__init__("meta-llama/llama-4-scout-17b-16e-instruct")

def llm_process(groq_llama_scout, news_content):
    '''llmの処理を実施する用の関数'''
    # 記事を読み込んで、llmに渡す
    news_body = news_content
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

def add_importance(importance, article_title, article_content):
    '''記事に重要度を追加したタイトルを書きこむ'''
    add_importance_article_title = f"{importance}_{article_title}"
    add_title_content = f"---\ntitle: {add_importance_article_title}\n---\n# {article_title}\n\n{article_content}"
    return add_title_content


def llm_review(downloads_path):
    try:
        # Groqのインスタンスを作成
        groq_llama_scout = Groq_Llama_Scout()
        # 記事をループしてレビューを依頼
        for news_dict in downloads_path:
            article_path = news_dict["article_path"]
            article_title = news_dict["article_title"]
            article_content = news_dict["article_content"]
            review_result = llm_process(groq_llama_scout, article_content)
            if review_result is None:
                news_dict["importance"] = "0"
                continue
            print(f"レビュー結果: {review_result} (記事：{article_path})")
            # レビュー結果に基づいて削除対象を判定
            # 元のdictに、is_errorとimportantの情報を追加
            news_dict["importance"] = review_result.get("important", "0")
            # タイトルを書きこんだ、記事の内容を更新して保存する
            updated_content = add_importance(news_dict["importance"], article_title, article_content)
            with open(article_path, "w", encoding="utf-8") as f:
                f.write(updated_content)

        return downloads_path
    except Exception as e:
        raise Exception(f"llm処理に失敗しました")
        
        

        
        



    