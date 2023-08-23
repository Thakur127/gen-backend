from django.urls import path
from . import views

urlpatterns = [
    path("config/", views.StripeConfig.as_view(), name="stripe_config"),
    path(
        "create-checkout-session/",
        views.CreateCheckoutSession.as_view(),
        name="checkout_session",
    ),
    path("webhook/", views.WebhookView.as_view(), name="webhook"),
    path(
        "available-currencies/", views.Currency.as_view(), name="available_currencies"
    ),
    path("transactions/", views.PaymentsView.as_view(), name="user-payments"),
    path(
        "transaction/<str:transaction_id>",
        views.PaymentDetailView.as_view(),
        name="payment-detail",
    ),
]
