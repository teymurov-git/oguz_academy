from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

from core.views import StaffRequiredMixin
from payments.models import Payment
from payments.forms import PaymentForm


class PaymentListView(StaffRequiredMixin, ListView):
    model = Payment
    template_name = 'payment_list.html'
    context_object_name = 'payments'


class PaymentCreateView(StaffRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'payment_form.html'
    success_url = reverse_lazy('payment_list')
