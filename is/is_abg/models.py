from django.db import models


# Create your models here.
class iabgInputForm(models.Model):
    document_choices = [
        ('Word', 'Word Document'),
        ('Excel', 'Excel Workbook'),
        ('Both', 'Both'), ]
    section_choices = [
        ("All", "All"),
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
    ]
    document_type = models.CharField(max_length=200,
                                     default='both', choices=document_choices)
    document_author = models.CharField(max_length=200, default='First-name Last-name')
    customer_name = models.CharField(max_length=200, default='Demo Intersight Customr')
    host = models.TextField(default='https://intersight.com', )
    private_api_key = models.TextField(default='Enter the Intersight Private Key', )
    public_api_key = models.TextField(default='Enter the Intersight Key ID')
    Select_Document_Sections = models.CharField(max_length=200, default='All',
                                                choices=section_choices)
