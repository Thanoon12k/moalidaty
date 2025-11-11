from django.urls import path

from mainapp.auth import ManagerLoginView
from .views import *

urlpatterns = [
    path('',RootView.as_view(),name='root'),
    path('manager/',ManagerListCreateView.as_view(),name='manager-list-create'),
    path("manager/<int:pk>", ManagerRetrieveUpdateDestroyView.as_view(), name="manager-details"),
    path('subscribers/', SubscriberListCreateView.as_view(), name='subscriber-list-create'),
    path('subscribers/<int:pk>/', SubscriberRetrieveUpdateDestroyView.as_view(), name='subscriber-detail'),
    path('workers/', WorkerListCreateView.as_view(), name='worker-list-create'),
    path('workers/<int:pk>/', WorkerRetrieveUpdateDestroyView.as_view(), name='worker-detail'),
    path('budgets/', BudgetListCreateView.as_view(), name='budget-list-create'),
    path('budgets/<int:pk>/', BudgetRetrieveUpdateDestroyView.as_view(), name='budget-detail'),
    path('receipts/', ReceiptListCreateView.as_view(), name='receipt-list-create'),
    path('receipts/<int:pk>/', ReceiptRetrieveUpdateDestroyView.as_view(), name='receipt-detail'),
]
auth_urlpatterns = [
    path('manager/login/', ManagerLoginView.as_view(), name='manager-login'),
]
urlpatterns += auth_urlpatterns