from django.urls import path
from .auth_views import (
    AccountRegisterView, AccountLoginView,
    WorkerLoginView, TokenRefreshView,
)
from .views import (
    AccountProfileView,
    SubscriberListCreateView, SubscriberDetailView,
    BudgetListCreateView, BudgetDetailView,
    ReceiptListCreateView, ReceiptDetailView, ReceiptRegenerateImageView,
    WorkerListCreateView, WorkerDetailView,
)

urlpatterns = [
    # ── Auth ─────────────────────────────────────────────────────────────────
    path('auth/register/',        AccountRegisterView.as_view(),  name='account-register'),
    path('auth/account/login/',   AccountLoginView.as_view(),     name='account-login'),
    path('auth/worker/login/',    WorkerLoginView.as_view(),      name='worker-login'),
    path('auth/token/refresh/',   TokenRefreshView.as_view(),     name='token-refresh'),

    # ── Account profile ───────────────────────────────────────────────────────
    path('account/profile/',      AccountProfileView.as_view(),   name='account-profile'),

    # ── Subscribers ───────────────────────────────────────────────────────────
    path('subscribers/',          SubscriberListCreateView.as_view(),   name='subscriber-list'),
    path('subscribers/<int:pk>/', SubscriberDetailView.as_view(),       name='subscriber-detail'),

    # ── Budgets ───────────────────────────────────────────────────────────────
    path('budgets/',              BudgetListCreateView.as_view(),        name='budget-list'),
    path('budgets/<int:pk>/',     BudgetDetailView.as_view(),            name='budget-detail'),

    # ── Receipts ──────────────────────────────────────────────────────────────
    path('receipts/',                             ReceiptListCreateView.as_view(),         name='receipt-list'),
    path('receipts/<int:pk>/',                    ReceiptDetailView.as_view(),             name='receipt-detail'),
    path('receipts/<int:pk>/image/',              ReceiptRegenerateImageView.as_view(),    name='receipt-regen-image'),

    # ── Workers ───────────────────────────────────────────────────────────────
    path('workers/',              WorkerListCreateView.as_view(),        name='worker-list'),
    path('workers/<int:pk>/',     WorkerDetailView.as_view(),            name='worker-detail'),
]