import pytest
from unittest.mock import patch, MagicMock
from app import create_app


@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.test_client() as c:
        yield c


def make_mock_doc(doc_id, data):
    doc = MagicMock()
    doc.id = doc_id
    doc.to_dict.return_value = data
    return doc


def test_get_transactions_returns_list(client):
    mock_doc = make_mock_doc("tx1", {
        "amount": 500, "type": "income", "category": "Revenue",
        "description": "Client payment", "date": "2026-05-09",
        "paymentMethod": "Bank Transfer", "contactId": ""
    })
    with patch("routes.transactions.db") as mock_db:
        mock_db.collection.return_value.stream.return_value = [mock_doc]
        response = client.get("/api/transactions")
        assert response.status_code == 200
        data = response.get_json()
        assert data[0]["amount"] == 500


def test_create_transaction_missing_amount_returns_400(client):
    with patch("routes.transactions.db"):
        response = client.post("/api/transactions", json={"type": "income"})
        assert response.status_code == 400


def test_create_transaction_success(client):
    with patch("routes.transactions.db") as mock_db:
        mock_ref = MagicMock()
        mock_ref.id = "tx_new"
        mock_db.collection.return_value.document.return_value = mock_ref
        response = client.post("/api/transactions", json={
            "amount": 200,
            "type": "expense",
            "category": "Software",
            "description": "GitHub subscription",
            "date": "2026-05-09",
            "paymentMethod": "Card",
            "contactId": ""
        })
        assert response.status_code == 201
        assert response.get_json()["id"] == "tx_new"


def test_delete_transaction_not_found(client):
    with patch("routes.transactions.db") as mock_db:
        mock_db.collection.return_value.document.return_value.get.return_value.exists = False
        response = client.delete("/api/transactions/missing")
        assert response.status_code == 404