from django import forms

from interactions.models import Interaction


class RatingForm(forms.ModelForm):
    class Meta:
        model = Interaction
        fields = ['rating']
        widgets = {
            'rating': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 1,
                    'max': 5,
                    'step': 0.5
                }
            )
        }
