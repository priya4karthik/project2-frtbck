from django import forms
from .models import FormSubmission
import re


class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = FormSubmission
        fields = ['full_name','email','phone','date_of_birth','address','city','occupation','bio']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }

    def clean_full_name(self):
        name = self.cleaned_data.get('full_name', '').strip()
        if len(name) < 2:
            raise forms.ValidationError('Full name must be at least 2 characters.')
        return name.title()

    def clean_email(self):
        return self.cleaned_data.get('email', '').strip().lower()

    def clean_phone(self):
        # Accept any format: +91 98765 43210, 9876543210, +1-800-555-0199, etc.
        phone = self.cleaned_data.get('phone', '').strip()
        digits = re.sub(r'[^\d]', '', phone)
        if len(digits) < 7 or len(digits) > 15:
            raise forms.ValidationError('Enter a valid phone number (7–15 digits).')
        return phone

    def clean_bio(self):
        bio = self.cleaned_data.get('bio', '').strip()
        if bio and len(bio) < 10:
            raise forms.ValidationError('Bio should be at least 10 characters if provided.')
        return bio
