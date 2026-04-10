from django.db import IntegrityError
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import Account, Subscriber, Budget, Receipt, Worker
from .serializers import (
    AccountSerializer, SubscriberSerializer,
    BudgetSerializer, ReceiptSerializer, WorkerSerializer,
)
from .permissions import IsGeneratorAuthenticated, IsAccountOnly
from .receipt_generator import generate_receipt_image


# ─── Mixin: injects generator_id from the JWT into all queries ───────────────

class _GeneratorScopeMixin:
    """All querysets are automatically scoped to the authenticated generator."""

    def _gid(self) -> int:
        return int(self.request.user['generator_id'])

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


# ─── Account ──────────────────────────────────────────────────────────────────

class AccountProfileView(_GeneratorScopeMixin, APIView):
    """GET / PATCH the authenticated generator's own profile."""
    permission_classes = [IsAccountOnly]

    def get(self, request):
        account = Account.objects.get(pk=self._gid())
        return Response(AccountSerializer(account).data)

    def patch(self, request):
        account = Account.objects.get(pk=self._gid())
        serializer = AccountSerializer(account, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ─── Subscribers ─────────────────────────────────────────────────────────────

class SubscriberListCreateView(_GeneratorScopeMixin, generics.ListCreateAPIView):
    serializer_class = SubscriberSerializer
    permission_classes = [IsGeneratorAuthenticated]

    def get_queryset(self):
        return Subscriber.objects.filter(
            generator_id=self._gid(), is_active=True
        )

    def perform_create(self, serializer):
        serializer.save(generator_id=self._gid())


class SubscriberDetailView(_GeneratorScopeMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SubscriberSerializer
    permission_classes = [IsGeneratorAuthenticated]

    def get_queryset(self):
        return Subscriber.objects.filter(generator_id=self._gid())

    def perform_destroy(self, instance):
        # Soft-delete: keep data for historical receipts
        instance.is_active = False
        instance.save()


# ─── Budgets ──────────────────────────────────────────────────────────────────

class BudgetListCreateView(_GeneratorScopeMixin, generics.ListCreateAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [IsAccountOnly]

    def get_queryset(self):
        return Budget.objects.filter(generator_id=self._gid())

    def perform_create(self, serializer):
        try:
            serializer.save(generator_id=self._gid())
        except IntegrityError:
            raise ValidationError({'detail': 'الميزانية لهذا الشهر والسنة موجودة مسبقاً'})


class BudgetDetailView(_GeneratorScopeMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [IsAccountOnly]

    def get_queryset(self):
        return Budget.objects.filter(generator_id=self._gid())


# ─── Receipts ────────────────────────────────────────────────────────────────

class ReceiptListCreateView(_GeneratorScopeMixin, generics.ListCreateAPIView):
    serializer_class = ReceiptSerializer
    permission_classes = [IsGeneratorAuthenticated]

    def get_queryset(self):
        qs = Receipt.objects.filter(
            generator_id=self._gid()
        ).select_related('subscriber', 'worker')

        # Optional filters: ?year=2025&month=3&subscriber=7
        for param in ('year', 'month', 'subscriber'):
            val = self.request.query_params.get(param)
            if val:
                qs = qs.filter(**{param: val})
        return qs

    def perform_create(self, serializer):
        try:
            receipt = serializer.save(generator_id=self._gid())
        except IntegrityError:
            raise ValidationError(
                {'detail': 'إيصال لهذا المشترك في هذا الشهر موجود مسبقاً'}
            )
        # Auto-generate receipt PNG image
        try:
            generate_receipt_image(receipt)
        except Exception as exc:
            # Image generation failure must not block receipt creation
            import logging
            logging.getLogger(__name__).warning(
                'Receipt image generation failed for receipt %s: %s', receipt.id, exc
            )


class ReceiptDetailView(_GeneratorScopeMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReceiptSerializer
    permission_classes = [IsGeneratorAuthenticated]

    def get_queryset(self):
        return Receipt.objects.filter(
            generator_id=self._gid()
        ).select_related('subscriber', 'worker')


class ReceiptRegenerateImageView(_GeneratorScopeMixin, APIView):
    """POST /receipts/{id}/image/ — regenerate the receipt PNG on demand."""
    permission_classes = [IsGeneratorAuthenticated]

    def post(self, request, pk):
        try:
            receipt = Receipt.objects.get(pk=pk, generator_id=self._gid())
        except Receipt.DoesNotExist:
            return Response({'detail': 'الإيصال غير موجود'}, status=status.HTTP_404_NOT_FOUND)

        generate_receipt_image(receipt)
        url = request.build_absolute_uri(receipt.receipt_image.url)
        return Response({'receipt_image_url': url})


# ─── Workers ─────────────────────────────────────────────────────────────────

class WorkerListCreateView(_GeneratorScopeMixin, generics.ListCreateAPIView):
    serializer_class = WorkerSerializer
    permission_classes = [IsAccountOnly]

    def get_queryset(self):
        return Worker.objects.filter(generator_id=self._gid(), is_active=True)

    def perform_create(self, serializer):
        serializer.save(generator_id=self._gid())


class WorkerDetailView(_GeneratorScopeMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WorkerSerializer
    permission_classes = [IsAccountOnly]

    def get_queryset(self):
        return Worker.objects.filter(generator_id=self._gid())

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
