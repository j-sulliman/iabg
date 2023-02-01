from django import forms
from django.contrib.admin.widgets import AdminSplitDateTime
from django.forms import BaseFormSet, TextInput, formset_factory
from .models import iabgInputForm

RADIO_CHOICES = (
    ("1", "Physical"),
    ("2", "Firmware"),
    ("3", "Compute Summary"),
    ("4", "Rack Servers"),
    ("5", "Blade Servers"),
    ("6", "Hyperflex"),
    ("7", "Physical Ports"),
    ("8", "FC Ports"),
    ("9", "Service Profiles"),
    ("10", "Management Addressing"),
)
DOC_CHOICES = (("1", "Both"), ("1", "Word Report"), ("2", "Excel Spreadsheet"))
MEDIA_CHOICES = (
    ("Audio", (("vinyl", "Vinyl"), ("cd", "CD"))),
    ("Video", (("vhs", "VHS Tape"), ("dvd", "DVD"))),
    ("unknown", "Unknown"),
)


class iabgForm(forms.ModelForm):
    class Meta:
        model = iabgInputForm
        fields = (
            'host',
            'public_api_key',
            'private_api_key',
        )
