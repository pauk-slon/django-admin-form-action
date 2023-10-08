# django-admin-form-action

[![Test Status][test-status-image]][test-status-link]
[![codecov][codecov-image]][codecov-link]

`django-admin-form-action` is intended to implement parametrized actions on the Django admin site. 
Action parameters are passed through an intermediate form as it shown below.

![demo](https://github.com/pauk-slon/django-admin-form-action/assets/2351932/a6c67b47-0fde-4d9e-9c23-cb50e9a87e48)

The demonstrated functionality can be implemented with `django-admin-form-action` in the following way:

```python
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group, User

from admin_form_action import form_action


class GroupsForm(forms.Form):
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all())

    def add_user(self, user: User):
        user.groups.add(*self.cleaned_data['groups'])

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    actions = ['add_to_groups']

    @form_action(GroupsForm)
    @admin.action(description='Add selected users to certain groups')
    def add_to_groups(self, request, queryset):
        # Validated form is injected by `@form_action` to `request.form`
        groups_form = request.form
        for user in queryset:
            groups_form.add_user(user)
```

## Install

```shell
pip install django-admin-form-action
```

```python
INSTALLED_APPS = [
    ...
    'admin_form_action',
    ...
]
```

## Development

### Run demo app

```shell
poetry install
poetry run django-admin migrate --settings=tests.app.settings
poetry run django-admin runserver --settings=tests.app.settings
```

### Test

```shell
poetry run pytest
```

### Lint

```shell
poetry run isort .
poetry run ruff . 
poetry run mypy .
```

[codecov-image]: https://codecov.io/gh/pauk-slon/django-admin-form-action/graph/badge.svg?token=QCY3CW2ZVG
[codecov-link]: https://codecov.io/gh/pauk-slon/django-admin-form-action
[test-status-image]: https://github.com/pauk-slon/django-admin-form-action/actions/workflows/test.yaml/badge.svg
[test-status-link]: https://github.com/pauk-slon/django-admin-form-action/actions/workflows/test.yaml
