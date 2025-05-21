import logging
import os
import random
import re
import time
from typing import Any, Dict, List, Literal, Optional
from urllib.parse import urlparse

import requests
from article.models import Article
from bs4 import BeautifulSoup
from django.conf import settings
from django.db import transaction
from duckduckgo_search import DDGS
from problem.models import Problem
from pydantic import BaseModel


class RelevanceResponse(BaseModel):
    """게시글 관련성 검사 응답 모델"""

    is_relevant: bool
    confidence: float
    reason: str


class ArticleParseResponse(BaseModel):
    """게시글 파싱 응답 모델"""

    title: str
    content: str
    code: str
    author: str


class ArticleCollectService:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.max_retries = 3
        self.base_delay = 2  # Base delay in seconds

        # Ollama 설정
        self.ollama_host = settings.OLLAMA_HOST
        self.ollama_port = settings.OLLAMA_PORT
        self.ollama_model = settings.OLLAMA_MODEL
        self.ollama_base_url = f"http://{self.ollama_host}:{self.ollama_port}"

        # Ollama 연결 테스트
        self._test_ollama_connection()

    def _test_ollama_connection(self):
        """Ollama 서비스 연결을 테스트합니다."""
        try:
            # 모델 목록 확인
            response = requests.get(f"{self.ollama_base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                available_models = [model["name"] for model in models]
                if self.ollama_model in available_models:
                    logging.info(f"Ollama 서비스 연결 성공 (모델: {self.ollama_model})")
                else:
                    logging.error(
                        f"지정된 모델 {self.ollama_model}을 찾을 수 없습니다. 사용 가능한 모델: {available_models}"
                    )
            else:
                logging.error(f"Ollama 서비스 연결 실패: {response.status_code}")
        except Exception as e:
            logging.error(f"Ollama 서비스 연결 테스트 중 오류 발생: {str(e)}")

    def _clean_text(self, text: str) -> str:
        """텍스트에서 불필요한 공백과 개행을 정리합니다."""
        # 연속된 공백을 하나로
        text = re.sub(r"\s+", " ", text)
        # 연속된 개행을 하나로
        text = re.sub(r"\n+", "\n", text)
        # 앞뒤 공백 제거
        text = text.strip()
        return text

    def _parse_article_with_ollama(
        self, html_content: str, url: str
    ) -> Optional[Dict[str, Any]]:
        """Ollama를 사용하여 HTML에서 게시글 정보를 추출합니다."""
        system_prompt = """You are a system that extracts article information from HTML content.
You must respond with ONLY a single JSON object in the following format, with no additional text, explanation, or markdown:
{
    "title": string,
    "content": string,
    "code": string,
    "author": string
}

Rules:
1. Extract the main title of the article
2. Extract the main content, excluding navigation, headers, footers, and other non-content elements
3. Extract any code blocks or programming code examples
4. Extract the author name if available
5. Remove any HTML tags from the extracted text
6. Clean up extra whitespace and newlines
7. If any field cannot be found, use an empty string

Do not add any text before or after the JSON object.
Do not use markdown code blocks.
Do not explain your reasoning outside the JSON object."""

        user_prompt = f"""Extract article information from the following HTML content.
URL: {url}

HTML Content:
{html_content[:8000]}...  # HTML 내용이 너무 길 경우 앞부분만 사용

Respond with ONLY a single JSON object containing the extracted information."""

        try:
            # Ollama API 호출
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": f"{system_prompt}\n\n{user_prompt}",
                    "stream": False,
                    "raw": True,
                    "options": {"temperature": 0.1, "num_predict": 500},
                },
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "").strip()

                # 응답 로깅
                logging.info(f"Ollama 원본 응답: {response_text}")

                if not response_text:
                    logging.error("Ollama API가 빈 응답을 반환했습니다.")
                    return None

                try:
                    # JSON 객체 추출
                    json_start = response_text.find("{")
                    json_end = response_text.find("}", json_start) + 1
                    if json_start == -1 or json_end == 0:
                        logging.error("응답에서 JSON 객체를 찾을 수 없습니다.")
                        return None

                    json_str = response_text[json_start:json_end]
                    # JSON 문자열 정리
                    json_str = json_str.replace("\n", " ").replace("\r", "")
                    json_str = re.sub(r"\s+", " ", json_str).strip()

                    # JSON 문자열을 파싱
                    article_data = ArticleParseResponse.model_validate_json(json_str)

                    # 텍스트 정리
                    return {
                        "title": self._clean_text(article_data.title),
                        "content": self._clean_text(article_data.content),
                        "code": self._clean_text(article_data.code),
                        "url": url,
                        "source": urlparse(url).netloc,
                        "author": self._clean_text(article_data.author),
                    }
                except Exception as e:
                    logging.error(f"Ollama 응답 파싱 실패: {str(e)}")
                    logging.error(f"파싱 실패한 응답: {response_text}")
                    return None
            else:
                logging.error(
                    f"Ollama API 호출 실패: {response.status_code} - {response.text}"
                )
                return None

        except requests.exceptions.Timeout:
            logging.error("Ollama API 호출 타임아웃")
            return None
        except Exception as e:
            logging.error(f"Ollama 게시글 파싱 중 오류 발생: {str(e)}")
            return None

    def _check_relevance_with_ollama(
        self, problem_id: int, title: str, content: str
    ) -> bool:
        """Ollama를 사용하여 게시글이 문제와 관련있는지 확인합니다."""
        system_prompt = """You are a system that determines the relevance of articles to Baekjoon Online Judge problems.
You must respond with ONLY a single JSON object in the following format, with no additional text, explanation, or markdown:
{
    "is_relevant": boolean,
    "confidence": float,
    "reason": string
}

Do not add any text before or after the JSON object.
Do not use markdown code blocks.
Do not explain your reasoning outside the JSON object.
Do not generate multiple JSON objects."""

        user_prompt = f"""Analyze if the following article is relevant to Baekjoon problem #{problem_id}.

Title: {title}
Content: {content[:1000]}...

Respond with ONLY a single JSON object containing:
1. is_relevant: true if the article discusses the problem's solution or explanation
2. confidence: your confidence score (0.0-1.0)
3. reason: brief explanation of your decision

Do not add any text before or after the JSON object.
Do not use markdown code blocks.
Do not explain your reasoning outside the JSON object.
Do not generate multiple JSON objects."""

        try:
            # Ollama API 호출
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": f"{system_prompt}\n\n{user_prompt}",
                    "stream": False,
                    "raw": True,
                    "options": {"temperature": 0.1, "num_predict": 200},
                },
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "").strip()

                # 응답 로깅
                logging.info(f"Ollama 원본 응답: {response_text}")

                if not response_text:
                    logging.error("Ollama API가 빈 응답을 반환했습니다.")
                    return False

                try:
                    # JSON 객체 추출
                    json_start = response_text.find("{")
                    json_end = response_text.find("}", json_start) + 1
                    if json_start == -1 or json_end == 0:
                        logging.error("응답에서 JSON 객체를 찾을 수 없습니다.")
                        return False

                    json_str = response_text[json_start:json_end]
                    # JSON 문자열 정리
                    json_str = json_str.replace("\n", " ").replace("\r", "")
                    json_str = re.sub(r"\s+", " ", json_str).strip()

                    # JSON 문자열을 파싱
                    relevance = RelevanceResponse.model_validate_json(json_str)
                    logging.info(
                        f"Ollama 응답 파싱 성공: {relevance.model_dump_json()}"
                    )

                    # 신뢰도가 0.7 이상인 경우에만 true 반환
                    return relevance.is_relevant and relevance.confidence >= 0.7
                except Exception as e:
                    logging.error(f"Ollama 응답 파싱 실패: {str(e)}")
                    logging.error(f"파싱 실패한 응답: {response_text}")
                    return False
            else:
                logging.error(
                    f"Ollama API 호출 실패: {response.status_code} - {response.text}"
                )
                return False

        except requests.exceptions.Timeout:
            logging.error("Ollama API 호출 타임아웃")
            return False
        except Exception as e:
            logging.error(f"Ollama 관련성 검사 중 오류 발생: {str(e)}")
            return False

    def _process_article_data(
        self, data: Dict[str, Any], problem_id: int
    ) -> Optional[Dict[str, Any]]:
        """게시글 데이터를 정리하고 관련성을 검사합니다."""
        if not data:
            return None

        # 관련성 검사
        if not self._check_relevance_with_ollama(
            problem_id, data["title"], data["content"]
        ):
            logging.info(f"게시글 관련성 검사 실패: {data['url']}")
            return None

        return data

    def _get_retry_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay with jitter."""
        delay = self.base_delay * (2**attempt)  # Exponential backoff
        jitter = random.uniform(0, 0.1 * delay)  # Add 10% jitter
        return delay + jitter

    def search_article_urls(self, problem_id: int, max_results: int = 30) -> List[str]:
        query = f"백준 {problem_id} 해설 OR 풀이"
        logging.info(f"DuckDuckGo 검색 시작: query={query}, max_results={max_results}")
        results = []

        for attempt in range(self.max_retries):
            try:
                with DDGS() as ddgs:
                    # Add a small delay between requests
                    if attempt > 0:
                        delay = self._get_retry_delay(attempt)
                        logging.info(
                            f"Retry attempt {attempt + 1}/{self.max_retries} after {delay:.2f}s delay"
                        )
                        time.sleep(delay)

                    for r in ddgs.text(query, max_results=max_results):
                        url = r.get("href")
                        if url:
                            logging.info(f"DuckDuckGo 검색 결과 URL: {url}")
                            results.append(url)
                            # Add a small delay between processing results
                            time.sleep(0.5)

                if results:
                    logging.info(
                        f"DuckDuckGo 검색 결과 총 {len(results)}개 URL 수집 완료"
                    )
                    return results

            except Exception as e:
                logging.error(
                    f"DuckDuckGo 검색 실패 (시도 {attempt + 1}/{self.max_retries}): {str(e)}"
                )
                if attempt == self.max_retries - 1:
                    logging.error(f"최대 재시도 횟수 초과: {str(e)}")
                    return []
                continue

        return results

    def scrape_article(self, url):
        """게시글을 스크래핑하고 파싱합니다."""
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                logging.error(
                    f"게시글 스크래핑 실패: {url} (상태 코드: {response.status_code})"
                )
                return None

            # Ollama를 사용하여 HTML 파싱
            return self._parse_article_with_ollama(response.text, url)

        except Exception as e:
            logging.error(f"게시글 스크래핑 중 오류 발생: {url} - {str(e)}")
            return None

    @transaction.atomic
    def collect_articles_for_problem(self, problem_id: int, max_articles: int = 10):
        logging.info(
            f"문제 {problem_id}에 대한 게시글 수집 시작 (최대 {max_articles}개)"
        )
        problem = Problem.objects.get(boj_id=problem_id)
        urls = self.search_article_urls(problem_id, max_results=max_articles)
        articles = []
        for url in urls[:max_articles]:
            data = self.scrape_article(url)
            if not data:
                logging.warning(f"게시글 파싱 실패: {url}")
                continue

            # 데이터 정리 및 관련성 검사
            processed_data = self._process_article_data(data, problem_id)
            if not processed_data:
                logging.warning(f"게시글 처리 실패: {url}")
                continue

            article, created = Article.objects.update_or_create(
                full_url=processed_data["url"],
                problem=problem,
                defaults={
                    "title": processed_data["title"],
                    "content": processed_data["content"],
                    "code": processed_data.get("code", ""),
                    "source": processed_data.get("source", ""),
                    "author": processed_data.get("author", ""),
                },
            )
            if created:
                logging.info(f"새 Article 저장: {article.full_url}")
            else:
                logging.info(f"기존 Article 갱신: {article.full_url}")
            articles.append(article)
        logging.info(f"문제 {problem_id}에 대해 총 {len(articles)}개 Article 저장 완료")
        return articles
