from django.contrib import admin
from payments.models import Payment, PaymentPlan, MonthlyPayment
from oguz.admin_site import admin_site


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'paid_amount', 'payment_date', 'payment_method', 'is_active')
    list_filter = ('payment_method', 'is_active', 'payment_date')
    search_fields = ('student__user__email', 'student__user__first_name', 'student__user__last_name', 'student__student_id')
    raw_id_fields = ('student', 'collected_by')
    filter_horizontal = ('groups',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Ödəniş', {'fields': ('student', 'groups', 'amount', 'paid_amount', 'payment_date')}),
        ('Əlavə', {'fields': ('payment_method', 'description', 'notes', 'collected_by', 'is_active')}),
        ('Tarixlər', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = ('student', 'total_amount', 'total_installments', 'installment_amount', 'start_date', 'is_active')
    list_filter = ('is_active', 'start_date')
    search_fields = ('student__user__email', 'student__user__first_name')
    raw_id_fields = ('student', 'group')


class MonthlyPaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'month', 'year', 'status', 'amount', 'paid_at')
    list_filter = ('status', 'year', 'month')
    search_fields = ('student__user__first_name', 'student__user__last_name')


admin_site.register(Payment, PaymentAdmin)
admin_site.register(PaymentPlan, PaymentPlanAdmin)
admin_site.register(MonthlyPayment, MonthlyPaymentAdmin)
