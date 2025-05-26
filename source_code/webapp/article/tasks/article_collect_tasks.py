import logging
from typing import List, Tuple

from article.services.article_collect_service import ArticleCollectService
from bs4 import BeautifulSoup
from celery import shared_task
from openai import OpenAIError
from requests.exceptions import RequestException

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
            logger.info(f"Starting article collection for problem {problem_id}")
            articles = service.collect_articles_for_problem(
                problem_id, max_articles=max_articles
            )
            if articles:
                success_count += 1
                logger.info(
                    f"Successfully collected {len(articles)} articles for problem {problem_id}"
                )
            else:
                failure_count += 1
                logger.warning(f"No articles found for problem {problem_id}")

        except OpenAIError as e:
            failure_count += 1
            logger.error(
                f"OpenAI API error while collecting articles for problem {problem_id}: {str(e)}"
            )
        except RequestException as e:
            failure_count += 1
            logger.error(
                f"Network error while collecting articles for problem {problem_id}: {str(e)}"
            )
        except Exception as e:
            failure_count += 1
            logger.error(
                f"Unexpected error while collecting articles for problem {problem_id}: {str(e)}",
                exc_info=True,
            )

    logger.info(
        f"Article collection completed. Success: {success_count}, Failure: {failure_count}"
    )
    return success_count, failure_count


@shared_task
def collect_articles_for_problem_range(
    start_id: int, end_id: int, max_articles: int = 10
) -> Tuple[int, int]:
    problem_ids = list(range(start_id, end_id + 1))
    logger.info(
        f"Starting article collection for problem range {start_id} to {end_id} "
        f"(total {len(problem_ids)} problems)"
    )
    return collect_articles_for_problem_list(problem_ids, max_articles=max_articles)
