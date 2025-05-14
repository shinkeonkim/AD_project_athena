import json
import os

import requests
from agent.models import QuestionTask, QuestionTaskStatus
from celery import shared_task
from django.conf import settings

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


@shared_task
def process_question_task(task_uuid):
    task = QuestionTask.objects.get(uuid=task_uuid)
    task.status = QuestionTaskStatus.IN_PROGRESS
    task.save()

    try:
        # Prepare the prompt for the LLM
        prompt = f"""
        당신은 코딩 인터뷰를 풀고 있는 학생을 위해 도움을 주는 교사입니다.
        당신은 누구보다도 알고리즘 문제 풀이에 대한 경험이 많은 사람입니다.
        당신은 학생의 코드에 대한 피드백을 제공해야 합니다.

        - 절대 학생의 코드를 통해 정답코드를 제공하거나, 답안을 바로 제시하지 마세요.
        - 주어지는 문제 정보를 참고하여 학생의 코드에 대한 피드백을 제공해주세요.
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
        Language: {task.language}"""

        print(prompt)

        # Make request to Gemini API
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

            task.feedback = feedback
            task.status = QuestionTaskStatus.COMPLETED
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
            task.status = QuestionTaskStatus.FAILED
            task.save()
            raise Exception(error_msg)

        task.save()

    except Exception as e:
        task.status = QuestionTaskStatus.FAILED
        task.save()
        raise e
