from django.urls import path

from mainapp.views_auth import *
from .views import *

urlpatterns = [
    path('',RootView.as_view(),name='root'),
    path('accounts/',AccountListCreateView.as_view(),name='accounts-list-create'),
    path("accounts/<int:pk>", AccountRetrieveUpdateDestroyView.as_view(), name="account-details"),
    path('subscribers/', SubscriberListCreateView.as_view(), name='subscriber-list-create'),
    path('subscribers/<int:pk>/', SubscriberRetrieveUpdateDestroyView.as_view(), name='subscriber-detail'),
    path('budgets/', BudgetListCreateView.as_view(), name='budget-list-create'),
    path('budgets/<int:pk>/', BudgetRetrieveUpdateDestroyView.as_view(), name='budget-detail'),
    path('receipts/', ReceiptListCreateView.as_view(), name='receipt-list-create'),
    path('receipts/<int:pk>/', ReceiptRetrieveUpdateDestroyView.as_view(), name='receipt-detail'),
    path('workers/',WorkerListCreateView.as_view(),name='workers-list-create'),
    path("workers/<int:pk>", WorkerRetrieveUpdateDestroyView.as_view(), name="account-details"),
    
    
]
auth_urlpatterns = [
    path('account/login/', AccountLoginView.as_view(), name='account-login'),
    path('worker/login/', WokerLoginView.as_view(), name='worker-login'),
    
]
urlpatterns += auth_urlpatterns