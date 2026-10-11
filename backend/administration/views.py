from rest_framework import filters, generics
from rest_framework.response import Response

from accounts.models import User
from careers.models import (
    Career,
    LearningResource,
    LearningResourceReport,
)
from profiles.models import Skill

from .analytics import get_admin_analytics
from .audit import create_audit_record
from .models import AuditRecord
from .permissions import IsAdminUser
from .serializers import (
    AdminAuditRecordSerializer,
    AdminCareerSerializer,
    AdminLearningResourceReportSerializer,
    AdminLearningResourceSerializer,
    AdminSkillSerializer,
    AdminUserRoleSerializer,
    AdminUserSerializer,
    AdminUserStatusSerializer,
)


class AuditedMutationMixin:
    audit_create_action = None
    audit_update_action = None
    audit_delete_action = None

    def perform_create(self, serializer):
        instance = serializer.save()

        if self.audit_create_action:
            create_audit_record(
                actor=self.request.user,
                action=self.audit_create_action,
                target=instance,
                metadata={},
            )

    def perform_update(self, serializer):
        changed_fields = sorted(
            serializer.validated_data.keys()
        )
        instance = serializer.save()

        if (
            self.audit_update_action
            and changed_fields
        ):
            create_audit_record(
                actor=self.request.user,
                action=self.audit_update_action,
                target=instance,
                metadata={
                    "changed_fields": changed_fields,
                },
            )

    def perform_destroy(self, instance):
        if self.audit_delete_action:
            create_audit_record(
                actor=self.request.user,
                action=self.audit_delete_action,
                target=instance,
                metadata={},
            )

        instance.delete()


class AdminUserListView(generics.ListAPIView):
    """
    List GradNavi users for administrative management.
    """

    queryset = User.objects.all().order_by("id")
    serializer_class = AdminUserSerializer
    permission_classes = (IsAdminUser,)


class AdminUserDetailView(
    AuditedMutationMixin,
    generics.RetrieveUpdateAPIView
):
    """
    Retrieve or update one GradNavi user.
    """

    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = (IsAdminUser,)
    audit_update_action = "admin.user.updated"


class AdminUserRoleUpdateView(
    generics.UpdateAPIView
):
    """
    Dedicated audited user-role management endpoint.
    """

    http_method_names = (
        "patch",
        "head",
        "options",
    )
    queryset = User.objects.all()
    serializer_class = AdminUserRoleSerializer
    permission_classes = (IsAdminUser,)

    def perform_update(self, serializer):
        user = self.get_object()
        previous_role = user.role
        instance = serializer.save()

        if previous_role != instance.role:
            create_audit_record(
                actor=self.request.user,
                action="admin.user.role_changed",
                target=instance,
                metadata={
                    "previous_role": previous_role,
                    "new_role": instance.role,
                },
            )


class AdminUserStatusUpdateView(
    generics.UpdateAPIView
):
    """
    Dedicated audited user active-status management endpoint.
    """

    http_method_names = (
        "patch",
        "head",
        "options",
    )
    queryset = User.objects.all()
    serializer_class = AdminUserStatusSerializer
    permission_classes = (IsAdminUser,)

    def perform_update(self, serializer):
        user = self.get_object()
        previous_status = user.is_active
        instance = serializer.save()

        if previous_status != instance.is_active:
            create_audit_record(
                actor=self.request.user,
                action="admin.user.status_changed",
                target=instance,
                metadata={
                    "previous_is_active": previous_status,
                    "new_is_active": instance.is_active,
                },
            )


class AdminCareerListCreateView(
    AuditedMutationMixin,
    generics.ListCreateAPIView
):
    """
    List or create GradNavi Career reference records.
    """

    queryset = Career.objects.all().order_by("id")
    serializer_class = AdminCareerSerializer
    permission_classes = (IsAdminUser,)
    audit_create_action = "admin.career.created"


