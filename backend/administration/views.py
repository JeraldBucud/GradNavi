from rest_framework import generics

from accounts.models import User
from careers.models import Career, LearningResource
from profiles.models import Skill

from .permissions import IsAdminUser
from .serializers import (
    AdminCareerSerializer,
    AdminLearningResourceSerializer,
    AdminSkillSerializer,
    AdminUserSerializer,
)


class AdminUserListView(generics.ListAPIView):
    """
    List GradNavi users for administrative management.
    """

    queryset = User.objects.all().order_by("id")
    serializer_class = AdminUserSerializer
    permission_classes = (IsAdminUser,)


class AdminUserDetailView(
    generics.RetrieveUpdateAPIView
):
    """
    Retrieve or update one GradNavi user.
    """

    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = (IsAdminUser,)


class AdminCareerListCreateView(
    generics.ListCreateAPIView
):
    """
    List or create GradNavi Career reference records.
    """

    queryset = Career.objects.all().order_by("id")
    serializer_class = AdminCareerSerializer
    permission_classes = (IsAdminUser,)


class AdminCareerDetailView(
    generics.RetrieveUpdateDestroyAPIView
):
    """
    Retrieve, update, or delete one Career.
    """

    queryset = Career.objects.all()
    serializer_class = AdminCareerSerializer
    permission_classes = (IsAdminUser,)


class AdminSkillListCreateView(
    generics.ListCreateAPIView
):
    """
    List or create canonical GradNavi Skill records.
    """

    queryset = Skill.objects.all().order_by("id")
    serializer_class = AdminSkillSerializer
    permission_classes = (IsAdminUser,)


class AdminSkillDetailView(
    generics.RetrieveUpdateDestroyAPIView
):
    """
    Retrieve, update, or delete one canonical Skill.
    """

    queryset = Skill.objects.all()
    serializer_class = AdminSkillSerializer
    permission_classes = (IsAdminUser,)


class AdminLearningResourceListCreateView(
    generics.ListCreateAPIView
):
    """
    List or create controlled learning resources.
    """

    queryset = LearningResource.objects.all().order_by("id")
    serializer_class = AdminLearningResourceSerializer
    permission_classes = (IsAdminUser,)


class AdminLearningResourceDetailView(
    generics.RetrieveUpdateDestroyAPIView
):
    """
    Retrieve, update, or delete one learning resource.
    """

    queryset = LearningResource.objects.all()
    serializer_class = AdminLearningResourceSerializer
    permission_classes = (IsAdminUser,)