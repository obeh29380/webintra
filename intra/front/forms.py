from django.contrib.auth.forms import AuthenticationForm,UserCreationForm,forms
from django.contrib.auth.models import User
from django import forms
from .models import WorkStatus
from django.core.exceptions import ValidationError

class LoginForm(AuthenticationForm):
    """ログインフォーム"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
            

class SignUpForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username','last_name','first_name','email', 'password1', 'password2')
        
        
#class workStatusForm(forms.Form):
#    answers = forms.fields.ChoiceField(
#        choices = (
#            (1, 1),
#            (11, 11),
#            (999, 'ALL')
#        ),
#        initial=10,
#        required=True,
#        widget=forms.widgets.Select()
#    )


class WorkStatusForm(forms.ModelForm):
    
    class Meta:
        model = WorkStatus
        # fields = ('status', 'name','name_selection','use')
        fields = '__all__'
        labels = {
            'status': '勤怠区分コード',
            'name': '勤怠区分名',
            'name_selection': '勤怠区分(プルダウン表示)',
            'use': '使用可否',
        }
        help_texts = {
            'status': '２桁の整数',
            'name': '１０文字以内',
            'name_selection': '２文字',
        }
        
        def check_name_selection(value):
            if len(value)>3:
                raise ValidationError('プルダウン表示は３文字以内で入力してください。')
