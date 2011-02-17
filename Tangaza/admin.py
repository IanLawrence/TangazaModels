#
#    Tangaza
#
#    Copyright (C) 2010 Nokia Corporation.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from Test.Tangaza.models import *
from Test.Tangaza.views import *
from Test.Tangaza.forms import *
from Test.Tangaza import utility
from django.template.defaultfilters import slugify
from django.contrib import admin
import logging

# added to create default fields for Watumiaji
from datetime import datetime

# Event driven model creation using signals
#from django.core.signals import *
#import django.dispatch
from Test.Tangaza import signals as custom_signal
from django.db.models.signals import post_save



#logger = logging.getLogger('tangaza_logger')

def filtered_user_queryset(request):
    org = request.user.organization_set.get()
    groups = Groups.objects.filter(org = org)
    
    user_groups = UserGroups.objects.filter(group__in = groups)
    users = [ug.user.user_id for ug in user_groups]
    
    qs = Users.objects.filter(user_id__in = users)
    
    return qs
    
#inline definitions
class GroupAdminInline(admin.TabularInline):
    model = GroupAdmin
    extra = 1
    max_num = 20
    formset = GroupAdminInlineFormset
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        
        if db_field.name == 'user' and not request.user.is_superuser:
            kwargs['queryset'] = filtered_user_queryset(request)
            return db_field.formfield(**kwargs)
        return super(GroupAdminInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

class UserGroupInline(admin.TabularInline):
    model = UserGroups
    form = UserGroupsForm
    formset = UserGroupsInlineFormset
    extra = 1
    max_num = 20
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        
        if db_field.name == 'user' and not request.user.is_superuser:
            kwargs['queryset'] = filtered_user_queryset(request)
            return db_field.formfield(**kwargs)
        return super(UserGroupInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

class UserPhonesInline(admin.TabularInline):
    model = UserPhones
    form = UserPhonesForm
    formset = UserPhonesInlineFormset
    max_num = 3
    extra = 1

#Groups customization
class GroupsAdmin(admin.ModelAdmin):
    list_display = ('group_name', 'group_type', 'is_active')
    list_filter = ('group_type', 'is_active')
    inlines = [GroupAdminInline, UserGroupInline]
    search_fields = ['group_name']
    form = GroupForm
    fields = ['group_name', 'group_type', 'is_active']
    
    def add_view(self, request, form_url='', extra_context=None):
        if request.user.is_superuser and not self.fields.__contains__('org'):
            self.fields.append('org')
        return super(GroupsAdmin, self).add_view(request, form_url, extra_context)
    
    def change_view(self, request, object_id, extra_context=None):
        if request.user.is_superuser and not self.fields.__contains__('org'):
            self.fields.append('org')
        return super(GroupsAdmin, self).change_view(request, object_id, extra_context)
    
    def queryset(self, request):
        qs = super(GroupsAdmin, self).queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(org = request.user.organization_set.get())
        return qs.exclude(group_type = 'mine')
    
    def save_model(self, request, obj, form, change):
        if not change:
            if request.user.is_superuser:
                logger.error('Org on form: %s' % obj.org)
            else:
                org = request.user.organization_set.get()
                obj.org = org
        obj.save()

admin.site.register(Vikundi, GroupsAdmin)

#Users customization
class UserAdmin(admin.ModelAdmin):
    inlines = [UserPhonesInline]
    form = UserForm
    search_fields = ['userphones__phone_number']
    ordering = ['userphones__phone_number']
    search_fields = ['name_text']
    ordering = ['name_text']
    fields = ['name_text', 'user_pin']
    
    def save_model(self, request, obj, form, change):
        new_watumiaji = form.save(commit=False)
        new_watumiaji.status = 'good'
        new_watumiaji.place_id = 1
        new_watumiaji.level = 'advanced'
        new_watumiaji.callback_limit = 60
        new_watumiaji.invitations_remaining = 100
        new_watumiaji.language_id = 1
        new_watumiaji.create_stamp = datetime.now()
        new_watumiaji.modify_stamp = datetime.now()
        new_watumiaji.notify_stamp = datetime.now()
        new_watumiaji.notify_period = datetime.now()
        new_watumiaji.dirty = 'on'
        new_watumiaji.notify_status = 'on'
        new_watumiaji.accepted_terms = 'no'
        new_watumiaji.dirty_time = datetime.now()
        new_watumiaji.notify_time = datetime.now()
        new_watumiaji.calling_time = datetime.now()
        new_watumiaji.save()
 
        #obj.save()
        #if adding new user then they'll be added to default
        #group for that organization
        if not change:
            if request.user.is_superuser:
                pass #catch this on the form
            else:
                slot = utility.auto_alloc_slot(obj)
                org = Organization.objects.get(org_admin = request.user)
                grp_name = slugify(org.org_name).replace('-','')
                group = Vikundi.objects.get(group_name = grp_name, org = org)
                obj.join_group(group, slot, None, False)
    
    def queryset(self, request):
        #Only returns users that belong to groups from this users organization
        #There has to be a better way of doing this
        qs = super(UserAdmin, self).queryset(request)
        if not request.user.is_superuser:
            org = request.user.organization_set.get()
            groups = Vikundi.objects.filter(org = org)
            user_groups = UserGroups.objects.filter(group__in = groups)
            users = [ug.user.user_id for ug in user_groups]
            qs = qs.filter(user_id__in = users)
        
        return qs

admin.site.register(Watumiaji, UserAdmin)

class OrganizationAdmin(admin.ModelAdmin):
    form = OrgForm
     
    
    def save_model(self, request, obj, form, change):
        org = obj.save()
        group_name = slugify(obj.org_name).replace('-','')
        custom_signal.create_vikundi_object.send(sender=obj, group_name=group_name, group_name_file='', group_type='private',is_active='yes', org=obj)


admin.site.register(Organization, OrganizationAdmin)

#Add profile as part of auth_user fields
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

AuthUserAdmin.list_display += ('member_profile',)
AuthUserAdmin.fieldsets[0][1]['fields'] += ('member_profile',)



