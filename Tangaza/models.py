from django.db import models

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

ISPRIMARY= (
    ('yes', 'Yes'),
    ('no', 'No'),
)

GROUPTYPE= (
    ('mine', 'Mine'),
    ('private', 'Private'),
    ('public', 'Public'),
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
    user_pin = models.CharField(max_length=18, blank=True, null=True)
    status = models.CharField(max_length=33)
    place_id = models.IntegerField()
    level = models.CharField(max_length=24)
    callback_limit = models.IntegerField()
    invitations_remaining = models.IntegerField()
    language = models.ForeignKey(Languages)
    name_file = models.CharField(max_length=96, blank=True)
    name_text = models.CharField(unique=True, max_length=255, verbose_name=u'Nickname')
    create_stamp = models.DateTimeField()
    modify_stamp = models.DateTimeField()
    notify_stamp = models.DateTimeField()
    notify_period = models.DateTimeField() # This field type is a guess.
    dirty = models.CharField(max_length=9)
    notify_status = models.CharField(max_length=9)
    accepted_terms = models.CharField(max_length=9)
    dirty_time = models.DateTimeField()
    notify_time = models.DateTimeField()
    calling_time = models.DateTimeField()

    class Meta:
        db_table = u'watumiaji'

    def __unicode__(self):
       return self.name_text

    def get_used_slots(self):
        user_groups = UserGroups.objects.filter(user = self)
        used_slots = [ug.slot for ug in user_groups]
        return used_slots


class Organization(models.Model):
    org_name = models.CharField(max_length=270, help_text="The name of the Organisation")
    org_admin = models.ForeignKey(User, help_text="Who is the administrator of this organization?")
    tangaza_account = models.ForeignKey(Watumiaji, help_text="What is their Tangaza account?")
    toll_free_number  = models.CharField(max_length=21,help_text="What is the toll free number this organisation are using?")

    class Meta:
        db_table = u'organization'

    def __unicode__(self):
       return self.org_name



class Vikundi(models.Model):
    group_name = models.CharField(unique=True, max_length=180)
    group_name_file = models.CharField(max_length=96, blank=True)
    group_type = models.CharField(max_length=7,choices=GROUPTYPE)
    is_active = models.CharField(unique=True, max_length=9, blank=True)
    org = models.ForeignKey(Organization)
    class Meta:
        db_table = u'vikundi'

class Countries(models.Model):
    country_code = models.IntegerField()
    country_name = models.CharField(max_length=27)

    class Meta:
        db_table = u'countries'

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


class Invitations(models.Model):
    invitation_to = models.ForeignKey(Watumiaji,related_name='+')
    invitation_from = models.ForeignKey(Watumiaji)
    group = models.ForeignKey(Vikundi)
    create_stamp = models.DateTimeField()
    completed = models.CharField(max_length=9)
    class Meta:
        db_table = u'invitations'

 
class PubMessages(models.Model):
    timestamp = models.DateTimeField()
    src_user = models.ForeignKey(Watumiaji)
    channel = models.ForeignKey(Vikundi, db_column='channel')
    filename = models.CharField(unique=True, max_length=96)
    text = models.CharField(max_length=768, blank=True)
    class Meta:
        db_table = u'pub_messages'


class SmsRawmessage(models.Model):
    phone = models.CharField(max_length=360)
    timestamp = models.DateField()
    text = models.CharField(max_length=4608)
    class Meta:
        db_table = u'sms_rawmessage'

class SubMessages(models.Model):
    message = models.ForeignKey(PubMessages)
    timestamp = models.DateTimeField()
    dst_user = models.ForeignKey(Watumiaji)
    heard = models.CharField(max_length=9)
    flagged = models.CharField(max_length=9)
    channel = models.ForeignKey(Vikundi, db_column='channel')
    class Meta:
        db_table = u'sub_messages'

class TermsAndPrivacy(models.Model):
    user = models.ForeignKey(Watumiaji)
    status = models.CharField(max_length=24)
    create_stamp = models.DateTimeField()
    class Meta:
        db_table = u'terms_and_privacy'

class UserGroupHistory(models.Model):
    group = models.ForeignKey(Vikundi)
    action = models.ForeignKey(Actions)
    user = models.ForeignKey(Watumiaji)
    create_stamp = models.DateTimeField()
    class Meta:
        db_table = u'user_group_history'

class UserGroups(models.Model):
    user = models.ForeignKey(Watumiaji)
    group = models.ForeignKey(Vikundi)
    is_quiet = models.CharField(max_length=9, choices=ISPRIMARY)
    slot = models.IntegerField()
    class Meta:
        db_table = u'user_groups'
        verbose_name_plural = "Watumiaji's who are members of this Vikundi"


class UserPhones(models.Model):
    country = models.ForeignKey(Countries)
    phone_number = models.CharField(unique=True, max_length=60)
    user = models.ForeignKey(Watumiaji)
    is_primary = models.CharField(max_length=3, choices=ISPRIMARY)
    class Meta:
        db_table = u'user_phones'


class AdminGroupHistory(models.Model):
    group = models.ForeignKey(Vikundi)
    action = models.ForeignKey(Actions)
    user_src = models.ForeignKey(Watumiaji)
    user_dst = models.ForeignKey(Watumiaji,related_name='+')
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


