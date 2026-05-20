from flask import Flask, send_from_directory
from routes.contacts import contacts_bp
from routes.transactions import transactions_bp
from routes.dashboard import dashboard_bp

# Browser (HTML/JS)
#       ↕  HTTP requests
# Flask App (Python)
#       ↕  Firestore SDK calls
# Google Firestore (cloud database)

def create_app(testing=False):
    # Flask app factory — creates and configures the app
    app = Flask(__name__, static_folder="frontend")
    app.config["TESTING"] = testing

    # Register each blueprint (group of related routes)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(dashboard_bp)

    # Serve the frontend HTML files
    @app.route("/")
    def index():
        return send_from_directory("frontend", "index.html")

    @app.route("/<path:filename>")
    def serve_static(filename):
        return send_from_directory("frontend", filename)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)