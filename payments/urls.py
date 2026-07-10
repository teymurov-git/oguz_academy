from django.urls import path
from payments.views import PaymentListView, PaymentCreateView

urlpatterns = [
    path('', PaymentListView.as_view(), name='payment_list'),
    path('add/', PaymentCreateView.as_view(), name='payment_add'),
]
