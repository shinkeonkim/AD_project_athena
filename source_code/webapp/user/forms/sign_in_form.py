from django import forms
from user.models import User


class SignInForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-input",
                "placeholder": "이메일",
            }
        ),
        label="이메일",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "비밀번호",
            }
        ),
        label="비밀번호",
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if not email or not password:
            raise forms.ValidationError("이메일과 비밀번호를 모두 입력해주세요.")

        try:
            user = User.objects.get(email=email)
            if not user.check_password(password):
                raise forms.ValidationError("이메일 또는 비밀번호가 올바르지 않습니다.")
            cleaned_data["user"] = user
        except User.DoesNotExist:
            raise forms.ValidationError("이메일 또는 비밀번호가 올바르지 않습니다.")

        return cleaned_data

    def authenticate(self, email, password):
        try:
            user = User.objects.get(email=email)
            if not user.check_password(password):
                return None
        except User.DoesNotExist:
            return None

        return user
