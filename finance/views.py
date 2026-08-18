from rest_framework import viewsets, serializers
from finance.models import FinanceAccount, ExpenseCategory, Expense, Salary


class FinanceAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinanceAccount
        fields = '__all__'


class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = '__all__'


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'


class SalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Salary
        fields = '__all__'


class FinanceAccountViewSet(viewsets.ModelViewSet):
    queryset = FinanceAccount.objects.all()
    serializer_class = FinanceAccountSerializer


class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.select_related('category', 'approved_by').all()
    serializer_class = ExpenseSerializer


class SalaryViewSet(viewsets.ModelViewSet):
    queryset = Salary.objects.select_related('employee__user').all()
    serializer_class = SalarySerializer
