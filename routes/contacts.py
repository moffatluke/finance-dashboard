from flask import Blueprint, request, jsonify
from db import db # talk to the data base
from google.cloud.firestore_v1 import SERVER_TIMESTAMP # timestamp the server not local machine
# jsonify converts python lists into json resposes to send back to the browers

contacts_bp = Blueprint("contacts", __name__) # creates blueprint object
COLLECTION = "contacts" # constant so if I rename the firestore collection it only needs to change in one place
REQUIRED = ["name"] # Needed fields to make a contact


# Get route. 
@contacts_bp.get("/api/contacts")
def get_contacts():
    try:
        status = request.args.get("status") # checks url
        col = db.collection(COLLECTION)
        docs = col.where("status", "==", status).stream() if status else col.stream()
        return jsonify([{"id": d.id, **d.to_dict()} for d in docs]) # filters by status
    except Exception as e:
        return jsonify({"error": str(e)}), 500 # prevents crashing and handles errors


# CREATE ROUTE (Creates a new contact)
@contacts_bp.post("/api/contacts")
def create_contact():
    try:
        data = request.get_json()
        for field in REQUIRED:
            if not data.get(field):
                return jsonify({"error": f"'{field}' is required"}), 400
        data["createdAt"] = SERVER_TIMESTAMP
        ref = db.collection(COLLECTION).document()
        ref.set(data)
        return jsonify({"id": ref.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# PUT route (updates a existing contact)
@contacts_bp.put("/api/contacts/<doc_id>")
def update_contact(doc_id):
    try:
        data = request.get_json()
        data.pop("createdAt", None) # removed creatAt fron the update data ( don't want to overwrite)
        ref = db.collection(COLLECTION).document(doc_id)
        if not ref.get().exists: # checks to see if the data exists in the db before it updates it. 
            return jsonify({"error": "Contact not found"}), 404
        ref.update(data) # updates only the fields sent and donesn't check anything else.
        return jsonify({"id": doc_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# DELETE ROUTE
@contacts_bp.delete("/api/contacts/<doc_id>")
def delete_contact(doc_id): 
    try:
        ref = db.collection(COLLECTION).document(doc_id)
        if not ref.get().exists: # checks to see if it exists
            return jsonify({"error": "Contact not found"}), 404
        ref.delete()
        return jsonify({"message": "Deleted"}) # yay its gone!
    except Exception as e:
        return jsonify({"error": str(e)}), 500