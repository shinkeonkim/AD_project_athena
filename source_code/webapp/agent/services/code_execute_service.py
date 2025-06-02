import grpc
from config.services import BaseService
from proto import executor_pb2, executor_pb2_grpc


class CodeExecuteService(BaseService):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def execute(
        self, language, code, timeout_seconds=5, memory_limit_mb=128, inputs=None
    ):
        """
        Executes the given code in the specified programming language.

        :param language: The programming language of the code (e.g., "python", "javascript").
        :param code: The code to be executed as a string.
        :return: An object containing the execution result, including stdout, stderr, execution time, and memory used.
        """
        return self.execute_code(
            language, code, timeout_seconds, memory_limit_mb, inputs
        )

    def execute_code(
        self, language, code, timeout_seconds=5, memory_limit_mb=128, inputs=[]
    ):
        """
        Executes the given code in the specified programming language.

        :param language: The programming language of the code (e.g., "python", "javascript").
        :param code: The code to be executed as a string.
        :return: An object containing the execution result, including stdout, stderr, execution time, and memory used.
        """
        channel = grpc.insecure_channel("code-executor:50051")
        stub = executor_pb2_grpc.CodeExecutorStub(channel)

        version = {
            "python": "3.12",
            "ruby": "3.2",
        }

        request = executor_pb2.ExecuteRequest(
            code=code,
            language=language,
            version=version[language],
            timeout_seconds=timeout_seconds,
            memory_limit_mb=memory_limit_mb,
            input=inputs if inputs else [],
        )
        try:
            response = stub.ExecuteCode(request)
            return response
        except Exception as e:
            return type(
                "Obj",
                (),
                {
                    "stdout": "",
                    "stderr": str(e),
                    "execution_time_ms": 0,
                    "memory_used_kb": 0,
                },
            )()
