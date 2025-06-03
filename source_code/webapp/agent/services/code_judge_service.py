import grpc
from config.services import BaseService
from proto import judger_pb2, judger_pb2_grpc


class CodeJudgeService(BaseService):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def execute(
        self,
        language,
        code,
        expected_output,
        timeout_seconds=5,
        memory_limit_mb=128,
        inputs=None,
    ):
        """
        Judge the given code in the specified programming language.
        :param language: The programming language of the code (e.g., "python").
        :param code: The code to be judged as a string.
        :param expected_output: List of expected output lines.
        :param inputs: List of input lines (optional).
        :return: An object containing the judge result.
        """
        return CodeJudgeService.judge_code(
            language, code, expected_output, timeout_seconds, memory_limit_mb, inputs
        )

    @staticmethod
    def judge_code(
        language,
        code,
        expected_output,
        timeout_seconds=5,
        memory_limit_mb=128,
        inputs=None,
    ):
        """
        Judge the given code in the specified programming language.
        :param language: The programming language of the code (e.g., "python").
        :param code: The code to be judged as a string.
        :param expected_output: List of expected output lines.
        :param inputs: List of input lines (optional).
        :return: An object containing the judge result.
        """
        channel = grpc.insecure_channel("code-judger:50052")
        stub = judger_pb2_grpc.CodeJudgerStub(channel)

        version = {
            "python": "3.12",
            "ruby": "3.2",
        }

        request = judger_pb2.JudgeRequest(
            code=code,
            language=language,
            version=version.get(language, "3.12"),
            timeout_seconds=timeout_seconds,
            memory_limit_mb=memory_limit_mb,
            input=inputs if inputs else [],
            expected_output=expected_output if expected_output else [],
        )
        try:
            response = stub.JudgeCode(request)
            return response
        except Exception as e:
            return type(
                "Obj",
                (),
                {
                    "correct": False,
                    "actual_output": "",
                    "expected_output": expected_output,
                    "stdout": "",
                    "stderr": str(e),
                    "execution_time_ms": 0,
                    "memory_used_kb": 0,
                    "error_message": str(e),
                },
            )()
