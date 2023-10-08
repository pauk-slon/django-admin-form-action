from typing import Optional

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdminBase
from django.contrib.auth.models import Group, User
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext_lazy as _

from admin_form_action import form_action

admin.site.unregister(User)


class GroupsForm(forms.Form):
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all())

    def add_user(self, user: User):
        user.groups.add(*self.cleaned_data['groups'])

    def remove_user(self, user: User):
        user.groups.remove(*self.cleaned_data['groups'])


@admin.register(User)
class UserAdmin(UserAdminBase):
    list_display = '__str__', 'view_user_groups'
    actions = 'add_to_groups', 'remove_from_groups'

    @admin.display(description=_('groups'))
    def view_user_groups(self, obj: User) -> str:
        return ', '.join(str(group) for group in obj.groups.all())

    @form_action(GroupsForm)
    @admin.action(
        description=_('Add selected %(verbose_name_plural)s to certain groups'),
    )
    def add_to_groups(
        self,
        request: HttpRequest,
        queryset: QuerySet[User],
    ) -> Optional[HttpResponse]:
        request = form_action(GroupsForm).cast_request(request)
        groups_form = request.form
        for user in queryset:
            groups_form.add_user(user)
        return None

    @form_action(GroupsForm)
    @admin.action(
        description=_('Remove selected %(verbose_name_plural)s from certain groups'),
    )
    def remove_from_groups(
        self,
        request: HttpRequest,
        queryset: QuerySet[User],
    ) -> Optional[HttpResponse]:
        request = form_action(GroupsForm).cast_request(request)
        groups_form = request.form
        for user in queryset:
            groups_form.remove_user(user)
        return None
