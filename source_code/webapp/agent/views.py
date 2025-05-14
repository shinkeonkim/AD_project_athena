from django.shortcuts import redirect, render


def question(request):
    if not request.user.is_authenticated:
        return redirect("login")

    return render(request, "agent/question.html")
