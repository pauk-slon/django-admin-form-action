from typing import Iterable

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdminBase
from django.contrib.auth.models import User, Group

from extended_actions import extended_action


admin.site.unregister(User)


class AddToGroupForm(forms.Form):
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all())


@admin.register(User)
class UserAdmin(UserAdminBase):
    actions = UserAdminBase.actions + ['add_to_groups_method']

    @extended_action(AddToGroupForm)
    def add_to_groups_method(self, request, queryset, form):
        groups = form.cleaned_data['groups']  # type: Iterable[Group]
        for user in queryset:  # type: User
            user.groups.add(*groups)
