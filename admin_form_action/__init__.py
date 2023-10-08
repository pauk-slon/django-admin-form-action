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
        self.fields['action'] = forms.CharField(widget=forms.HiddenInput)


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
    default_form_template: Final = 'admin_form_action/form.html'

    def __init__(self, form_class: Type[FormT], form_template: Optional[str] = None):
        form_class_name = '_Action%s' % form_class.__name__
        self.form_class = type(form_class_name, (_FormMixin, form_class), {})
        self.form_template = form_template

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
                        'action': action_method.__name__,
                    },
                    queryset=queryset,
                )
            options = model_admin.model._meta
            if hasattr(action_method, 'short_description'):
                description = action_method.short_description % {
                    'verbose_name_plural': options.verbose_name_plural,
                }
            else:
                description = action_method.__name__.replace('_', ' ')
            return render(
                request=request,
                template_name=self.form_template or self.default_form_template,
                context={
                    'items': queryset,
                    'form': form,
                    'action_submit_parameter': _ACTION_SUBMIT_PARAMETER,
                    'description': description,
                    'opts': options,
                }
            )

        return _wrapper

    @staticmethod
    def cast_request(request: HttpRequest) -> InjectedHttpRequest[FormT]:
        return cast(InjectedHttpRequest[FormT], request)


def form_action(
    form_class: Type[FormT],
    *,
    template: Optional[str] = None,
) -> Decorator[ModelAdminT, FormT]:
    return Decorator[ModelAdminT, FormT](form_class, template)
