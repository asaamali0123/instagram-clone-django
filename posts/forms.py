from django import forms
from .models import Profile

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        # CHANGE 'profile_pic' to 'profileimg' below:
        fields = ['profileimg', 'bio', 'website', 'gender', 'full_name'] 
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Bio'}),
            'website': forms.TextInput(attrs={'placeholder': 'Website'}),
            'full_name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
        }