import grpc
from config.services import BaseService
from django.db import transaction
from problem.models.problem_code import ProblemCode
from problem.models.problem_test_case import ProblemTestCase
from proto import testcase_generator_pb2, testcase_generator_pb2_grpc


class CreateProblemTestCaseService(BaseService):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def execute(self, problem):
        """
        Creates test cases for a given problem using the code-testcase-generator.

        :param problem: The Problem instance to generate test cases for
        :return: A tuple of (updated ProblemCode instance, list of created ProblemTestCase instances)
        """
        return self._create_test_cases(problem)

    def _create_test_cases(self, problem):
        """
        Internal method to create test cases for a problem.

        :param problem: The Problem instance
        :return: A tuple of (updated ProblemCode instance, list of created ProblemTestCase instances)
        """
        # Get the latest problem_code if it exists
        problem_code = (
            ProblemCode.objects.filter(problem=problem).order_by("-created_at").first()
        )

        request = testcase_generator_pb2.GenerateTestcaseRequest(
            boj_id=problem.boj_id,
            description=problem.description,
            input_description=problem.input_description,
            output_description=problem.output_description,
            validation_code=problem_code.validation_code if problem_code else "",
            solution_code=problem_code.solution_code if problem_code else "",
            num_testcases=5,  # Default number of test cases
            example_testcases=[
                testcase_generator_pb2.Testcase(
                    input=tc.input_data, output=tc.output_data
                )
                for tc in problem.test_cases.filter(is_official=True)
            ],
        )

        # Call the testcase generator service
        channel = grpc.insecure_channel("code-testcase-generator:50053")
        stub = testcase_generator_pb2_grpc.TestcaseGeneratorStub(channel)

        try:
            response = stub.GenerateTestcases(request)

            # Use transaction to ensure data consistency
            with transaction.atomic():
                # Update or create problem_code
                if problem_code:
                    problem_code.validation_code = response.validation_code
                    problem_code.solution_code = response.solution_code
                    problem_code.save()
                else:
                    problem_code = ProblemCode.objects.create(
                        problem=problem,
                        validation_code=response.validation_code,
                        solution_code=response.solution_code,
                        language="cpp",  # Default language
                    )

                # Create test cases
                test_cases = []
                for tc in response.testcases:
                    test_case = ProblemTestCase.objects.create(
                        problem=problem,
                        input_data=tc.input,
                        output_data=tc.output,
                        is_official=False,
                    )
                    test_cases.append(test_case)

                return problem_code, test_cases

        except Exception as e:
            self.logger.error(f"Failed to generate test cases: {str(e)}")
            raise RuntimeError(f"Failed to generate test cases: {str(e)}")
