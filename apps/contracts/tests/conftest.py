import pytest
from datetime import date, timedelta
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.contracts.models import Contract


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        email="admin@test.com", password="pass1234!", role=User.Role.ADMIN
    )


@pytest.fixture
def lawyer_user(db):
    return User.objects.create_user(
        email="lawyer@test.com", password="pass1234!", role=User.Role.LAWYER
    )


@pytest.fixture
def lawyer_user_2(db):
    return User.objects.create_user(
        email="lawyer2@test.com", password="pass1234!", role=User.Role.LAWYER
    )


@pytest.fixture
def client_user(db):
    return User.objects.create_user(
        email="client@test.com", password="pass1234!", role=User.Role.CLIENT
    )


# ---------------------------------------------------------------------------
# API client helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def anon_client():
    return APIClient()


def make_auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def admin_client(admin_user):
    return make_auth_client(admin_user)


@pytest.fixture
def lawyer_client(lawyer_user):
    return make_auth_client(lawyer_user)


@pytest.fixture
def lawyer_client_2(lawyer_user_2):
    return make_auth_client(lawyer_user_2)


@pytest.fixture
def client_client(client_user):
    return make_auth_client(client_user)


# ---------------------------------------------------------------------------
# Contracts
# ---------------------------------------------------------------------------

@pytest.fixture
def future_date():
    return date.today() + timedelta(days=30)


@pytest.fixture
def past_date():
    return date.today() - timedelta(days=1)


@pytest.fixture
def contract(db, lawyer_user, future_date):
    return Contract.objects.create(
        title="Service Agreement",
        description="Test contract",
        status=Contract.Status.ACTIVE,
        created_by=lawyer_user,
        deadline=future_date,
    )


@pytest.fixture
def contract_payload(future_date):
    return {
        "title": "New Contract",
        "description": "A description",
        "status": "DRAFT",
        "deadline": str(future_date),
        "parties": [],
    }
