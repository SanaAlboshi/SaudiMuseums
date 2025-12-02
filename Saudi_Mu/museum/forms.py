from django import forms
from .models import Authority, Museum


class AuthorityForm(forms.ModelForm):
    class Meta:
        model = Authority
        fields = ['type', 'name', 'description', 'location', 'image', 'map_url']

        widgets = {
            'type': forms.Select(attrs={'class': 'authority-input'}),
            'name': forms.TextInput(attrs={'class': 'authority-input'}),
            'description': forms.Textarea(attrs={'class': 'authority-text'}),
            'location': forms.TextInput(attrs={'class': 'authority-input'}),
            'map_url': forms.TextInput(attrs={'class': 'authority-input'}),
            'image': forms.FileInput(attrs={'class': 'authority-file'}),
        }


# ================= NEW ===================

class MuseumForm(forms.ModelForm):
    class Meta:
        model = Museum
        fields = [
            'name',
            'image',
            'location',
            'description',
            'open_time',
            'close_time'
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'authority-input'}),
            'location': forms.TextInput(attrs={'class': 'authority-input'}),
            'description': forms.Textarea(attrs={'class': 'authority-text'}),
            'image': forms.FileInput(attrs={'class': 'authority-file'}),

            'open_time': forms.TimeInput(
                attrs={'type': 'time', 'class': 'authority-input'}
            ),
            'close_time': forms.TimeInput(
                attrs={'type': 'time', 'class': 'authority-input'}
            ),
        }
