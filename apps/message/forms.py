from django import forms
from .models import Message

class CreateMessageForm(forms.ModelForm):

	class Meta:
		model = Message
		fields = ('message_text', 'image')
		widgets = {
		  'message_text': forms.Textarea(attrs={'rows':100, 'cols':100}),
		}
