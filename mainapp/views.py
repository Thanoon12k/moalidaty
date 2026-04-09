from django.db import IntegrityError
from rest_framework import generics, views
from .models import *
from .serializers import *
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.urls import get_resolver
from django.contrib.auth.hashers import check_password

# Subscriber CRUD

class RootView(views.APIView):
    def get(self, request):
        resolver = get_resolver()
        urlsList = {}
        for sub in resolver.url_patterns[1].url_patterns:
            path = str(sub.pattern).lstrip('/')
            urlsList[sub.name] = request.build_absolute_uri('/' + path)
        return Response(urlsList)

class SubscriberListCreateView(generics.ListCreateAPIView):
    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer


class SubscriberRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer


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
        except AttributeError:
            raise ValidationError({
                "detail": "no existense budget found  for this date year and month !! (create budget for year month first then try again)"
            })
            
            

class ReceiptRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer



class AccountListCreateView(generics.ListCreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class AccountRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class WorkerListCreateView(generics.ListCreateAPIView):
    
    serializer_class = WorkerSerializer
    def get_queryset(self):
        print('body- ',self.request.body.decode())
        # queryset = Worker.objects.all()
        return Worker.objects.all()

class WorkerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer
