'''
Created on Mar 16, 2012

@author: robert
'''
from django import forms

class UpdateAnnouncementsForm(forms.Form):
    text = forms.CharField(max_length=70)

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField()
    sender = forms.EmailField()
    cc_myself = forms.BooleanField(required=False)