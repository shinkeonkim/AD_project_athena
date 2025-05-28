import logging
from typing import List, Tuple

from article.exceptions import (
    ArticleCollectException,
    InvalidProblemIdException,
    InvalidProblemRangeException,
)
from article.services.article_collect_service import ArticleCollectService
from bs4 import BeautifulSoup
from celery import shared_task
from openai import OpenAIError
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


@shared_task
def collect_articles_for_problem_list(
    problem_ids: List[int], max_articles: int = 10
) -> List[int]:
    """여러 문제에 대한 게시글을 수집하는 태스크"""
    service = ArticleCollectService()
    collected_articles = []

    for problem_id in problem_ids:
        try:
            if problem_id <= 0:
                raise InvalidProblemIdException(
                    f"Invalid problem ID: {problem_id}", {"problem_id": problem_id}
                )
            articles = service.perform_collect_articles(
                problem_id=problem_id, max_articles=max_articles
            )
            collected_articles.extend([article.id for article in articles])
        except ArticleCollectException as e:
            logger.error(
                f"Error collecting articles for problem {problem_id}: {str(e)}"
            )
            continue
        except Exception as e:
            logger.error(f"Unexpected error for problem {problem_id}: {str(e)}")
            continue

    return collected_articles


@shared_task
def collect_articles_for_problem_range(
    start_id: int, end_id: int, max_articles: int = 10
) -> List[int]:
    """특정 범위의 문제에 대한 게시글을 수집하는 태스크"""
    if start_id <= 0:
        raise InvalidProblemRangeException(
            "Start ID must be greater than 0", {"start_id": start_id}
        )
    if end_id < start_id:
        raise InvalidProblemRangeException(
            "End ID must be greater than or equal to Start ID",
            {"start_id": start_id, "end_id": end_id},
        )

    problem_ids = list(range(start_id, end_id + 1))
    return collect_articles_for_problem_list(problem_ids, max_articles=max_articles)
