import json
from types import SimpleNamespace
from bson import ObjectId


class FakeCursor:
    def __init__(self, items):
        self.items = items

    def sort(self, key, direction):
        reverse = direction == -1
        self.items = sorted(self.items, key=lambda item: item.get(key), reverse=reverse)
        return self

    def __iter__(self):
        return iter(self.items)


class FakeCollection:
    def __init__(self):
        self.items = []

    def insert_one(self, document):
        doc = document.copy()
        doc.setdefault("_id", ObjectId())
        self.items.append(doc)
        return SimpleNamespace(inserted_id=doc["_id"])

    def find_one(self, query):
        for doc in self.items:
            if all(doc.get(key) == value for key, value in query.items()):
                return doc
        return None

    def update_one(self, query, update):
        doc = self.find_one(query)
        if not doc:
            return SimpleNamespace(matched_count=0)
        updates = update.get("$set", {})
        doc.update(updates)
        return SimpleNamespace(matched_count=1)

    def find(self, query):
        results = [doc for doc in self.items if all(doc.get(key) == value for key, value in query.items())]
        return FakeCursor(results)

    def create_index(self, *args, **kwargs):
        return "idx"


class FakeDB:
    def __init__(self):
        self.agreements = FakeCollection()
        self.agreement_actions = FakeCollection()


def _setup_fake_db(test_client):
    fake_db = FakeDB()
    test_client.application.db = fake_db
    return fake_db


def _create_agreement(test_client, status="proposed"):
    payload = {
        "parties": [{"id": "requester"}],
        "terms": {"human_readable": "Initial terms", "machine_readable": {"scope": "test"}},
        "status": status,
        "model_id": "model-x",
        "model_version": "v1",
    }
    response = test_client.post('/api/agreements', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data.decode('utf-8'))
    return data["agreement"]


def test_accept_proposed_agreement(test_client):
    _setup_fake_db(test_client)
    agreement = _create_agreement(test_client, status="proposed")

    action_payload = {"action": "accept", "actor_party_id": "requester"}
    response = test_client.post(
        f"/api/agreements/{agreement['id']}/actions",
        data=json.dumps(action_payload),
        content_type='application/json',
    )

    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert data["agreement"]["status"] == "active"


def test_decline_proposed_agreement(test_client):
    _setup_fake_db(test_client)
    agreement = _create_agreement(test_client, status="proposed")

    action_payload = {"action": "decline", "actor_party_id": "requester"}
    response = test_client.post(
        f"/api/agreements/{agreement['id']}/actions",
        data=json.dumps(action_payload),
        content_type='application/json',
    )

    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert data["agreement"]["status"] == "rejected"


def test_counter_supersedes_agreement(test_client):
    _setup_fake_db(test_client)
    agreement = _create_agreement(test_client, status="proposed")

    action_payload = {
        "action": "counter",
        "actor_party_id": "requester",
        "payload": {
            "terms": {"human_readable": "Counter terms", "machine_readable": {"scope": "counter"}}
        },
    }

    response = test_client.post(
        f"/api/agreements/{agreement['id']}/actions",
        data=json.dumps(action_payload),
        content_type='application/json',
    )

    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert data["agreement"]["status"] == "superseded"
    assert data["counter_agreement"]["status"] == "proposed"
    assert data["counter_agreement"]["supersedes_agreement_id"] == agreement["id"]


def test_invalid_transition_on_draft(test_client):
    _setup_fake_db(test_client)
    agreement = _create_agreement(test_client, status="draft")

    action_payload = {"action": "accept", "actor_party_id": "requester"}
    response = test_client.post(
        f"/api/agreements/{agreement['id']}/actions",
        data=json.dumps(action_payload),
        content_type='application/json',
    )

    assert response.status_code == 400
