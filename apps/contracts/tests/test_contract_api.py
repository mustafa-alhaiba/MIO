import pytest
from datetime import date, timedelta
from django.urls import reverse

from apps.contracts.models import Contract

LIST_URL    = reverse("contract-list")
DETAIL_URL  = lambda pk: reverse("contract-detail", args=[pk])
UPLOAD_URL  = lambda pk: reverse("contract-upload", args=[pk])


# =============================================================================
# List  GET /api/contracts/
# =============================================================================

@pytest.mark.django_db
class TestContractList:

    def test_unauthenticated_returns_401(self, anon_client):
        res = anon_client.get(LIST_URL)
        assert res.status_code == 401

    def test_admin_sees_all_contracts(self, admin_client, contract, lawyer_user_2):
        Contract.objects.create(
            title="Other Contract", created_by=lawyer_user_2,
            deadline=date.today() + timedelta(days=10), status=Contract.Status.DRAFT,
        )
        res = admin_client.get(LIST_URL)
        assert res.status_code == 200
        assert res.data["count"] == 2

    def test_lawyer_sees_only_own_contracts(self, lawyer_client, lawyer_client_2, lawyer_user, lawyer_user_2, future_date):
        Contract.objects.create(
            title="Mine", created_by=lawyer_user, deadline=future_date, status=Contract.Status.DRAFT
        )
        Contract.objects.create(
            title="Others", created_by=lawyer_user_2, deadline=future_date, status=Contract.Status.DRAFT
        )
        res = lawyer_client.get(LIST_URL)
        assert res.status_code == 200
        assert res.data["count"] == 1
        assert res.data["results"][0]["title"] == "Mine"

    def test_client_sees_only_party_contracts(self, client_client, client_user, lawyer_user, future_date):
        visible = Contract.objects.create(
            title="Party Contract", created_by=lawyer_user,
            deadline=future_date, status=Contract.Status.ACTIVE,
        )
        visible.parties.add(client_user)
        Contract.objects.create(
            title="Hidden Contract", created_by=lawyer_user,
            deadline=future_date, status=Contract.Status.ACTIVE,
        )
        res = client_client.get(LIST_URL)
        assert res.status_code == 200
        assert res.data["count"] == 1
        assert res.data["results"][0]["title"] == "Party Contract"

    def test_filter_by_status(self, lawyer_client, lawyer_user, future_date):
        Contract.objects.create(
            title="Draft One", created_by=lawyer_user,
            deadline=future_date, status=Contract.Status.DRAFT,
        )
        Contract.objects.create(
            title="Active One", created_by=lawyer_user,
            deadline=future_date, status=Contract.Status.ACTIVE,
        )
        res = lawyer_client.get(LIST_URL, {"status": "DRAFT"})
        assert res.status_code == 200
        assert res.data["count"] == 1
        assert res.data["results"][0]["status"] == "DRAFT"

    def test_filter_by_deadline_before(self, lawyer_client, lawyer_user):
        soon = date.today() + timedelta(days=5)
        later = date.today() + timedelta(days=60)
        Contract.objects.create(
            title="Soon", created_by=lawyer_user, deadline=soon, status=Contract.Status.DRAFT
        )
        Contract.objects.create(
            title="Later", created_by=lawyer_user, deadline=later, status=Contract.Status.DRAFT
        )
        cutoff = date.today() + timedelta(days=10)
        res = lawyer_client.get(LIST_URL, {"deadline_before": str(cutoff)})
        assert res.status_code == 200
        assert res.data["count"] == 1
        assert res.data["results"][0]["title"] == "Soon"

    def test_soft_deleted_contracts_not_in_list(self, lawyer_client, contract):
        contract.soft_delete()
        res = lawyer_client.get(LIST_URL)
        assert res.status_code == 200
        assert res.data["count"] == 0


# =============================================================================
# Create  POST /api/contracts/
# =============================================================================

