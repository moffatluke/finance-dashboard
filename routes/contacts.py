from flask import Blueprint, request, jsonify
from db import db  # reuse the Firestore connection

contacts_bp = Blueprint("contacts", __name__)

# GET /contacts — fetch all contacts
@contacts_bp.route("/contacts", methods=["GET"])
def get_contacts():
    docs = db.collection("contacts").stream()  # query every doc in the collection
    contacts = []
    for doc in docs:
        contact = doc.to_dict()   # convert Firestore doc to a plain dict
        contact["id"] = doc.id    # attach the doc's ID so the frontend can reference it
        contacts.append(contact)
    return jsonify(contacts)  # send back as JSON array

############################################

# POST /contacts — add a new contact
@contacts_bp.route("/contacts", methods=["POST"])
def add_contact():
    data = request.get_json()  # read the JSON body from the request
    doc_ref = db.collection("contacts").add(data)  # add a new doc to Firestore
    return jsonify({"id": doc_ref[1].id}), 201  # return the new doc's ID, 201 = Created