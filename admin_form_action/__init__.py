from functools import wraps
from typing import Callable, Final, Generic, Optional, Type, TypeVar, cast

from django import forms
from django.contrib.admin import ModelAdmin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

_ACTION_SUBMIT_PARAMETER: Final = 'perform'


class _FormMixin(forms.Form):
    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset')
        super(_FormMixin, self).__init__(*args, **kwargs)
        self.fields[ACTION_CHECKBOX_NAME] = (
            forms.CharField(widget=forms.MultipleHiddenInput)
        )


FormT = TypeVar('FormT', bound=forms.Form)
ModelAdminT = TypeVar('ModelAdminT', bound=ModelAdmin)


class InjectedHttpRequest(Generic[FormT], HttpRequest):
    form: FormT


ActionMethod = Callable[[ModelAdminT, HttpRequest, QuerySet], Optional[HttpResponse]]
WrappedActionMethod = Callable[
    [ModelAdminT, InjectedHttpRequest[FormT], QuerySet],
    Optional[HttpResponse],
]


class Decorator(Generic[ModelAdminT, FormT]):
    def __init__(self, form_class: Type[FormT]):
        form_class_name = '_Action%s' % form_class.__name__
        self.form_class = type(form_class_name, (_FormMixin, form_class), {})

    def __call__(
        self,
        action_method: ActionMethod[ModelAdminT],
    ) -> WrappedActionMethod[ModelAdminT, FormT]:
        @wraps(action_method)
        def _wrapper(
                model_admin: ModelAdminT,
                request: InjectedHttpRequest,
                queryset: QuerySet,
        ) -> Optional[HttpResponse]:
            if _ACTION_SUBMIT_PARAMETER in request.POST:
                form = self.form_class(request.POST, queryset=queryset)
                if form.is_valid():
                    request.form = form
                    return action_method(model_admin, request, queryset)
            else:
                form = self.form_class(
                    initial={
                        ACTION_CHECKBOX_NAME: (
                            request.POST.getlist(ACTION_CHECKBOX_NAME)
                        ),
                    },
                    queryset=queryset,
                )
            if hasattr(action_method, 'short_description'):
                description = action_method.short_description
            else:
                description = action_method.__name__.replace('_', ' ')
            return render(
                request=request,
                template_name='admin_form_action/input_form.html',
                context={
                    'items': queryset,
                    'form': form,
                    'action': action_method.__name__,
                    'action_submit_parameter': _ACTION_SUBMIT_PARAMETER,
                    'description': description,
                }
            )

        return _wrapper

    @staticmethod
    def cast_request(request: HttpRequest) -> InjectedHttpRequest[FormT]:
        return cast(InjectedHttpRequest[FormT], request)


def form_action(form_class: Type[FormT]) -> Decorator[ModelAdminT, FormT]:
    return Decorator[ModelAdminT, FormT](form_class)
