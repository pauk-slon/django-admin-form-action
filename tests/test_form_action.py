import pytest


@pytest.mark.django_db
def test_form_action_view(admin_client):
    response = admin_client.post('/admin/auth/user/', {'action': 'add_to_groups', '_selected_action': 1})
    assert response.status_code == 200
    assert 'groups' in response.context['form'].fields
