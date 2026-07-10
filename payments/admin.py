from django.contrib import admin
from payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'group', 'amount', 'payment_method', 'payment_date')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('student__user__email', 'student__user__first_name', 'student__user__last_name', 'note')
    raw_id_fields = ('student', 'group')
    date_hierarchy = 'payment_date'
