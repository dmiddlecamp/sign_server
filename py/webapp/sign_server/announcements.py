'''
Created on Mar 16, 2012

@author: robert
'''
from django import forms

class UpdateAnnouncementsForm(forms.Form):
    text = forms.CharField(max_length=78)
