from django.db.models import Q

from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from careers.models import Career

from .models import (
    Interest,
    Skill,
    StudentProfile,
)
from .serializers import (
    CareerReferenceSerializer,
    InterestReferenceSerializer,
    SkillReferenceSerializer,
    StudentProfileSerializer,
    StudentProfileUpdateSerializer,
)


class ReferenceSearchView(APIView):
    """
    Authenticated read-only search over approved GradNavi
    reference records used by Student Profile selectors.
    """

    permission_classes = (
        IsAuthenticated,
    )

    result_limit = 25

    serializer_class = None

    def get_queryset(self):
        raise NotImplementedError

    def apply_search(
        self,
        queryset,
        search,
    ):
        return queryset

    def get(
        self,
        request,
    ):
        search = (
            request.query_params
            .get(
                "search",
                "",
            )
            .strip()
        )

        queryset = (
            self.get_queryset()
        )

        if search:
            queryset = (
                self.apply_search(
                    queryset,
                    search,
                )
            )

        total = (
            queryset.count()
        )

        results = list(
            queryset[
                :self.result_limit
            ]
        )

        serializer = (
            self.serializer_class(
                results,
                many=True,
            )
        )

        return Response(
            {
                "data": {
                    "results": (
                        serializer.data
                    ),
                    "total": total,
                    "search": search,
                }
            }
        )


class SkillReferenceView(
    ReferenceSearchView
):
    serializer_class = (
        SkillReferenceSerializer
    )

    result_limit = 25

    def get_queryset(self):
        return (
            Skill.objects
            .all()
            .order_by(
                "name",
                "id",
            )
        )

    def apply_search(
        self,
        queryset,
        search,
    ):
        return queryset.filter(
            Q(
                name__icontains=search
            )
            | Q(
                category__icontains=search
            )
            | Q(
                concept_type__icontains=search
            )
        )


class InterestReferenceView(
    ReferenceSearchView
):
    serializer_class = (
        InterestReferenceSerializer
    )

    result_limit = 25

    def get_queryset(self):
        return (
            Interest.objects
            .all()
            .order_by(
                "name",
                "id",
            )
        )

    def apply_search(
        self,
        queryset,
        search,
    ):
        return queryset.filter(
            Q(
                name__icontains=search
            )
            | Q(
                category__icontains=search
            )
        )


class CareerReferenceView(
    ReferenceSearchView
):
    serializer_class = (
        CareerReferenceSerializer
    )

    result_limit = 50

    def get_queryset(self):
        return (
            Career.objects
            .filter(
                active=True
            )
            .order_by(
                "name",
                "id",
            )
        )

    def apply_search(
        self,
        queryset,
        search,
    ):
        return queryset.filter(
            Q(
                name__icontains=search
            )
            | Q(
                category__icontains=search
            )
            | Q(
                description__icontains=search
            )
        )


class StudentProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        profile = self._get_profile(request.user)
        return Response({"data": {"profile": StudentProfileSerializer(profile).data}})

    def patch(self, request):
        profile = self._get_profile(request.user)
        serializer = StudentProfileUpdateSerializer(
            data=request.data,
            context={"profile": profile},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        profile = self._get_profile(request.user)
        return Response({"data": {"profile": StudentProfileSerializer(profile).data}})

    def _get_profile(self, user):
        try:
            return (
                StudentProfile.objects.prefetch_related(
                    "student_skills__skill",
                    "student_interests__interest",
                    "education",
                    "experience",
                    "projects",
                    "career_goals",
                    "personality_responses",
                )
                .order_by("id")
                .get(user=user)
            )
        except StudentProfile.DoesNotExist:
            raise NotFound("Student profile was not found.")
