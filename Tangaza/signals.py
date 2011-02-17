from Tangaza.models import Vikundi
from django.dispatch import Signal


create_vikundi_object = Signal(providing_args=["group_name", "group_name_file", "group_type", "is_active", "org"])


def create_vikundi_object_handler(sender,  **kwargs):
    group_name =  kwargs['group_name']
    group_name_file = kwargs['group_name_file']
    group_type = kwargs['group_type']
    is_active = kwargs['is_active'] 
    org = kwargs['org'] 
    group = Vikundi(group_name=group_name, group_name_file=group_name_file, group_type=group_type, is_active=is_active, org=org)
    group.save()
    


create_vikundi_object.connect(create_vikundi_object_handler)

