import firebase_admin # import all the firebase stuff
# the firebase_admin is the official Python library to talking to firebase
from firebase_admin import credentials, firestore # Taking out the credentials(authenticating) firestore(db)
from dotenv import load_dotenv # .dotenv reads the .env files
import os # access environment variables

load_dotenv() # reads the .env file and loads

cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS")) 
firebase_admin.initialize_app(cred) # like logging in
db = firestore.client() # creates the db client object