from django import forms
from payments.models import Payment


class PaymentForm(forms.ModelForm):

    class Meta:
        model = Payment
        fields = ['student', 'group', 'amount', 'payment_method', 'note']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'group': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
