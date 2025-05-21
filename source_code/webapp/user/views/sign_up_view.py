from django.shortcuts import redirect, render
from django.views import View
from user.forms import SignUpForm


class SignUpView(View):
    def get(self, request):
        form = SignUpForm()
        return render(request, "user/signup.html", {"form": form})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("user:signin")
        else:
            return render(
                request,
                "user/signup.html",
                {"form": form},
            )
