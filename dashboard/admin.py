from django.contrib import admin
from import_export import resources, fields
from dashboard.models import *
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget

# Register your models here.

class TicketDataResources(resources.ModelResource):
    user = fields.Field(
        column_name='username',
        attribute='user',
        widget=ForeignKeyWidget(User, 'username')) 
    
    assigned_request = fields.Field(
        column_name='username',
        attribute='assigned_request',
        widget=ForeignKeyWidget(User, 'username'))  
    
    class Meta:
        model=Ticket
        fields=('user','ticket_type','ticket_title','ticket_description','ticket_number','priority_level','submission_status','assigned_request','solved_date','created_at')
        export_order = fields 



