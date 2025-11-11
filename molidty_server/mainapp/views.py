from django.db import IntegrityError
from rest_framework import generics,views
from .models import MyManager, Subscriber, Worker, Budget, Receipt
from .serializers import *
from rest_framework.views import exception_handler
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.urls import get_resolver
from django.contrib.auth.hashers import check_password

# Subscriber CRUD

class RootView(views.APIView):
    def get(self,request):
        resolver=get_resolver()
        urlsList={} 
        for sub in resolver.url_patterns[1].url_patterns:
            urlsList[sub.name]="http://localhost:8000/"+str(sub.pattern)
        return Response(urlsList)

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
    def perform_create(self, serializer):
        try:
            serializer.save()
        except IntegrityError:
            raise ValidationError({
                "detail": "  Budget for this year and month already exists."
            })
        

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


class ElectricManagerList(generics.ListAPIView):
    queryset = MyManager.objects.all()
    serializer_class = ManagerSerializer


class ManagerListCreateView(generics.ListCreateAPIView):
    queryset = MyManager.objects.all()
    serializer_class = ManagerSerializer

class ManagerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MyManager.objects.all()
    serializer_class = ManagerSerializer