@pytest.mark.django_db
class TestContractCreate:

    def test_unauthenticated_returns_401(self, anon_client, contract_payload):
        res = anon_client.post(LIST_URL, contract_payload, format="json")
        assert res.status_code == 401

    def test_client_cannot_create(self, client_client, contract_payload):
        res = client_client.post(LIST_URL, contract_payload, format="json")
        assert res.status_code == 403

    def test_lawyer_can_create(self, lawyer_client, lawyer_user, contract_payload):
        res = lawyer_client.post(LIST_URL, contract_payload, format="json")
        assert res.status_code == 201
        assert Contract.objects.filter(created_by=lawyer_user, title="New Contract").exists()

    def test_admin_can_create(self, admin_client, admin_user, contract_payload):
        res = admin_client.post(LIST_URL, contract_payload, format="json")
        assert res.status_code == 201

    def test_lawyer_cannot_set_expired_status(self, lawyer_client, contract_payload, future_date):
        contract_payload["status"] = "EXPIRED"
        res = lawyer_client.post(LIST_URL, contract_payload, format="json")
        assert res.status_code == 400

    def test_lawyer_cannot_set_archived_status(self, lawyer_client, contract_payload):
        contract_payload["status"] = "ARCHIVED"
        res = lawyer_client.post(LIST_URL, contract_payload, format="json")
        assert res.status_code == 400

    def test_admin_can_set_archived_status(self, admin_client, contract_payload):
        contract_payload["status"] = "ARCHIVED"
        res = admin_client.post(LIST_URL, contract_payload, format="json")
        assert res.status_code == 201
        assert res.data["status"] == "ARCHIVED"

    def test_past_deadline_auto_sets_expired(self, lawyer_client, past_date):
        payload = {
            "title": "Expired Contract",
            "status": "ACTIVE",
            "deadline": str(past_date),
            "parties": [],
        }
        res = lawyer_client.post(LIST_URL, payload, format="json")
        assert res.status_code == 201
        assert res.data["status"] == "EXPIRED"

    def test_create_with_parties(self, lawyer_client, client_user, contract_payload):
        contract_payload["parties"] = [client_user.pk]
        res = lawyer_client.post(LIST_URL, contract_payload, format="json")
        assert res.status_code == 201
        contract = Contract.objects.get(pk=res.data["id"])
        assert contract.parties.filter(pk=client_user.pk).exists()


# =============================================================================
# Retrieve  GET /api/contracts/{id}/
# =============================================================================

@pytest.mark.django_db
class TestContractRetrieve:

    def test_unauthenticated_returns_401(self, anon_client, contract):
        res = anon_client.get(DETAIL_URL(contract.pk))
        assert res.status_code == 401

    def test_creator_can_retrieve(self, lawyer_client, contract):
        res = lawyer_client.get(DETAIL_URL(contract.pk))
        assert res.status_code == 200
        assert res.data["title"] == contract.title

    def test_party_can_retrieve(self, client_client, client_user, contract):
        contract.parties.add(client_user)
        res = client_client.get(DETAIL_URL(contract.pk))
        assert res.status_code == 200

    def test_admin_can_retrieve_any(self, admin_client, contract):
        res = admin_client.get(DETAIL_URL(contract.pk))
        assert res.status_code == 200

    def test_other_lawyer_cannot_retrieve(self, lawyer_client_2, contract):
        res = lawyer_client_2.get(DETAIL_URL(contract.pk))
        assert res.status_code == 404


# =============================================================================
# Update  PATCH /api/contracts/{id}/
# =============================================================================

@pytest.mark.django_db
class TestContractUpdate:

    def test_lawyer_can_update_own(self, lawyer_client, contract):
        res = lawyer_client.patch(DETAIL_URL(contract.pk), {"title": "Updated"}, format="json")
        assert res.status_code == 200
        contract.refresh_from_db()
        assert contract.title == "Updated"

    def test_lawyer_cannot_update_others_contract(self, lawyer_client_2, contract):
        res = lawyer_client_2.patch(DETAIL_URL(contract.pk), {"title": "Hack"}, format="json")
        assert res.status_code == 404

    def test_client_cannot_update(self, client_client, client_user, contract):
        contract.parties.add(client_user)
        res = client_client.patch(DETAIL_URL(contract.pk), {"title": "Hack"}, format="json")
        assert res.status_code == 403

    def test_admin_can_update_any(self, admin_client, contract):
        res = admin_client.patch(DETAIL_URL(contract.pk), {"title": "Admin Edit"}, format="json")
        assert res.status_code == 200
        contract.refresh_from_db()
        assert contract.title == "Admin Edit"


# =============================================================================
# Soft Delete  DELETE /api/contracts/{id}/
# =============================================================================

@pytest.mark.django_db
class TestContractDelete:

    def test_lawyer_can_soft_delete_own(self, lawyer_client, contract):
        res = lawyer_client.delete(DETAIL_URL(contract.pk))
        assert res.status_code == 204
        contract.refresh_from_db()
        assert contract.deleted_at is not None

    def test_soft_deleted_excluded_from_list(self, lawyer_client, contract):
        lawyer_client.delete(DETAIL_URL(contract.pk))
        res = lawyer_client.get(LIST_URL)
        assert res.data["count"] == 0

    def test_lawyer_cannot_delete_others_contract(self, lawyer_client_2, contract):
        res = lawyer_client_2.delete(DETAIL_URL(contract.pk))
        assert res.status_code == 404

    def test_client_cannot_delete(self, client_client, client_user, contract):
        contract.parties.add(client_user)
        res = client_client.delete(DETAIL_URL(contract.pk))
        assert res.status_code == 403

    def test_admin_can_delete_any(self, admin_client, contract):
        res = admin_client.delete(DETAIL_URL(contract.pk))
        assert res.status_code == 204
        contract.refresh_from_db()
        assert contract.deleted_at is not None
