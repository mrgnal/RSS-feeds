import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from rss_channels.models import RssChannel

@pytest.mark.django_db
def test_admin_user_has_access_to_admin_api():
    client = APIClient()
    admin_user = type('User', (), {
        'is_authenticated': True,
        'is_superuser': True,
    })()
    client.force_authenticate(user=admin_user)

    url = reverse('admin-channel-list')
    response = client.get(url)

    assert response.status_code != 403


@pytest.mark.django_db
def test_non_admin_user_has_no_access_to_admin_api():
    client = APIClient()
    regular_user = type('User', (), {
        'is_authenticated': True,
        'is_superuser': False,
    })()
    client.force_authenticate(user=regular_user)

    url = reverse('admin-channel-list')
    response = client.get(url)

    assert response.status_code == 403
