from config.services import BaseService


class CodeJudgeService(BaseService):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def execute(self, *args, **kwargs):
        """ """

        return "CodeJudgeService executed"
