from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

from core.views import StaffRequiredMixin
from payments.models import Payment
from payments.forms import PaymentForm

from rest_framework import viewsets
from payments.serializers import PaymentSerializer, PaymentPlanSerializer
from payments.models import PaymentPlan


class PaymentListView(StaffRequiredMixin, ListView):
    model = Payment
    template_name = 'payment_list.html'
    context_object_name = 'payments'


class PaymentCreateView(StaffRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'payment_form.html'
    success_url = reverse_lazy('payment_list')


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related('student__user', 'group', 'collected_by').all()
    serializer_class = PaymentSerializer
    search_fields = ('student__user__email', 'student__user__first_name', 'student__user__last_name', 'receipt_number')


class PaymentPlanViewSet(viewsets.ModelViewSet):
    queryset = PaymentPlan.objects.all()
    serializer_class = PaymentPlanSerializer
