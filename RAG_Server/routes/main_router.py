from flask import Blueprint
import routes.chroma_apis as chroma_apis

# Create a Blueprint for the main router
main_router = Blueprint('main_router', __name__)

# Define a simple route
@main_router.route('/')
def home():
    return "Welcome to the Main Router!"

# Register another router (e.g., chroma_apis) with the main router
main_router.register_blueprint(chroma_apis.router)
