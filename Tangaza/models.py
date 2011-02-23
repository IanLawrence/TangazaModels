
# Create your models here.

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models
from django.contrib.auth.models import User

# Event driven model creation using signals
from django.db.models.signals import post_save



# Some default values for database fields

GROUPTYPE = (
    ('mine', 'Mine'),
    ('private', 'Private'),
    ('public', 'Public'),
)

WATUMIAJI_STATUS = (
    ('good', 'Good'),
    ('bad', 'Bad'),
    ('blacklisted', 'Blacklisted'),
)

LEVELS = (
    ('basic', 'Basic'),
    ('advanced', 'Advanced'),
    ('expert', 'Expert'),
)

NOTIFY_STATUS = (
    ('off', 'Off'),
    ('on', 'On'),
)

YES_NO = (
    ('yes', 'Yes'),
    ('no', 'No'),
)

YES_NULL = (
    ('yes', 'Yes'),
)
class Actions(models.Model):
    action_desc = models.CharField(max_length=270)
    class Meta:
        db_table = u'actions'

class Languages(models.Model):
    name = models.CharField(max_length=60)

    class Meta:
        db_table = u'languages'

    def __unicode__(self):
       return self.name

class SmsLog(models.Model):
    sender = models.CharField(max_length=60)
    text = models.CharField(max_length=600, blank=True)
    class Meta:
        db_table = u'sms_log'

class Watumiaji(models.Model):
    user_pin = models.CharField(max_length=18, blank=True)
    status = models.CharField(max_length=33, choices = WATUMIAJI_STATUS, default='good')
    place_id = models.IntegerField(default=1)
    level = models.CharField(max_length=24, choices = LEVELS, default='advanced')
    callback_limit = models.IntegerField(default = 60)
    invitations_remaining = models.IntegerField(default = 100)
    language = models.ForeignKey(Languages, default=1)
    name_file = models.CharField(max_length=96, blank=True)
    name_text = models.CharField(unique=True, max_length=255, db_index=True, verbose_name=u'Nickname')
    create_stamp = models.DateTimeField(auto_now_add=True)
    modify_stamp = models.DateTimeField(blank=True)
    notify_stamp = models.DateTimeField(auto_now_add=True)
    notify_period = models.TimeField(auto_now_add=True)
    dirty = models.CharField(max_length=9, choices=YES_NO, default='no')
    notify_status = models.CharField(max_length=9, choices=NOTIFY_STATUS, default='on')
    accepted_terms = models.CharField(max_length=9, choices=YES_NO, default='no')
    dirty_time = models.DateTimeField(auto_now_add=True)
    notify_time = models.DateTimeField(auto_now_add=True)
    calling_time = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, unique=True, null=True, blank=True, verbose_name=u'Tangaza Account', 
                             help_text=u"What is their Tangaza account?")
    
    class Meta:
        db_table = u'watumiaji'
        verbose_name_plural = u'Watumiaji'
        ordering = [u'name_text']
        
    def __unicode__(self):
       return self.name_text

    def get_used_slots(self):
        user_groups = UserGroups.objects.filter(user = self)
        used_slots = [ug.slot for ug in user_groups]
        return used_slots


class Organization(models.Model):
    org_name = models.CharField(max_length=270, db_index=True, verbose_name=u'Name', help_text="The name of the Organisation")
    org_admin = models.ForeignKey(User, verbose_name=u'Administrator', help_text="Who is the administrator of this organization?")
    #tangaza_account = models.ForeignKey(Watumiaji, help_text="What is their Tangaza account?")
    toll_free_number  = models.CharField(max_length=21,help_text="What is the toll free number this organisation are using?")
    
    class Meta:
        db_table = u'organization'
        ordering = [u'org_name']
        
    def __unicode__(self):
       return self.org_name


class Vikundi(models.Model):
    group_name = models.CharField(unique=True, max_length=180,db_index=True)
    group_name_file = models.CharField(max_length=96, blank=True)
    group_type = models.CharField(max_length=7,choices=GROUPTYPE[1:], default='private')
    is_active = models.CharField(max_length=9, blank=True, choices=YES_NO, default='yes')
    is_deleted = models.CharField(unique=True, max_length=9, choices=YES_NULL, default='yes', null=True, blank=True)
    org = models.ForeignKey(Organization)
    
    class Meta:
        db_table = u'vikundi'
        verbose_name_plural = u'Vikundi'
        ordering = [u'group_name']
        unique_together = ('group_name','is_deleted')

