from django.contrib.auth import login, logout
from django.shortcuts import redirect, render

from .form.login_form import LoginForm
from .form.register_form import RegisterForm


def signin(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]
            login(request, user)
            return redirect("main:index")
        else:
            # 폼이 유효하지 않은 경우 에러 메시지를 템플릿에 전달
            return render(
                request,
                "user/login.html",
                {
                    "form": form,
                    "login_error": form.non_field_errors()
                    or "입력하신 정보를 확인해주세요.",
                },
            )
    else:
        form = LoginForm()
    return render(request, "user/login.html", {"form": form})


def signup(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("user:signin")
    else:
        form = RegisterForm()
    return render(request, "user/register.html", {"form": form})


def signout(request):
    logout(request)
    return redirect("/")
