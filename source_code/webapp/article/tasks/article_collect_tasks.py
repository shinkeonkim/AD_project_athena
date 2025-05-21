import logging
from math import ceil
from typing import List, Tuple

from article.services.article_collect_service import ArticleCollectService
from celery import chord, group, shared_task
from celery.result import GroupResult

logger = logging.getLogger(__name__)

# 청크 크기 설정 (한 번에 처리할 문제 수)
CHUNK_SIZE = 5
# 동시 실행 가능한 최대 태스크 수
MAX_CONCURRENT_TASKS = 1


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
    # 전체 문제 ID 리스트 생성
    problem_ids = list(range(start_id, end_id + 1))

    # 청크로 나누기
    chunks = [
        problem_ids[i : i + CHUNK_SIZE] for i in range(0, len(problem_ids), CHUNK_SIZE)
    ]

    # 각 청크에 대한 태스크 생성
    tasks = []
    for chunk in chunks:
        task = collect_articles_for_problem_list.s(chunk, max_articles)
        tasks.append(task)

    # 청크를 MAX_CONCURRENT_TASKS 크기의 그룹으로 나누기
    task_groups = [
        group(tasks[i : i + MAX_CONCURRENT_TASKS])
        for i in range(0, len(tasks), MAX_CONCURRENT_TASKS)
    ]

    # 각 그룹을 순차적으로 실행하고 결과 수집
    total_success = 0
    total_failure = 0

    for i, task_group in enumerate(task_groups):
        logger.info(f"Processing group {i + 1}/{len(task_groups)}")
        try:
            # 그룹 실행 및 결과 대기
            result = task_group.apply_async()
            group_results = result.get(timeout=3600)  # 1시간 타임아웃

            # 결과 집계
            for success, failure in group_results:
                total_success += success
                total_failure += failure

            logger.info(
                f"Completed group {i + 1}/{len(task_groups)}. "
                f"Current totals - Success: {total_success}, Failure: {total_failure}"
            )

        except Exception as e:
            logger.error(f"Error processing group {i + 1}: {str(e)}")
            # 실패한 그룹의 결과를 부분적으로 수집
            if isinstance(result, GroupResult):
                completed_results = result.completed()
                for success, failure in completed_results:
                    total_success += success
                    total_failure += failure

    logger.info(
        f"Completed article collection for problems {start_id}-{end_id}. "
        f"Total Success: {total_success}, Total Failure: {total_failure}"
    )

    return total_success, total_failure


@shared_task
def collect_articles_for_problem_chunk(
    chunk: List[int], max_articles: int = 10
) -> Tuple[int, int]:
    """청크 단위로 문제 수집을 처리하는 태스크"""
    return collect_articles_for_problem_list(chunk, max_articles)
