from django.core.exceptions import ValidationError


class BaseException(Exception):
    """BaseException의 기본 예외 클래스"""

    def __init__(self, message: str, data: dict = None):
        self.message = message
        self.data = data or {}
        super().__init__(self.message)


class ArticleCollectException(BaseException):
    """ArticleCollectService의 기본 예외 클래스"""

    pass


class ArticleValidationException(BaseException, ValidationError):
    """게시글 수집 관련 검증 예외의 기본 클래스"""

    pass


class InvalidProblemRangeException(ArticleValidationException):
    """잘못된 문제 ID 범위에 대한 예외"""

    pass


class InvalidProblemIdException(ArticleValidationException):
    """잘못된 문제 ID에 대한 예외"""

    pass


class ArticleScrapingException(ArticleCollectException):
    """웹 스크래핑 중 발생하는 예외"""

    pass


class ArticleParsingException(ArticleCollectException):
    """웹 페이지 파싱 중 발생하는 예외"""

    pass


class CodeBlockExtractionException(ArticleCollectException):
    """코드 블록 추출 중 발생하는 예외"""

    pass


class ContentStructureException(ArticleCollectException):
    """콘텐츠 구조화 중 발생하는 예외"""

    pass


class ProblemRelevanceException(ArticleCollectException):
    """문제 관련성 판단 중 발생하는 예외"""

    pass


class OpenAIServiceException(ArticleCollectException):
    """OpenAI API 호출 중 발생하는 예외"""

    pass


class SearchServiceException(ArticleCollectException):
    """검색 서비스 호출 중 발생하는 예외"""

    pass
