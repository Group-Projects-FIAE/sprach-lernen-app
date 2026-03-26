from allauth.account.forms import SignupForm
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label="Name")
    last_name = forms.CharField(max_length=30, label="Surname")

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    new_password = forms.CharField(
        required=False, widget=forms.PasswordInput, label="New password"
    )
    repeat_password = forms.CharField(
        required=False, widget=forms.PasswordInput, label="Repeat the password"
    )
    mother_tongue = forms.CharField(
        required=False, disabled=True, initial="English", label="Mother tongue"
    )
    language_to_learn = forms.CharField(
        required=False, disabled=True, initial="German", label="Language to learn"
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile', 'level', 'daily_target']
        labels = {
            'first_name': 'Name',
            'last_name': 'Surname',
            'email': 'Email',
            'profile': 'Profile Picture',
            'level': 'Level',
            'daily_target': 'Words per day'
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("new_password")
        repeat_password = cleaned_data.get("repeat_password")

        if password or repeat_password:
            if password != repeat_password:
                raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("new_password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
