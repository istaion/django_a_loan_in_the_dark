from django import forms
from .models import STATE_CHOICES, BANK_CHOICES, NAICS_CHOICES
from loans.models import Loan

class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['state', 'bank', 'naics', 'rev_line_cr', 'low_doc', 'new_exist', 
                  'has_franchise', 'recession', 'urban_rural', 'create_job', 'retained_job', 
                  'no_emp', 'term', 'gr_appv']

    rev_line_cr = forms.ChoiceField(choices=[(None, 'N/A'), (0, 'Non'), (1, 'Oui')], required=False)
    low_doc = forms.ChoiceField(choices=[(None, 'N/A'), (0, 'Non'), (1, 'Oui')], required=False)
    new_exist = forms.ChoiceField(choices=[(None, 'N/A'), (0, 'Non'), (1, 'Oui')], required=False)
    has_franchise = forms.ChoiceField(choices=[(None, 'N/A'), (0, 'Non'), (1, 'Oui')], required=False)
    recession = forms.ChoiceField(choices=[(None, 'N/A'), (0, 'Non'), (1, 'Oui')], required=False)
    urban_rural = forms.ChoiceField(choices=[(None, 'N/A'), (0, 'Non'), (1, 'Oui')], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields.values():
            field.required = False
        self.fields['term'].required = True
        self.fields['gr_appv'].required = True

    def clean_rev_line_cr(self):
        rev_line_cr = self.cleaned_data.get('rev_line_cr')
        if rev_line_cr in {'1','0'}:
            return int(rev_line_cr) 
        return None 

    def clean_low_doc(self):
        low_doc = self.cleaned_data.get('low_doc')
        if low_doc in {'1','0'}:
            return int(low_doc) 
        return None

    def clean_new_exist(self):
        new_exist = self.cleaned_data.get('new_exist')
        if new_exist in {'1','0'}:
            return int(new_exist)  
        return None

    def clean_has_franchise(self):
        has_franchise = self.cleaned_data.get('has_franchise')
        if has_franchise in {'1','0'}:
            return int(has_franchise)  
        return None

    def clean_recession(self):
        recession = self.cleaned_data.get('recession')
        if recession in {'1','0'}:
            return int(recession) 
        return None

    def clean_urban_rural(self):
        urban_rural = self.cleaned_data.get('urban_rural')
        if urban_rural in {'1','0'}:
            return int(urban_rural)  
        return None
