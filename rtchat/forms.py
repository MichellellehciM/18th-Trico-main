from django.forms import ModelForm
from django import forms
from .models import *

class ChatmessageCreateForm(ModelForm):
    class Meta:
        model = GroupMessage
        fields = ["body"]
        widgets = {
            "body": forms.TextInput(attrs={"placeholder": "請輸入訊息...", "class": "p-4 text-black", "maxlength": 300, "autofocus": True}),
        }



    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['body'].required = False  # 非必填