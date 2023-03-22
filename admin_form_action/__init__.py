from functools import wraps
from typing import Any, Type, Optional, Callable, Collection, Mapping

from django import forms
from django.contrib import admin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


ACTION_SUBMIT_PARAMETER = 'perform'


class _InputFormMixin(forms.Form):
    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset')
        super(_InputFormMixin, self).__init__(*args, **kwargs)
        self.fields[ACTION_CHECKBOX_NAME] = forms.CharField(widget=forms.MultipleHiddenInput)


ActionMethod = Callable[[admin.ModelAdmin, HttpRequest, models.QuerySet, Mapping[str, Any]], HttpResponse]


def form_action(
    form_class: Type[forms.Form],
    permissions: Optional[Collection[str]] = None,
    description: Optional[str] = None,
) -> Callable[[ActionMethod], ActionMethod]:

    class _InputForm(_InputFormMixin, form_class):
        pass

    def _decorator(action_method: ActionMethod) -> ActionMethod:
        @wraps(action_method)
        def _wrapper(
            model_admin: admin.ModelAdmin,
            request: HttpRequest,
            queryset: models.QuerySet,
        ) -> HttpResponse:
            if ACTION_SUBMIT_PARAMETER in request.POST:
                form = _InputForm(request.POST, queryset=queryset)
                if form.is_valid():
                    action_method(model_admin, request, queryset, form.cleaned_data)
            else:
                form = _InputForm(
                    initial={ACTION_CHECKBOX_NAME: request.POST.getlist(ACTION_CHECKBOX_NAME)},
                    queryset=queryset,
                )
            return render(
                request=request,
                template_name='admin_form_action/input_form.html',
                context={
                    'items': queryset,
                    'form': form,
                    'action': action_method.__name__,
                    'action_submit_parameter':  ACTION_SUBMIT_PARAMETER,
                }
            )
        if description:
            _wrapper.short_description = description
        if permissions:
            _wrapper.allowed_permissions = permissions
        return _wrapper

    return _decorator
