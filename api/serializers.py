from rest_framework import serializers
from dashboard.models import *


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
       model=Ticket
       fields=['user','ticket_type','ticket_title','ticket_description','ticket_number','priority_level','ticket_file','submission_status']
    
    
    