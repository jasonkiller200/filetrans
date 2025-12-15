from flask import Blueprint, request, current_app

sap_bp = Blueprint('sap_api', __name__)

@sap_bp.route('/sap_upload', methods=['POST'])
def upload_file_sap():
    """
    Handles automated file uploads from the SAP script.
    Authenticates, saves to 'sap_staging', moves to MPS folder, and cleans up.
    """
    sap_file_service = current_app.config['SAP_FILE_SERVICE']
    api_key_secret = current_app.config['API_KEY_SECRET']
    mps_destination_folder = current_app.config['MPS_DESTINATION_FOLDER']

    # 1. Authentication
    api_key_provided = request.headers.get('X-API-Key')
    if api_key_provided != api_key_secret:
        return "Unauthorized: Invalid API Key", 401
    
    # 2. File validation
    if 'file' not in request.files:
        return "No file part in the request.", 400
    file = request.files['file']
    if file.filename == '':
        return "No file selected.", 400

    # 3. Process the file
    try:
        # Save the file to the staging area
        saved_file_info = sap_file_service.save_file(file)
        
        # Attempt to transfer to the final destination
        try:
            sap_file_service.transfer_to_mps(saved_file_info, mps_destination_folder)
            # If transfer is successful, delete from staging
            sap_file_service.delete_file(saved_file_info.stored_name)
            
            return f"檔案 '{saved_file_info.original_name}' 已成功上傳並移動至 MPS 資料夾。", 200

        except Exception as transfer_e:
            # If transfer fails, the file remains in the sap_staging folder for manual recovery.
            return f"檔案 '{saved_file_info.original_name}' 上傳成功，但移動至 MPS 資料夾時發生錯誤: {transfer_e}", 500

    except Exception as e:
        return f"An error occurred during initial upload/save: {e}", 500
