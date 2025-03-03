from django import forms
from accounts.models import CustomUser

class_for_css = 'form-control'

class UserCreate(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ['email', 'is_staff', 'username', 'phone_number', 'last_name', 'first_name']
        widgets = {
            'email': forms.EmailInput(attrs={'class': class_for_css }),
            'username': forms.TextInput(attrs={'class': class_for_css }),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'last_name': forms.TextInput(attrs={'class': class_for_css }),
            'first_name': forms.TextInput(attrs={'class': class_for_css }),
            'phone_number': forms.TextInput(attrs={'class': class_for_css }),
        }

class UserFisrtLoginForm(forms.Form):
    new_password = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput()
    )
    confirm_new_password = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput()
    )

class UserUpdate(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ['username', 'phone_number', 'last_name', 'first_name', 'profile_picture', 'username']
        widgets = {
            'email': forms.EmailInput(attrs={'class': class_for_css }),
            'username': forms.TextInput(attrs={'class': class_for_css }),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'last_name': forms.TextInput(attrs={'class': class_for_css }),
            'first_name': forms.TextInput(attrs={'class': class_for_css }),
            'phone_number': forms.TextInput(attrs={'class': class_for_css }),
        }

