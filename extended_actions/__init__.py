__version__ = '0.1.0'

from typing import Type, Callable

from django import forms
from django.contrib import admin
from django.db import models
from django.http import HttpResponseRedirect, HttpRequest, HttpResponse
from django.shortcuts import render


default_app_config = 'extended_actions.apps.ExtendedActionsConfig'


class FormMixin(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)


def extended_action(form_class):  # type: (Type[forms.Form]) -> Callable
    class _Form(FormMixin, form_class):
        pass

    def _decorator(action_method):
        def _wrapper(self, request, queryset):
            # type: (admin.ModelAdmin, HttpRequest, models.QuerySet) -> HttpResponse
            form = None
            if 'perform' in request.POST:
                form = _Form(request.POST)
                if form.is_valid():
                    action_method(self, request, queryset, form)
                return HttpResponseRedirect(request.get_full_path())
            if not form:
                form = _Form(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
            return render(request, 'extended_actions/form.html', context={
                'items': queryset,
                'form': form,
                'action': action_method.__name__,
            })
        return _wrapper

    return _decorator
