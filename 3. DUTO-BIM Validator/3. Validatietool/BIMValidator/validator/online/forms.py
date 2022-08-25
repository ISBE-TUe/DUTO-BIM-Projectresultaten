from django import forms

TYPE_CHOICES = (
    ('IFC-SPF', 'IFC-SPF'),
    ('ILS-PDF', 'ILS-PDF'),
    ('ILS-XML', 'ILS-XML'),
    ('ILS-JSON', 'ILS-JSON'),
    ('ILS-SHACL', 'ILS-SHACL'),
    ('ICDD', 'ICDD')
)

class NewProjectForm(forms.Form):
    title = forms.CharField(label='Project name', max_length=50)
    type = forms.ChoiceField(choices=TYPE_CHOICES)
    file = forms.FileField(label='Upload File')
    