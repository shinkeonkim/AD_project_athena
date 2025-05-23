import logging
from typing import List, Tuple

from article.services.article_collect_service import ArticleCollectService
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def collect_articles_for_problem_list(
    problem_ids: List[int], max_articles: int = 10
) -> Tuple[int, int]:
    service = ArticleCollectService()
    success_count = 0
    failure_count = 0
    for problem_id in problem_ids:
        try:
            articles = service.collect_articles_for_problem(
                problem_id, max_articles=max_articles
            )
            if articles:
                success_count += 1
                logger.info(f"Successfully collected articles for problem {problem_id}")
            else:
                failure_count += 1
                logger.warning(f"No articles found for problem {problem_id}")
        except Exception as e:
            failure_count += 1
            logger.error(
                f"Error collecting articles for problem {problem_id}: {str(e)}"
            )
    return success_count, failure_count


@shared_task
def collect_articles_for_problem_range(
    start_id: int, end_id: int, max_articles: int = 10
) -> Tuple[int, int]:
    return collect_articles_for_problem_list(
        list(range(start_id, end_id + 1)), max_articles=max_articles
    )
