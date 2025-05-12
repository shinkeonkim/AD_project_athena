from django.shortcuts import render


def question(request):
    return render(request, "agent/question.html")
