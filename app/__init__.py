import os
from flask import Flask, Blueprint
from services import FileService

def create_app():
    app = Flask(__name__)

    # --- Configuration ---
    app.config['SECRET_KEY'] = 'a_random_secret_key_that_should_be_changed' # Will be set by run.py or config
    API_KEY_SECRET = '5132135788' # Will be set by run.py or config
    MPS_DESTINATION_FOLDER = r'P:/F004/MPS維護' # Will be set by run.py or config

    # Determine base directory dynamically for relative paths
    base_dir = os.path.abspath(os.path.dirname(__file__))

    UPLOAD_FOLDER = os.path.join(base_dir, 'uploads')
    SAP_STAGING_FOLDER = os.path.join(base_dir, 'sap_staging')

    # Ensure upload and staging folders exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(SAP_STAGING_FOLDER, exist_ok=True)

    # --- Service Instantiation ---
    # A separate service instance for each folder ensures separation of concerns
    web_file_service = FileService(upload_folder=UPLOAD_FOLDER)
    sap_file_service = FileService(upload_folder=SAP_STAGING_FOLDER)

    # Store services and API key in app.config for easy access by blueprints
    app.config['WEB_FILE_SERVICE'] = web_file_service
    app.config['SAP_FILE_SERVICE'] = sap_file_service
    app.config['API_KEY_SECRET'] = API_KEY_SECRET
    app.config['MPS_DESTINATION_FOLDER'] = MPS_DESTINATION_FOLDER
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # Make these accessible if needed in blueprints
    app.config['SAP_STAGING_FOLDER'] = SAP_STAGING_FOLDER # Make these accessible if needed in blueprints


    # --- Register Blueprints ---
    from app.web_ui.routes import web_bp
    from app.sap_api.routes import sap_bp

    app.register_blueprint(web_bp)
    app.register_blueprint(sap_bp, url_prefix='/api') # /api prefix for SAP endpoint

    return app