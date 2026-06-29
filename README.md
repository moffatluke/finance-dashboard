# FINANCE DASHBOARD

A browser-based CRM dashboard built with Python Flask and Google Firestore. Track contacts through a sales pipeline, log income and expenses, and view a live summary dashboard, all from the browser with no local database required.

## Live Demo

**[View the live demo →](https://finance-dashboard-demo-weld.vercel.app/dashboard.html)** A deployed, click-through version preloaded with sample data, so you can explore the dashboard, contacts, and transactions without any Firebase setup.

## Instructions for Build and Use

Steps to build and/or run the software:

1. Clone the repository and navigate to the project folder
2. Create and activate a virtual environment: `python -m venv venv` then `venv\Scripts\activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Add your `serviceAccount.json` to the project root (download from Firebase Console → Project Settings → Service Accounts)
5. Create a `.env` file in the project root with: `GOOGLE_APPLICATION_CREDENTIALS=serviceAccount.json`
6. Run the app: `python app.py`

Instructions for using the software:

1. Open `http://127.0.0.1:5000` in your browser
2. Use the sidebar to navigate between Dashboard, Contacts, and Transactions
3. On the **Contacts** page, add a new contact using the form and assign them a pipeline status
4. On the **Transactions** page, log income or expenses and link them to a contact
5. On the **Dashboard**, view a live summary of total contacts, revenue, and expenses
6. Use the edit and delete buttons in each table to update or remove records


## Development Environment

To recreate the development environment, you need the following software and/or libraries with the specified versions:

* Python 3.12+
* flask 3.1.0 — web server and REST API routing
* firebase-admin 6.5.0 — Firestore database connection
* python-dotenv 1.0.1 — loads environment variables from `.env`


## Screenshots

### Dashboard
A live summary of revenue, expenses, net income, and pipeline status — with a 6-month cash flow chart that updates as transactions are added.

![Dashboard](docs/screenshots/dashboard.png)

---

### Contacts
A searchable, filterable contact book with pipeline status badges, follow-up dates, and notes for each person.

![Contacts](docs/screenshots/contacts.png)

---

### Transactions
A full transaction ledger with income/expense filtering, contact linking, and inline editing.

![Transactions](docs/screenshots/transactions.png)

---

## Data Model

The app uses two Firestore collections that are linked together:

- **contacts** — people in your pipeline with a name, company, status, and follow-up date
- **transactions** — income and expense records, each with an optional `contactId` field that references a contact

This lets you see which client a payment came from, link expenses to the people involved, and navigate directly from a transaction to the contact's profile page. The dashboard aggregates both collections to give a live financial and pipeline summary in a single API call.

---

## Code Highlights

### API Client (`frontend/app.js`)
A lightweight JavaScript API client that centralizes all `fetch()` calls in one place. Every page uses it — no raw `fetch` scattered across the frontend.

```javascript
const api = {
  dashboard: () => api._req("GET", "/api/dashboard"),
  contacts: {
    list: (status) => api._req("GET", "/api/contacts" + (status ? `?status=${encodeURIComponent(status)}` : "")),
    create: (data) => api._req("POST", "/api/contacts", data),
    update: (id, data) => api._req("PUT", `/api/contacts/${id}`, data),
    remove: (id) => api._req("DELETE", `/api/contacts/${id}`),
  },
  transactions: {
    list: () => api._req("GET", "/api/transactions"),
    create: (data) => api._req("POST", "/api/transactions", data),
    update: (id, data) => api._req("PUT", `/api/transactions/${id}`, data),
    remove: (id) => api._req("DELETE", `/api/transactions/${id}`),
  },
};
```

Adding a contact from a form is a single line:
```javascript
await api.contacts.create({ name: "Jane Doe", status: "Lead" });
```

---

### Dashboard Summary Endpoint (`routes/dashboard.py`)
A single `GET /api/dashboard` route that queries both Firestore collections, aggregates the data in Python, and returns a ready-to-render JSON summary — no extra requests needed from the frontend.

```python
@dashboard_bp.get("/api/dashboard")
def get_dashboard():
    contacts = [{"id": d.id, **d.to_dict()} for d in db.collection("contacts").stream()]
    transactions = [{"id": d.id, **d.to_dict()} for d in db.collection("transactions").stream()]

    by_status = {"Lead": 0, "Contacted": 0, "Customer": 0}
    for c in contacts:
        status = c.get("status", "")
        if status in by_status:
            by_status[status] += 1

    total_income = sum(t["amount"] for t in transactions if t.get("type") == "income")
    total_expenses = sum(t["amount"] for t in transactions if t.get("type") == "expense")

    return jsonify({
        "totalContacts": len(contacts),
        "byStatus": by_status,
        "totalIncome": total_income,
        "totalExpenses": total_expenses,
    })
```

---

### Testing with Firebase Mocks (`tests/`)
All 11 tests run without a real Firebase connection. A session-level pytest fixture patches the Firebase SDK so tests are fast, isolated, and don't touch the live database.

```python
# tests/conftest.py — patches Firebase for the entire test session
@pytest.fixture(autouse=True, scope="session")
def mock_firebase():
    with patch("firebase_admin.initialize_app"), \
         patch("firebase_admin.credentials.Certificate", return_value=MagicMock()), \
         patch("firebase_admin.firestore.client", return_value=MagicMock()):
        yield

# tests/test_contacts.py — each test mocks only what it needs
def test_get_contacts_returns_list(client):
    mock_doc = make_mock_doc("abc123", {"name": "Jane Doe", "status": "Lead"})
    with patch("routes.contacts.db") as mock_db:
        mock_db.collection.return_value.stream.return_value = [mock_doc]
        response = client.get("/api/contacts")
        assert response.status_code == 200
        assert response.get_json()[0]["name"] == "Jane Doe"
```

Run all tests with:
```bash
venv\Scripts\pytest -v
```

---

## Useful Websites to Learn More

I found these websites useful in developing this software:

* [Claude AI](https://claude.ai)
* [Flask Documentation](https://flask.palletsprojects.com/)
* [Firestore Documentation](https://firebase.google.com/docs/firestore)
* [Firebase Console](https://console.firebase.google.com/)
* [Python dotenv Docs](https://pypi.org/project/python-dotenv/)


## Future Work

The following items I plan to fix, improve, and/or add to this project in the future:

* [ ] Add user authentication so the app can be used by a team
* [ ] Filter transactions by date range or category
* [ ] Export contacts and transactions to CSV
* [ ] Add a search/filter bar to the Contacts table
