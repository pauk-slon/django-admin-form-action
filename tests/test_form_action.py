from http import HTTPStatus

import pytest


@pytest.mark.django_db
def test_form_action_init(admin_client):
    response = admin_client.post('/admin/auth/user/', {'action': 'add_to_groups', '_selected_action': 1})
    assert response.status_code == HTTPStatus.OK
    assert 'groups' in response.context['form'].fields


@pytest.mark.django_db
def test_form_action_invalid(admin_client):
    request_data = {
        'action': 'add_to_groups',
        '_selected_action': 1,
        'perform': '',
    }
    response = admin_client.post('/admin/auth/user/', request_data)
    assert response.status_code == HTTPStatus.OK
    assert not response.context['form'].is_valid()
    assert response.context['form'].errors['groups']
