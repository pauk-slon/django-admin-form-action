from http import HTTPStatus
from typing import List

import pytest
from django.contrib.auth.models import Group, User
from model_bakery import baker


@pytest.fixture
def users(admin_user) -> List[User]:
    return baker.make(User, _quantity=5) + [admin_user]


@pytest.fixture
def groups_to_add() -> List[Group]:
    return baker.make(Group, _quantity=2)


@pytest.fixture(autouse=True)
def groups(groups_to_add: List[Group]) -> List[Group]:
    return baker.make(Group, _quantity=2) + groups_to_add


@pytest.mark.django_db
def test_form_action_init(admin_client, users: List[User]):
    request_data = {
        'action': 'add_to_groups',
        '_selected_action': [user.id for user in users],
    }
    response = admin_client.post('/admin/auth/user/', request_data)
    assert response.status_code == HTTPStatus.OK
    assert 'groups' in response.context['form'].fields
    assert response.context['items'].count() == len(users)
    assert response.context['description'] == 'Add selected users to certain groups'


@pytest.mark.django_db
def test_form_auto_description(admin_client, users: List[User]):
    request_data = {
        'action': 'remove_from_groups',
        '_selected_action': [user.id for user in users],
    }
    response = admin_client.post('/admin/auth/user/', request_data)
    assert response.status_code == HTTPStatus.OK
    assert response.context['description'] == 'remove from groups'


@pytest.mark.django_db
def test_form_action_invalid(admin_client, users):
    request_data = {
        'action': 'add_to_groups',
        '_selected_action': [user.id for user in users],
        'perform': '',
        'groups': [],
    }
    response = admin_client.post('/admin/auth/user/', request_data)
    assert response.status_code == HTTPStatus.OK
    assert not response.context['form'].is_valid()
    assert response.context['form'].errors['groups']


@pytest.mark.django_db
def test_form_action_performing(
    admin_client,
    users: List[User],
    groups_to_add: List[Group],
):
    request_data = {
        'action': 'add_to_groups',
        '_selected_action': [user.id for user in users],
        'perform': '',
        'groups': [group.id for group in groups_to_add],
    }
    response = admin_client.post('/admin/auth/user/', request_data)
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers['Location'] == '/admin/auth/user/'
    for group in Group.objects.all():
        if group in groups_to_add:
            assert set(group.user_set.all()) == set(users)
        else:
            assert not set(group.user_set.all()).intersection(set(users))
