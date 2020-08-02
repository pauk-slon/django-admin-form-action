from typing import Iterable

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdminBase
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy as _

from extended_actions import extended_action


admin.site.unregister(User)


class AddToGroupForm(forms.Form):
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all())


@admin.register(User)
class UserAdmin(UserAdminBase):
    actions = UserAdminBase.actions + ['add_to_groups']

    @extended_action(AddToGroupForm, _('Add selected users to groups'))
    def add_to_groups(self, request, queryset, form):
        groups = form.cleaned_data['groups']  # type: Iterable[Group]
        for user in queryset:  # type: User
            user.groups.add(*groups)
