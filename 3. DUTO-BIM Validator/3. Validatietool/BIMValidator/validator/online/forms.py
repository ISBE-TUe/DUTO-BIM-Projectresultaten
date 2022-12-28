from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

TYPE_IFC_CHOICES = (
    ('IFC-SPF', 'IFC-SPF'),
#    ('ICDD', 'ICDD')
)

TYPE_ILS_CHOICES = (
    ('ILS-PDF', 'ILS-PDF'),
    ('ILS-XML', 'ILS-XML'),
#    ('ILS-JSON', 'ILS-JSON'),
#    ('ILS-SHACL', 'ILS-SHACL')
)

TYPE_ILSCHECK_CHOICES = (
    ('ILS-CHECK', 'ILS-CHECK'),
)

class NewIfcProjectForm(forms.Form):
    title = forms.CharField(label='Project name', max_length=50)
    type = forms.ChoiceField(choices=TYPE_IFC_CHOICES)
    file = forms.FileField(label='Upload File')

class NewIlsProjectForm(forms.Form):
    title = forms.CharField(label='Project name', max_length=50)
    type = forms.ChoiceField(choices=TYPE_ILS_CHOICES)
    file = forms.FileField(label='Upload File')

class NewIlsCheckProjectForm(forms.Form):
    title = forms.CharField(label='Project name', max_length=50)
    type = forms.ChoiceField(choices=TYPE_ILSCHECK_CHOICES)
    ifcfile = forms.FileField(label='Upload IFC File (SPF)')
    ilsfile = forms.FileField(label='Upload ILS File (XML)')

class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user