from rest_framework import serializers
from dashboard.models import *


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
       model=Ticket
       fields=['ticket_type','ticket_title','ticket_description','priority_level','ticket_file']
    
    
    