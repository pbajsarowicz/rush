from django import forms

from .models import User


class RegistrationForm(forms.ModelForm):
	
   
    email = forms.EmailField(widget=forms.TextInput,label="Email")
    first_name = forms.CharField(widget=forms.TextInput,label="Imie")
    last_name = forms.CharField(widget=forms.TextInput,label="Nazwisko")
    organization_name = forms.CharField(widget=forms.TextInput,
    									label="Nazwa organizacji")
    organization_address = forms.CharField(widget=forms.TextInput,
											label="Adres organizacji")
    

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'organization_name',
        		 'organization_address']


    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        if commit:
            user.save()
        return user
