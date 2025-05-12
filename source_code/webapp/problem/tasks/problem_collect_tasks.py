import asyncio
import logging
from typing import List, Tuple

from celery import shared_task

from ..services.problem_info_collect_service import ProblemInfoCollectService

logger = logging.getLogger(__name__)


@shared_task
def collect_problem_range(start_id: int, end_id: int) -> Tuple[int, int]:
    """
    Collect problem information for a range of problem IDs.

    Args:
        start_id (int): Starting problem ID
        end_id (int): Ending problem ID

    Returns:
        Tuple[int, int]: (success_count, failure_count)
    """
    service = ProblemInfoCollectService()
    success_count = 0
    failure_count = 0

    async def collect_problems():
        nonlocal success_count, failure_count
        for problem_id in range(start_id, end_id + 1):
            try:
                problem = await service.collect_problem_info(problem_id)
                if problem:
                    success_count += 1
                    logger.info(f"Successfully collected problem {problem_id}")
                else:
                    failure_count += 1
                    logger.warning(f"Failed to collect problem {problem_id}")
            except Exception as e:
                failure_count += 1
                logger.error(f"Error collecting problem {problem_id}: {str(e)}")

    # Run the async function
    asyncio.run(collect_problems())

    logger.info(
        f"Problem collection completed. Success: {success_count}, Failures: {failure_count}"
    )
    return success_count, failure_count


@shared_task
def collect_problem_list(problem_ids: List[int]) -> Tuple[int, int]:
    """
    Collect problem information for a list of problem IDs.

    Args:
        problem_ids (List[int]): List of problem IDs to collect

    Returns:
        Tuple[int, int]: (success_count, failure_count)
    """
    service = ProblemInfoCollectService()
    success_count = 0
    failure_count = 0

    async def collect_problems():
        nonlocal success_count, failure_count
        for problem_id in problem_ids:
            try:
                problem = await service.collect_problem_info(problem_id)
                if problem:
                    success_count += 1
                    logger.info(f"Successfully collected problem {problem_id}")
                else:
                    failure_count += 1
                    logger.warning(f"Failed to collect problem {problem_id}")
            except Exception as e:
                failure_count += 1
                logger.error(f"Error collecting problem {problem_id}: {str(e)}")

    # Run the async function
    asyncio.run(collect_problems())

    logger.info(
        f"Problem collection completed. Success: {success_count}, Failures: {failure_count}"
    )
    return success_count, failure_count
