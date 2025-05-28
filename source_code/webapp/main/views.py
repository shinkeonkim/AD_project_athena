from django.shortcuts import render


def index(request):
    return render(request, "main/index.html")


def test_500_error(request):
    """500 에러 페이지 테스트를 위한 view"""
    raise Exception("This is a test 500 error")
