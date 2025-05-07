from django import forms
from django import forms
from django.core.exceptions import ValidationError
import re
from .models import Candidat, Concours

class CandidatForm(forms.ModelForm):
    class Meta:
        model = Candidat
        exclude = ['inscription_validee', 'date_inscription']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenoms': forms.TextInput(attrs={'class': 'form-control'}),
            'niveau_etudes': forms.Select(attrs={'class': 'form-control'}),
            'etablissement_origine': forms.TextInput(attrs={'class': 'form-control'}),
            'concours': forms.Select(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
        }

 