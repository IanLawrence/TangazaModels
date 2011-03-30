
from Tangaza.models import *
from django.dispatch import Signal
from django.db.models.signals import *
from Tangaza import utility

import logging

logger = logging.getLogger(__name__)

def get_or_create_user_profile():
    profile = None
    user = User.objects.all()[0]
    try:
        profile = user.get_profile()
    except Watumiaji.DoesNotExist:
        profile = Watumiaji.objects.create(name_text=user.username, user=user) 
    return profile


create_vikundi_object = Signal(providing_args=["auth_user","user", "group_name", "org"])

def create_vikundi_object_handler(sender,  **kwargs):
    logger.debug ('Creating vikundi %s' % kwargs)
    auth_user = kwargs['auth_user']
    #group_leader = kwargs['group_leader']
    group_name =  kwargs['group_name']
    org = kwargs['org']
   
    
    slot = utility.auto_alloc_slot(get_or_create_user_profile(), auth_user.is_superuser)
    Vikundi.create(auth_user.get_profile(), group_name, slot, org = org)

create_vikundi_object.connect(create_vikundi_object_handler)

def user_left_group(sender, **kwargs):
    logger.debug("Deleting user group %s" % kwargs)
    
#    action = Actions.objects.get(action_desc = 'left group')
#    user_group = kwargs['instance']
#    hist = UserGroupHistory(user = user_group.user, group = user_group.group, action = action)
#    hist.save()

post_delete.connect(user_left_group, sender=UserGroups)

def user_joined_group(sender, **kwargs):
    if not kwargs['created']:
        return
    
    action = Actions.objects.get(action_desc = 'joined group')
    user_group = kwargs['instance']
    hist = UserGroupHistory(user = user_group.user, group = user_group.group, action = action)
    hist.save()

post_save.connect(user_joined_group, sender=UserGroups)

def group_created(sender, **kwargs):
    if not kwargs['created']:
        return
    instance = kwargs['instance']
    
    #if its a new group there'll be only one of it in group_admin table
    g = GroupAdmin.objects.filter(group = instance)
    if len(g) > 1:
        return
    
    action = Actions.objects.get (action_desc = 'created group')
    admin_group_hist = AdminGroupHistory (group = instance.group, action = action,
                                          user_src = instance.user, user_dst = instance.user)
    admin_group_hist.save()

#using GroupAdmin to send signal so as to be able to access user details
post_save.connect(group_created, sender=GroupAdmin)

from django.template.defaultfilters import slugify
def organization_created(sender, **kwargs):
    if not kwargs['created']:
        return
    instance = kwargs['instance']

post_save.connect(organization_created, sender=Organization)

def user_invited(sender, **kwargs):
    if not kwargs['created']:
        return
    inv = kwargs['instance']
    
    action = Actions.objects.get(action_desc = 'invited user')
    hist = UserGroupHistory(user = inv.invitation_from, group = inv.group, action = action)
    hist.save()

post_save.connect(user_invited, sender=Invitations)

def admin_added(sender, **kwargs):
    if not kwargs['created']:
        return
    group_admin = kwargs['instance']
    pass

post_save.connect(admin_added, sender=AdminGroupHistory)

def user_created(sender, **kwargs):
    #NOTE: 
    #Disabled creation if 'mine' group for now so signal doesnt work at the moment
    #To enable the signal connector just uncomment the signal line below
    if not kwargs['created']:
        return
    
    instance = kwargs['instance']
    user = instance.user
    
    #if its a new user there'll be only one of it in user_phones table
    #if just adding an additional number there'll be more than 1
    u = UserPhones.objects.filter(user=user)
    if len(u) > 1:
        return
    
    group = Groups (group_name = instance.phone_number, group_type = 'mine')
    group.save()
    
    user_group = UserGroups (user = user, group = group, slot = 1, is_quiet = 'no')
    user_group.save()
    
    grp_admin = GroupAdmin(user = user, group = group)
    grp_admin.save()
    
    action = Actions.objects.get (action_desc = 'created user')
    admin_group_hist = AdminGroupHistory (group = group, action = action,
                                          user_src = user, user_dst = user)

#post_save.connect(user_created, sender=UserPhones)                                                      

def group_delete_starting(sender, **kwargs):
    logger.debug("Group delete starting")

pre_delete.connect(group_delete_starting, Vikundi)
