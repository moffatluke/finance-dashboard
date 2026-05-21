from flask import Blueprint, request, jsonify
from db import db  # reuse the Firestore connection
from google.cloud.firestore_v1 import SERVER_TIMESTAMP  # use server time instead of local time

transactions_bp = Blueprint("transactions", __name__)
COLLECTION = "transactions"  # Firestore collection name
REQUIRED = ["amount", "type", "category", "description", "date", "paymentMethod"]  # fields that must be present


# GET /api/transactions — fetch all transactions
@transactions_bp.get("/api/transactions")
def get_transactions():
    try:

        docs = db.collection(COLLECTION).stream()  # fetch every doc in the collection

        return jsonify([{"id": d.id, **d.to_dict()} for d in docs])  
        # return as JSON array with id attached (yay always need ids)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# POST /api/transactions — create a new transaction
@transactions_bp.post("/api/transactions")
def create_transaction():
    try:
        data = request.get_json()  # read JSON body from the request
        for field in REQUIRED:
            if data.get(field) is None:  # check all required fields are present
                return jsonify({"error": f"'{field}' is required"}), 400
        data["createdAt"] = SERVER_TIMESTAMP  # let Firestore set the timestamp
        ref = db.collection(COLLECTION).document()  # create a new doc with auto-generated ID
        ref.set(data)  # write the data to Firestore
        return jsonify({"id": ref.id}), 201  # return the new ID, 201 = Created
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# PUT /api/transactions/<doc_id> — update an existing transaction
@transactions_bp.put("/api/transactions/<doc_id>")
def update_transaction(doc_id):
    try:
        data = request.get_json()
        data.pop("createdAt", None)  # never overwrite the original creation timestamp
        ref = db.collection(COLLECTION).document(doc_id)
        if not ref.get().exists:  # make sure the doc exists before updating
            return jsonify({"error": "Transaction not found"}), 404
        ref.update(data)  # update only the fields sent, leave the rest untouched
        return jsonify({"id": doc_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# DELETE /api/transactions/<doc_id> — delete a transaction
@transactions_bp.delete("/api/transactions/<doc_id>")
def delete_transaction(doc_id):
    try:
        ref = db.collection(COLLECTION).document(doc_id)
        if not ref.get().exists:  # return 404 if doc doesn't exist
            return jsonify({"error": "Transaction not found"}), 404
        ref.delete()
        return jsonify({"message": "Deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500