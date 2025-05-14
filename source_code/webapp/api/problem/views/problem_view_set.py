from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Q
from problem.models import Problem
from rest_framework import status, viewsets
from rest_framework.response import Response


class ProblemViewSet(viewsets.ViewSet):
    def list(self, request):
        search_query = request.GET.get("search", "")

        if search_query:
            search_vector = SearchVector("title", weight="A") + SearchVector(
                "boj_id", weight="B"
            )

            query = SearchQuery(search_query)

            problems = (
                Problem.objects.annotate(rank=SearchRank(search_vector, query))
                .filter(
                    Q(title__icontains=search_query)
                    | Q(description__icontains=search_query)
                    | Q(boj_id__icontains=search_query)
                )
                .order_by("-rank", "boj_id")[:10]
            )

            problems = problems.values("id", "boj_id", "title", "level", "rank")
        else:
            problems = Problem.objects.order_by("boj_id").values(
                "id", "boj_id", "title", "level"
            )[:10]

        return Response(list(problems), status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        try:
            problem = Problem.objects.get(pk=pk)
            problem_data = {
                "id": problem.id,
                "boj_id": problem.boj_id,
                "title": problem.title,
                "description": problem.description,
                "input_description": problem.input_description,
                "output_description": problem.output_description,
                "level": problem.level,
                "extra_information": problem.extra_information,
                "test_cases": [
                    {"input": test_case.input_data, "output": test_case.output_data}
                    for test_case in problem.test_cases.all()
                ],
            }
            return Response(problem_data, status=status.HTTP_200_OK)
        except Problem.DoesNotExist:
            return Response(
                {"error": "Problem not found"}, status=status.HTTP_404_NOT_FOUND
            )
