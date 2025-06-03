import json
import logging
import os

import requests
from agent.models import QuestionTask, QuestionTaskStatus
from agent.services.code_judge_service import CodeJudgeService
from article.models import Article
from celery import shared_task
from django.conf import settings
from django.db import transaction
from user.models import Ticket

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent"

logger = logging.getLogger(__name__)


@shared_task
def process_question_task(task_uuid):
    logger.info(f"Question task 처리 시작 - UUID: {task_uuid}")

    task = QuestionTask.objects.get(uuid=task_uuid)
    task.status = QuestionTaskStatus.IN_PROGRESS
    task.save()
    logger.info(f"Task 상태 업데이트: IN_PROGRESS - Problem: {task.problem.title}")

    try:
        # 1. Judge code for all test cases first
        test_cases = list(task.problem.test_cases.all())
        judge_results = []
        for tc in test_cases:
            inputs = tc.input_data.split("\n") if tc.input_data else []
            expected_output = tc.output_data.split("\n") if tc.output_data else []
            result = CodeJudgeService().execute(
                language=task.language,
                code=task.code,
                expected_output=expected_output,
                timeout_seconds=5,
                memory_limit_mb=128,
                inputs=inputs,
            )
            judge_results.append(result)
            if not getattr(result, "correct", False):
                task.feedback = "반례 테스트케이스가 존재합니다. 해당 테스트케이스를 고려하여 문제를 다시 풀어보세요."
                task.code_result = json.dumps(
                    {
                        "inputs": inputs,
                        "expected_output": expected_output,
                        "actual_output": getattr(result, "actual_output", ""),
                        "stdout": getattr(result, "stdout", ""),
                        "stderr": getattr(result, "stderr", ""),
                        "error_message": getattr(result, "error_message", ""),
                    },
                    ensure_ascii=False,
                )
                task.status = QuestionTaskStatus.COMPLETED
                task.save()
                logger.info("Judge에서 정답이 아님. LLM 호출 없이 종료.")
                return

        # 관련 Article 정보 수집
        logger.info(f"관련 Article 정보 수집 시작 - Problem: {task.problem.title}")
        related_articles = Article.objects.filter(
            problem=task.problem,
            relevance_confidence__gte=0.7,  # 신뢰도 0.7 이상인 게시글만 선택
        ).order_by("-relevance_confidence")[
            :5
        ]  # 상위 5개만 선택

        logger.info(f"수집된 Article 수: {len(related_articles)}개")

        # Article 정보 구조화
        article_info = []
        for article in related_articles:
            article_info.append(
                {
                    "summary": article.summary,
                    "approach": article.approach,
                    "complexity_analysis": article.complexity_analysis,
                    "additional_tips": article.additional_tips,
                    "relevance_confidence": article.relevance_confidence,
                }
            )
            logger.debug(
                f"Article 정보 구조화 완료 - 신뢰도: {article.relevance_confidence}"
            )

        # Prepare the prompt for the LLM
        logger.info("LLM 프롬프트 생성 시작")
        prompt = f"""
        당신은 코딩 인터뷰를 풀고 있는 학생을 위해 도움을 주는 교사입니다.
        당신은 누구보다도 알고리즘 문제 풀이에 대한 경험이 많은 사람입니다.
        당신은 학생의 코드에 대한 피드백을 제공해야 합니다.

        - 절대 학생의 코드를 통해 정답코드를 제공하거나, 답안을 바로 제시하지 마세요.
        - 주어지는 문제 정보와 관련 게시글 정보를 참고하여 학생의 코드에 대한 피드백을 제공해주세요.
        - 주어지는 코드나 문제정보를 다시 반환하지 마세요.
        - 피드백은 한글로 제공해주세요.
        - 피드백은 학생을 격려하지만, 비판적인 내용으로 끝나야합니다.
        - 정답을 제시하지 마세요.
        - 예를 들어, OOO에 대한 접근은 잘 하고 있습니다. 다만, XXX에 대한 내용은 다시 생각해보세요. 라는 식으로 제공하세요.

        Problem: {task.problem.title}
        Problem Description: {task.problem.description}
        Problem Input: {task.problem.input_description}
        Problem Output: {task.problem.output_description}
        Problem Extra Information: {task.problem.extra_information}
        Problem Category: {task.problem.categories.all()}
        Problem TestCase: {task.problem.test_cases.all().values('input_data', 'output_data')}

        Code: {task.code}
        Language: {task.language}

        Related Articles Information:
        {json.dumps(article_info, ensure_ascii=False, indent=2)}"""

        logger.debug(f"생성된 프롬프트 길이: {len(prompt)} 문자")

        # Make request to Gemini API
        logger.info("Gemini API 호출 시작")
        response = requests.post(
            f"{GEMINI_API_URL}?key={settings.GEMINI_API_KEY}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 200:
            result = response.json()
            feedback = (
                result.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "No feedback generated")
            )
            logger.info(f"피드백 생성 성공 - 길이: {len(feedback)} 문자")

            task.feedback = feedback
            task.status = QuestionTaskStatus.COMPLETED
            logger.info("Task 상태 업데이트: COMPLETED")
        else:
            error_msg = (
                f"Gemini API request failed with status code: {response.status_code}"
            )
            if response.text:
                try:
                    error_detail = response.json()
                    error_msg += f"\nError details: {error_detail}"
                except:  # noqa: E722
                    error_msg += f"\nResponse text: {response.text}"
            logger.error(f"Gemini API 호출 실패: {error_msg}")
            task.status = QuestionTaskStatus.FAILED
            task.save()
            raise Exception(error_msg)

        task.save()
        logger.info("Task 저장 완료")

    except Exception as e:
        logger.error(f"Task 처리 중 예외 발생: {str(e)}", exc_info=True)
        with transaction.atomic():
            task.status = QuestionTaskStatus.FAILED
            user = task.user
            ticket, _ = Ticket.objects.get_or_create(user=user)
            ticket.decrease_usage()
            ticket.save()
            task.save()
            logger.info(
                f"실패 상태로 Task 저장 완료 - 사용자: {user.email if user else 'None'}"
            )
        raise e

    logger.info(f"Question task 처리 완료 - UUID: {task_uuid}")
