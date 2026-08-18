from django.contrib import admin
from finance.models import FinanceAccount, ExpenseCategory, Expense, Salary
from oguz.admin_site import admin_site


@admin.register(FinanceAccount, site=admin_site)
class FinanceAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_type', 'currency', 'balance', 'is_active')


@admin.register(ExpenseCategory, site=admin_site)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')


@admin.register(Expense, site=admin_site)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('category', 'amount', 'expense_date', 'payment_method')
    list_filter = ('category', 'payment_method', 'expense_date')
    raw_id_fields = ('approved_by',)


@admin.register(Salary, site=admin_site)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'amount', 'bonus', 'net_amount', 'month', 'year', 'status')
    list_filter = ('status', 'month', 'year')
    raw_id_fields = ('employee',)
