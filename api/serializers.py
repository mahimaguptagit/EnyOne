from rest_framework import serializers
from dashboard.models import *


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
       model=Ticket
       fields=['ticket_type','ticket_title','ticket_description','priority_level','ticket_file']
    
    
# https://www.wattpad.com/1388183111-meri-rooh%E2%99%A1-5-pampering/page/2    