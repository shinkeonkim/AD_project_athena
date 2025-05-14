from django import forms
from user.models import User


class RegisterForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "아이디",
            }
        ),
        label="아이디",
    )
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
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "비밀번호 확인",
            }
        ),
        label="비밀번호 확인",
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if (
            not self.cleaned_data["username"]
            or not self.cleaned_data["email"]
            or not self.cleaned_data["password"]
        ):
            raise forms.ValidationError("모든 필드를 입력해주세요.")

        if password != password_confirm:
            raise forms.ValidationError("비밀번호가 일치하지 않습니다.")

        if User.objects.filter(username=self.cleaned_data["username"]).exists():
            raise forms.ValidationError("이미 존재하는 아이디입니다.")

        if User.objects.filter(email=self.cleaned_data["email"]).exists():
            raise forms.ValidationError("이미 존재하는 이메일입니다.")

        return cleaned_data

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
        )
        return user

    def authenticate(self, username, password):
        try:
            user = User.objects.get(username=username)
            if not user.check_password(password):
                return None
        except User.DoesNotExist:
            return None

        return user
