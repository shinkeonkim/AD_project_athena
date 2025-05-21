from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.views import View
from user.forms import SignInForm


class SignInView(View):
    def get(self, request):
        form = SignInForm()
        return render(request, "user/signin.html", {"form": form})

    def post(self, request):
        form = SignInForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]
            login(request, user)
            return redirect("main:index")
        else:
            return render(
                request,
                "user/signin.html",
                {
                    "form": form,
                    "login_error": form.non_field_errors()
                    or "입력하신 정보를 확인해주세요.",
                },
            )
