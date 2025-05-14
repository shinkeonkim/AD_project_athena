import json
import re
from typing import Any, Dict, Optional

import aiohttp
from asgiref.sync import sync_to_async
from bs4 import BeautifulSoup
from django.db import transaction
from lxml import etree, html

from ..models import Problem, ProblemCategory, ProblemTestCase


class ProblemInfoCollectService:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",  # noqa: E501
            "Accept": "application/json",
            "x-solvedac-language": "ko",
        }

    def _process_html_content(self, element) -> str:
        """
        Process HTML content to preserve mathematical expressions and formatting.

        Args:
            element: BeautifulSoup element containing HTML content

        Returns:
            str: Processed HTML content
        """
        if not element:
            return ""

        tree = html.fromstring(str(element))

        # 이미지 주소를 백준 주소로 대체하여 저장합니다.
        for img in tree.xpath("//img"):
            src = img.get("src", "")
            if src.startswith("/"):
                img.set("src", f"https://www.acmicpc.net{src}")

        # Process superscript and subscript elements
        for sup in tree.xpath("//sup"):
            new_sup = etree.Element("sup")
            new_sup.text = sup.text
            new_sup.set("class", "math-sup")
            new_sup.set("data-exponent", sup.text)
            sup.getparent().replace(sup, new_sup)

        for sub in tree.xpath("//sub"):
            new_sub = etree.Element("sub")
            new_sub.text = sub.text
            new_sub.set("class", "math-sub")
            new_sub.set("data-subscript", sub.text)
            sub.getparent().replace(sub, new_sub)

        processed_html = etree.tostring(tree, encoding="unicode", method="html")

        soup = BeautifulSoup(processed_html, "lxml")

        return str(soup)

    async def collect_problem_info(self, problem_id: int) -> Optional[Problem]:
        """
        Collect problem information from solved.ac API and Baekjoon website.

        Args:
            problem_id (int): The ID of the problem to collect

        Returns:
            Optional[Problem]: Created or updated Problem instance, None if failed
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Fetch basic problem info from solved.ac API
                api_url = (
                    f"https://solved.ac/api/v3/problem/show?problemId={problem_id}"
                )
                async with session.get(api_url, headers=self.headers) as response:
                    if response.status != 200:
                        print(f"API Error: {response.status}")
                        return None

                    problem_info = await response.json()

                # Fetch test cases from Baekjoon website
                boj_url = f"https://www.acmicpc.net/problem/{problem_id}"
                async with session.get(boj_url, headers=self.headers) as response:
                    if response.status != 200:
                        print(f"Web Error: {response.status}")
                        return None

                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    # Extract problem details
                    description = soup.find("div", {"id": "problem_description"})
                    input_desc = soup.find("div", {"id": "problem_input"})
                    output_desc = soup.find("div", {"id": "problem_output"})

                    # Process HTML content
                    description_html = self._process_html_content(description)
                    input_desc_html = self._process_html_content(input_desc)
                    output_desc_html = self._process_html_content(output_desc)

                    # Extract test cases
                    sample_inputs = soup.find_all(
                        "pre",
                        {
                            "class": "sampledata",
                            "id": lambda x: x and x.startswith("sample-input"),
                        },
                    )
                    sample_outputs = soup.find_all(
                        "pre",
                        {
                            "class": "sampledata",
                            "id": lambda x: x and x.startswith("sample-output"),
                        },
                    )

                    # Extract additional problem information
                    extra_info = {}
                    info_table = soup.find("table", {"id": "problem-info"})
                    if info_table:
                        # Get headers from thead
                        headers = [
                            th.text.strip()
                            for th in info_table.find("thead").find_all("th")
                        ]
                        # Get values from tbody
                        values = [
                            td.text.strip()
                            for td in info_table.find("tbody").find_all("td")
                        ]

                        # Map Korean headers to English keys
                        header_to_key = {
                            "시간 제한": "time_limit",
                            "메모리 제한": "memory_limit",
                            "제출": "submission_count",
                            "정답": "accepted_count",
                            "맞힌 사람": "accepted_user_count",
                            "정답 비율": "accepted_rate",
                        }

                        # Create dictionary from headers and values
                        for header, value in zip(headers, values):
                            if header in header_to_key:
                                extra_info[header_to_key[header]] = value

                    # ORM 작업을 동기 함수로 분리하고 sync_to_async로 감싸서 호출
                    return await sync_to_async(self._save_problem_info)(
                        problem_id,
                        problem_info,
                        sample_inputs,
                        sample_outputs,
                        description_html,
                        input_desc_html,
                        output_desc_html,
                        extra_info,
                    )
        except Exception as e:
            print(f"Error collecting problem {problem_id}: {str(e)}")
            return None

    def _save_problem_info(
        self,
        problem_id,
        problem_info,
        sample_inputs,
        sample_outputs,
        description,
        input_desc,
        output_desc,
        extra_info,
    ):
        with transaction.atomic():
            problem, created = Problem.objects.update_or_create(
                boj_id=problem_id,
                defaults={
                    "title": problem_info["titleKo"],
                    "description": description,
                    "input_description": input_desc,
                    "output_description": output_desc,
                    "level": problem_info["level"],
                    "extra_information": extra_info,
                },
            )
            # Update categories
            for tag in problem_info["tags"]:
                category, _ = ProblemCategory.objects.get_or_create(
                    name=tag["displayNames"][0]["name"],
                    defaults={"description": tag["displayNames"][0]["short"]},
                )
                problem.categories.add(category)
            # Update test cases
            problem.test_cases.all().delete()  # Remove existing test cases
            for input_data, output_data in zip(sample_inputs, sample_outputs):
                ProblemTestCase.objects.create(
                    problem=problem,
                    input_data=input_data.text.strip(),
                    output_data=output_data.text.strip(),
                )
            return problem
