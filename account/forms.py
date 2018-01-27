from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import MinimumLengthValidator, CommonPasswordValidator

User = get_user_model()


class UserRegistrationForm(forms.ModelForm):
    #making account type radio button from dropdown list
    account_type = forms.ChoiceField(
        widget=forms.RadioSelect, 
        choices=[('jobseeker', 'Job Seeker'), ('recruiter', 'Recruiter')]
    )
    #including new confirm_password field
    confirm_password = forms.CharField(
        widget=forms.PasswordInput
    )

    class Meta():
        model = User
        fields = (
            'account_type',
            'username',
            'email',
            'password',
            'confirm_password',
        )
        widgets = {
            'password':forms.PasswordInput
        }

    #check that the password in both fields match
    def clean_confirm_password(self, *args, **kwargs):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "Password does not match."
            )

        return password

    #check if email is already registered
    def clean_email(self, *args, **kwargs):
        email = self.cleaned_data.get("email")

        user = User.objects.filter(email=email)
        if user.exists():
            raise forms.ValidationError("This email is already registered.")

        return email



class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self, *args, **kwargs):
        """
        checking if user with associated username already
        exists.
        """
        username = self.cleaned_data.get('username')

        user = User.objects.filter(username=username)
        if not user.exists():
            raise forms.ValidationError("This user does not exist.")

        return username

    #checking if valid login credentials is provided
    def clean(self, *args, **kwargs):
        """
        to check if given username and password is valid
        credentials of a user.
        """
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        user = authenticate(username=username, password=password)

        if not user:
            raise forms.ValidationError("Invalid login credentials provided.")

        if not user.is_active:
            raise forms.ValidationError("This account is deactivated. Please contact admin to activate it.")

        return self.cleaned_data