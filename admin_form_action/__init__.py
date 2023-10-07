from functools import wraps
from typing import Callable, Final, Type

from django import forms
from django.contrib.admin import ModelAdmin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

_ACTION_SUBMIT_PARAMETER: Final = 'perform'


class _InputFormMixin(forms.Form):
    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset')
        super(_InputFormMixin, self).__init__(*args, **kwargs)
        self.fields[ACTION_CHECKBOX_NAME] = (
            forms.CharField(widget=forms.MultipleHiddenInput)
        )


ActionMethod = Callable[[ModelAdmin, HttpRequest, QuerySet], HttpResponse]


def form_action(form_class: Type[forms.Form]) -> Callable[[ActionMethod], ActionMethod]:

    class _InputForm(_InputFormMixin, form_class):
        pass

    def _decorator(action_method: ActionMethod) -> ActionMethod:
        @wraps(action_method)
        def _wrapper(
            model_admin: ModelAdmin,
            request: HttpRequest,
            queryset: QuerySet,
        ) -> HttpResponse:
            if _ACTION_SUBMIT_PARAMETER in request.POST:
                form = _InputForm(request.POST, queryset=queryset)
                if form.is_valid():
                    request.form = form
                    return action_method(model_admin, request, queryset)
            else:
                form = _InputForm(
                    initial={
                        ACTION_CHECKBOX_NAME: (
                            request.POST.getlist(ACTION_CHECKBOX_NAME)
                        ),
                    },
                    queryset=queryset,
                )
            return render(
                request=request,
                template_name='admin_form_action/input_form.html',
                context={
                    'items': queryset,
                    'form': form,
                    'action': action_method.__name__,
                    'action_submit_parameter': _ACTION_SUBMIT_PARAMETER,
                }
            )
        return _wrapper
    return _decorator
