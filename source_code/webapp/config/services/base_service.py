import logging
from abc import ABC, abstractmethod
from typing import Any


class BaseService(ABC):
    """서비스 클래스의 기본 클래스"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """실제 서비스 로직을 구현하는 메서드"""
        pass

    def perform(self, *args, **kwargs) -> Any:
        """서비스 실행을 위한 메인 메서드"""
        try:
            self.logger.info(f"Starting {self.__class__.__name__} execution")
            result = self.execute(*args, **kwargs)
            self.logger.info(
                f"Successfully completed {self.__class__.__name__} execution"
            )
            return result
        except Exception as e:
            self.logger.error(
                f"Unexpected error in {self.__class__.__name__}: {str(e)}",
                exc_info=True,
            )
            raise Exception(
                f"Unexpected error in {self.__class__.__name__}: {str(e)}",
                data={"original_error": str(e)},
            )