class AdminCareerDetailView(
    AuditedMutationMixin,
    generics.RetrieveUpdateDestroyAPIView
):
    """
    Retrieve, update, or delete one Career.
    """

    queryset = Career.objects.all()
    serializer_class = AdminCareerSerializer
    permission_classes = (IsAdminUser,)
    audit_update_action = "admin.career.updated"
    audit_delete_action = "admin.career.deleted"


class AdminSkillListCreateView(
    AuditedMutationMixin,
    generics.ListCreateAPIView
):
    """
    List or create canonical GradNavi Skill records.
    """

    queryset = Skill.objects.all().order_by("id")
    serializer_class = AdminSkillSerializer
    permission_classes = (IsAdminUser,)
    audit_create_action = "admin.skill.created"


class AdminSkillDetailView(
    AuditedMutationMixin,
    generics.RetrieveUpdateDestroyAPIView
):
    """
    Retrieve, update, or delete one canonical Skill.
    """

    queryset = Skill.objects.all()
    serializer_class = AdminSkillSerializer
    permission_classes = (IsAdminUser,)
    audit_update_action = "admin.skill.updated"
    audit_delete_action = "admin.skill.deleted"


class AdminLearningResourceListCreateView(
    AuditedMutationMixin,
    generics.ListCreateAPIView
):
    """
    List or create controlled learning resources.
    """

    queryset = LearningResource.objects.all().order_by("id")
    serializer_class = AdminLearningResourceSerializer
    permission_classes = (IsAdminUser,)
    audit_create_action = "admin.learning_resource.created"


class AdminLearningResourceDetailView(
    AuditedMutationMixin,
    generics.RetrieveUpdateDestroyAPIView
):
    """
    Retrieve, update, or delete one learning resource.
    """

    queryset = LearningResource.objects.all()
    serializer_class = AdminLearningResourceSerializer
    permission_classes = (IsAdminUser,)
    audit_update_action = "admin.learning_resource.updated"
    audit_delete_action = "admin.learning_resource.deleted"


class AdminLearningResourceReportListView(
    generics.ListAPIView
):
    """
    List student-submitted learning resource reports for review.
    """

    queryset = (
        LearningResourceReport
        .objects
        .all()
        .order_by("-created_at", "-id")
    )
    serializer_class = AdminLearningResourceReportSerializer
    permission_classes = (IsAdminUser,)


class AdminLearningResourceReportDetailView(
    generics.RetrieveUpdateAPIView
):
    """
    Retrieve or update the review status of one report.
    """

    http_method_names = (
        "get",
        "patch",
        "head",
        "options",
    )
    queryset = LearningResourceReport.objects.all()
    serializer_class = AdminLearningResourceReportSerializer
    permission_classes = (IsAdminUser,)

    def perform_update(self, serializer):
        report = self.get_object()
        previous_status = report.status
        instance = serializer.save()

        if previous_status != instance.status:
            create_audit_record(
                actor=self.request.user,
                action=(
                    "admin.learning_resource_report."
                    "status_changed"
                ),
                target=instance,
                metadata={
                    "previous_status": previous_status,
                    "new_status": instance.status,
                },
            )


class AdminAuditRecordListView(generics.ListAPIView):
    """
    List administrative audit records.
    """

    queryset = AuditRecord.objects.all()
    serializer_class = AdminAuditRecordSerializer
    permission_classes = (IsAdminUser,)
    filter_backends = (filters.SearchFilter,)
    search_fields = (
        "action",
        "actor__email",
        "actor__first_name",
        "actor__last_name",
        "target_type",
        "target_id",
        "area",
    )


class AdminAuditRecordDetailView(
    generics.RetrieveAPIView
):
    """
    Retrieve one administrative audit record.
    """

    queryset = AuditRecord.objects.all()
    serializer_class = AdminAuditRecordSerializer
    permission_classes = (IsAdminUser,)


class AdminAnalyticsView(generics.GenericAPIView):
    """
    Return aggregated FR-15 administration analytics.
    """

    permission_classes = (IsAdminUser,)

    def get(self, request):
        return Response(
            get_admin_analytics()
        )
