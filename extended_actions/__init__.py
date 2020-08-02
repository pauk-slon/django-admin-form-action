__version__ = '0.1.0'

from typing import Type, Callable

from django import forms
from django.contrib import admin
from django.db import models
from django.http import HttpResponseRedirect, HttpRequest, HttpResponse
from django.shortcuts import render


default_app_config = 'extended_actions.apps.ExtendedActionsConfig'


class FormMixin(forms.Form):
    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset')
        super(FormMixin, self).__init__(*args, **kwargs)
        self.fields[admin.ACTION_CHECKBOX_NAME] = forms.CharField(widget=forms.MultipleHiddenInput)


def extended_action(form_class):  # type: (Type[forms.Form]) -> Callable
    class _Form(FormMixin, form_class):
        pass

    def _decorator(action_method):
        def _wrapper(model_admin, request, queryset):
            # type: (admin.ModelAdmin, HttpRequest, models.QuerySet) -> HttpResponse
            form = None
            action_submit_parameter = 'perform'
            if action_submit_parameter in request.POST:
                form = _Form(request.POST, queryset=queryset)
                if form.is_valid():
                    action_method(model_admin, request, queryset, form)
                return HttpResponseRedirect(request.get_full_path())
            if not form:
                form = _Form(
                    initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)},
                    queryset = queryset
                )
            return render(request, 'extended_actions/form.html', context={
                'items': queryset,
                'form': form,
                'action': action_method.__name__,
                'action_submit_parameter':  action_submit_parameter,
            })
        return _wrapper

    return _decorator
