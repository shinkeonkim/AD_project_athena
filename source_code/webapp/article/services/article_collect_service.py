import json
import logging
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import numpy as np
import requests
from article.models import Article
from bs4 import BeautifulSoup
from django.conf import settings
from django.db import transaction
from duckduckgo_search import DDGS
from openai import OpenAI
from problem.models import Problem
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer


class ProblemRelevance(BaseModel):
    """문제 관련성 판단 결과"""

    is_related: bool
    confidence: float
    reason: str


class CodeExplanation(BaseModel):
    """코드 설명 결과"""

    explanation: str
    time_complexity: str
    space_complexity: str
    key_points: List[str]


class ArticleStructure(BaseModel):
    """게시글 구조화 결과"""

    summary: str
    approach: str
    complexity_analysis: str
    additional_tips: str


class ArticleCollectService:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.embed_model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2", token=settings.HUGGINGFACE_TOKEN
        )
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def _get_function_schema(self, model: type[BaseModel]) -> Dict[str, Any]:
        """Pydantic 모델로부터 OpenAI function schema를 생성합니다."""
        schema = model.model_json_schema()
        return {
            "name": model.__name__,
            "description": model.__doc__ or "",
            "parameters": schema,
        }

    def _extract_tool_call(self, response: Any, model: type[BaseModel]) -> BaseModel:
        """OpenAI 응답에서 tool call을 추출하여 Pydantic 모델로 변환합니다."""
        try:
            tool_call = response.choices[0].message.tool_calls[0]
            if tool_call.function.name != model.__name__:
                raise ValueError(
                    f"Expected function {model.__name__}, got {tool_call.function.name}"
                )

            arguments = json.loads(tool_call.function.arguments)
            return model.model_validate(arguments)
        except (IndexError, KeyError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to extract tool call: {e}")

    def check_problem_relevance(
        self, problem_title: str, problem_id: int, content: str
    ) -> ProblemRelevance:
        """주어진 콘텐츠가 특정 알고리즘 문제와 관련이 있는지 판단합니다."""
        return ProblemRelevance(is_related=False, confidence=0.0, reason="")

    def is_problem_related(self, problem: Problem, content: str) -> Tuple[bool, float]:
        """Check if the content is related to the given problem using embedding similarity."""
        problem_text = f"{problem.title} {problem.description}"
        problem_embedding = self.embed_model.encode(problem_text)
        content_embedding = self.embed_model.encode(content)
        similarity = self.cosine_similarity(problem_embedding, content_embedding)

        # 유사도가 낮으면 LLM으로 더 정확한 분류
        if similarity < 0.7:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": f"다음 웹페이지가 알고리즘 문제 '{problem.title}' ({problem.boj_id})에 대한 해설인지 판별해주세요.\n\n웹페이지 내용: {content[:1000]}",
                    }
                ],
                tools=[
                    {
                        "type": "function",
                        "function": self._get_function_schema(ProblemRelevance),
                    }
                ],
                tool_choice="auto",
            )

            try:
                result = self._extract_tool_call(response, ProblemRelevance)
                return result.is_related, result.confidence
            except Exception as e:
                logging.error(f"Failed to parse problem relevance: {e}")
                return False, 0.0

        return similarity > 0.7, similarity

    def explain_code(self, language: str, code: str) -> CodeExplanation:
        """주어진 코드를 분석하고 설명합니다."""
        return CodeExplanation(
            explanation="", time_complexity="", space_complexity="", key_points=[]
        )

    def extract_code_blocks(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract code blocks from HTML content and detect their language."""
        code_blocks = []
        seen_codes = set()  # 중복 코드 방지를 위한 set
        MAX_CODE_BLOCKS = 5  # 최대 코드 블록 수
        MIN_CODE_LENGTH = 50  # 최소 코드 길이
        MAX_CODE_LENGTH = 2000  # 최대 코드 길이

        logging.info("코드 블록 추출 시작")

        # 코드 블록 찾기 (pre, code 태그)
        for pre in soup.find_all(["pre", "code"]):
            # 코드 블록의 언어 감지
            language = None
            if pre.get("class"):
                for cls in pre.get("class"):
                    if cls.startswith("language-"):
                        language = cls.replace("language-", "")
                        break

            # 코드 추출
            code = pre.get_text(strip=True)

            # 코드 블록 필터링
            if not code:
                logging.debug("빈 코드 블록 발견, 건너뜀")
                continue

            if len(code) < MIN_CODE_LENGTH:
                logging.debug(f"코드가 너무 짧음 (길이: {len(code)}), 건너뜀")
                continue

            if len(code) > MAX_CODE_LENGTH:
                logging.debug(f"코드가 너무 김 (길이: {len(code)}), 건너뜀")
                continue

            # 중복 코드 제거
            if code in seen_codes:
                logging.debug("중복 코드 블록 발견, 건너뜀")
                continue
            seen_codes.add(code)

            # 언어가 감지되지 않은 경우 코드 내용으로부터 추정
            if not language:
                if "def " in code or "import " in code:
                    language = "python"
                elif "#include" in code or "int main" in code:
                    language = "cpp"
                elif "public class" in code or "import java" in code:
                    language = "java"
                else:
                    language = "unknown"
                logging.debug(f"언어 자동 감지: {language}")

            try:
                logging.info(
                    f"OpenAI API 호출 시작 - 언어: {language}, 코드 길이: {len(code)}"
                )
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": f"다음 {language} 코드를 분석하여 설명해주세요. 다음 항목들을 모두 포함해주세요:\n1. 코드의 전체적인 설명 (explanation)\n2. 시간 복잡도 분석 (time_complexity)\n3. 공간 복잡도 분석 (space_complexity)\n4. 주요 포인트들 (key_points)\n\n코드:\n```{language}\n{code}\n```",
                        }
                    ],
                    tools=[
                        {
                            "type": "function",
                            "function": self._get_function_schema(CodeExplanation),
                        }
                    ],
                    tool_choice="auto",
                )

                explanation = self._extract_tool_call(response, CodeExplanation)
                logging.info(
                    f"코드 설명 생성 성공 - 언어: {language}, 설명 길이: {len(explanation.explanation)}"
                )

                code_blocks.append(
                    {
                        "language": language,
                        "code": code,
                        "explanation": explanation.explanation,
                        "time_complexity": explanation.time_complexity,
                        "space_complexity": explanation.space_complexity,
                        "key_points": explanation.key_points,
                    }
                )

                # 최대 코드 블록 수 제한
                if len(code_blocks) >= MAX_CODE_BLOCKS:
                    logging.info(
                        f"최대 코드 블록 수({MAX_CODE_BLOCKS}) 도달, 처리 중단"
                    )
                    break

            except Exception as e:
                logging.error(f"코드 설명 생성 실패 - 언어: {language}, 에러: {str(e)}")
                continue

        logging.info(f"코드 블록 추출 완료 - 총 {len(code_blocks)}개 블록 처리됨")
        return code_blocks

    def structure_article(self, content: str) -> ArticleStructure:
        """게시글 내용을 구조화합니다."""
        return ArticleStructure(
            summary="", approach="", complexity_analysis="", additional_tips=""
        )

    def structure_content(self, content: str) -> Dict:
        """Structure the content using LLM."""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": f"다음 알고리즘 해설 글을 분석하여 구조화해주세요. 게시글의 전체적인 내용을 요약하고, 접근 방법, 복잡도 분석, 추가 팁 등을 정리해주세요:\n\n{content[:5000]}",
                    }
                ],
                tools=[
                    {
                        "type": "function",
                        "function": self._get_function_schema(ArticleStructure),
                    }
                ],
                tool_choice="auto",
            )

            result = self._extract_tool_call(response, ArticleStructure)
            return result.model_dump()
        except Exception as e:
            logging.error(f"Failed to structure content: {e}")
            return {
                "summary": "",
                "approach": "",
                "complexity_analysis": "",
                "additional_tips": "",
            }

    def search_article_urls(self, problem_id: int, max_results: int = 30):
        query = f"백준 {problem_id} 해설 OR 풀이"
        logging.info(f"DuckDuckGo 검색 시작: query={query}, max_results={max_results}")
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                url = r.get("href")
                if url:
                    logging.info(f"DuckDuckGo 검색 결과 URL: {url}")
                    results.append(url)
        logging.info(f"DuckDuckGo 검색 결과 총 {len(results)}개 URL 수집 완료")
        return results

    def scrape_article(self, url: str) -> Optional[Dict]:
        """Scrape article content from any website."""
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                logging.warning(
                    f"Failed to fetch URL: {url}, status code: {response.status_code}"
                )
                return None

            soup = BeautifulSoup(response.text, "html.parser")

            # 제목 추출
            title = soup.find("title")
            title_text = title.text.strip() if title else "Unknown Title"

            # 메인 콘텐츠 추출
            body = soup.find("body")
            if not body:
                logging.warning(f"No body tag found in {url}")
                return None

            # 불필요한 요소 제거
            for element in body.find_all(
                ["script", "style", "nav", "header", "footer", "aside"]
            ):
                element.decompose()

            # 텍스트 콘텐츠 추출
            content = body.get_text(separator="\n", strip=True)

            # 작성자 추출
            author = ""
            author_elements = body.find_all(
                ["a", "span", "div"],
                class_=lambda x: x
                and any(
                    term in str(x).lower() for term in ["author", "writer", "byline"]
                ),
            )
            if author_elements:
                author = author_elements[0].text.strip()

            return {
                "title": title_text,
                "content": content,
                "url": url,
                "source": urlparse(url).netloc,
                "author": author,
                "soup": soup,  # BeautifulSoup 객체도 반환
            }

        except Exception as e:
            logging.error(f"Error scraping {url}: {str(e)}")
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

            # 콘텐츠가 문제와 관련 있는지 확인
            is_related, confidence = self.is_problem_related(problem, data["content"])
            if not is_related:
                logging.info(f"관련 없는 게시글 스킵: {url} (신뢰도: {confidence:.2f})")
                continue

            # 콘텐츠 추출 및 구조화
            code_blocks = self.extract_code_blocks(data["soup"])
            structured_content = self.structure_content(data["content"])

            # 구조화된 콘텐츠로 Article 데이터 업데이트
            article_data = {
                "title": data["title"],
                "full_url": data["url"],
                "site_url": urlparse(data["url"]).netloc,
                "author": data.get("author", ""),
                "source": data.get("source", ""),
                "problem": problem,
                "summary": structured_content["summary"],
                "approach": structured_content["approach"],
                "complexity_analysis": structured_content["complexity_analysis"],
                "additional_tips": structured_content["additional_tips"],
                "code_blocks": code_blocks,
                "relevance_confidence": confidence,
            }

            article, created = Article.objects.update_or_create(
                full_url=data["url"], problem=problem, defaults=article_data
            )

            if created:
                logging.info(f"새 Article 저장: {article.full_url}")
            else:
                logging.info(f"기존 Article 갱신: {article.full_url}")
            articles.append(article)

        logging.info(f"문제 {problem_id}에 대해 총 {len(articles)}개 Article 저장 완료")
        return articles