class Countries(models.Model):
    country_code = models.IntegerField()
    country_name = models.CharField(max_length=27)

    class Meta:
        db_table = u'countries'
        ordering = [u'country_name']
        verbose_name_plural = u'Countries'
        
    @classmethod
    def phone2country(cls, phone):
        return 'kenya'


class Dlr(models.Model):
    smsc = models.CharField(max_length=120, blank=True)
    ts = models.CharField(max_length=120, blank=True)
    dest = models.CharField(max_length=120, blank=True)
    src = models.CharField(max_length=120, blank=True)
    service = models.CharField(max_length=120, blank=True)
    url = models.CharField(max_length=765, blank=True)
    mask = models.IntegerField(null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)
    boxc = models.CharField(max_length=120, blank=True)
    class Meta:
        db_table = u'dlr'

class GroupAdmin(models.Model):
    user = models.ForeignKey(Watumiaji)
    group = models.ForeignKey(Vikundi)
    
    class Meta:
        db_table = u'group_admin'
        unique_together = (('user', 'group'))

class Invitations(models.Model):
    invitation_to = models.ForeignKey(Watumiaji, related_name='invitation_to')
    invitation_from = models.ForeignKey(Watumiaji, related_name='invitation_from')
    group = models.ForeignKey(Vikundi)
    create_stamp = models.DateTimeField(auto_now_add=True)
    completed = models.CharField(max_length=9, choices=YES_NO, default='no')
    class Meta:
        db_table = u'invitations'

 
class PubMessages(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    src_user = models.ForeignKey(Watumiaji)
    channel = models.ForeignKey(Vikundi, db_column='channel')
    filename = models.CharField(unique=True, max_length=96)
    text = models.CharField(max_length=768, blank=True)
    class Meta:
        db_table = u'pub_messages'


class SmsRawmessage(models.Model):
    phone = models.CharField(max_length=360)
    timestamp = models.DateField(auto_now_add=True)
    text = models.CharField(max_length=4608)
    class Meta:
        db_table = u'sms_rawmessage'

class SubMessages(models.Model):
    message = models.ForeignKey(PubMessages)
    timestamp = models.DateTimeField(auto_now_add=True)
    dst_user = models.ForeignKey(Watumiaji)
    heard = models.CharField(max_length=9, choices=YES_NO, default='no')
    flagged = models.CharField(max_length=9, choices=YES_NO, default='no')
    channel = models.ForeignKey(Vikundi, db_column='channel')
    class Meta:
        db_table = u'sub_messages'

class TermsAndPrivacy(models.Model):
    user = models.ForeignKey(Watumiaji)
    accepted = models.CharField(max_length=24, choices=YES_NO, default='no')
    create_stamp = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = u'terms_and_privacy'

class UserGroupHistory(models.Model):
    group = models.ForeignKey(Vikundi)
    action = models.ForeignKey(Actions)
    user = models.ForeignKey(Watumiaji)
    create_stamp = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = u'user_group_history'

class UserGroups(models.Model):
    user = models.ForeignKey(Watumiaji)
    group = models.ForeignKey(Vikundi)
    is_quiet = models.CharField(max_length=9, choices=YES_NO)
    slot = models.PositiveIntegerField()
    class Meta:
        db_table = u'user_groups'
        verbose_name_plural = "Watumiaji who are members of this Vikundi"
        unique_together = (('user','slot'), ('user','group'),)

class UserPhones(models.Model):
    country = models.ForeignKey(Countries)
    phone_number = models.CharField(unique=True, max_length=60)
    user = models.ForeignKey(Watumiaji, db_index=True)
    is_primary = models.CharField(max_length=3, choices=YES_NO, default='yes')
    class Meta:
        db_table = u'user_phones'
        verbose_name = u'User Phone'
        ordering = [u'phone_number']


class AdminGroupHistory(models.Model):
    group = models.ForeignKey(Vikundi)
    action = models.ForeignKey(Actions)
    user_src = models.ForeignKey(Watumiaji,related_name='user_src')
    user_dst = models.ForeignKey(Watumiaji,related_name='user_dst')
    timestamp = models.DateTimeField()
    class Meta:
        db_table = u'admin_group_history'

class Calls(models.Model):
    user = models.ForeignKey(Watumiaji)
    timestamp = models.DateTimeField()
    seconds = models.IntegerField()
    cbstate = models.CharField(max_length=30)
    class Meta:
        db_table = u'calls'


#post_save.connect(create_vikundi_signal, sender=Organization)


