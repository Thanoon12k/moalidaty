from django.db import IntegrityError
from rest_framework import generics
from .models import Subscriber, Worker, Budget, Receipt
from .serializers import SubscriberSerializer, WorkerSerializer, BudgetSerializer, ReceiptSerializer
from rest_framework.views import exception_handler
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
# Subscriber CRUD
class SubscriberListCreateView(generics.ListCreateAPIView):
    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer

class SubscriberRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer

# Worker CRUD
class WorkerListCreateView(generics.ListCreateAPIView):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer

class WorkerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer

# Budget CRUD
class BudgetListCreateView(generics.ListCreateAPIView):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer

class BudgetRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer

# Receipt CRUD
class ReceiptListCreateView(generics.ListCreateAPIView):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer
    def perform_create(self, serializer):
        try:
            serializer.save()
        except IntegrityError:
            raise ValidationError({
                "detail": "Receipt for this subscriber and month already exists."
            })
            

class ReceiptRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer