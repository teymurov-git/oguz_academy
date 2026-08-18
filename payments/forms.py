from django import forms
from payments.models import Payment


class PaymentForm(forms.ModelForm):

    class Meta:
        model = Payment
        fields = ['student', 'groups', 'amount', 'paid_amount', 'payment_method', 'payment_date', 'description']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'groups': forms.CheckboxSelectMultiple(),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'paid_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
