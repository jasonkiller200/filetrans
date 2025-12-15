import os
from flask import Blueprint, render_template, request, send_from_directory, redirect, url_for, flash, current_app

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    """Renders the main page with files from the 'uploads' folder."""
    web_file_service = current_app.config['WEB_FILE_SERVICE']
    try:
        all_files = web_file_service.get_all_files()
        return render_template('index.html', files=all_files)
    except Exception as e:
        flash(f"Error loading file list: {e}", "danger")
        return render_template('index.html', files=[])

@web_bp.route('/upload', methods=['POST'])
def upload_file_web():
    """Handles file uploads from the web UI to the 'uploads' folder."""
    web_file_service = current_app.config['WEB_FILE_SERVICE']
    if 'file' not in request.files:
        flash('No file part in the request.', 'warning')
        return redirect(url_for('web.index'))

    file = request.files['file']

    if file.filename == '':
        flash('No file selected.', 'warning')
        return redirect(url_for('web.index'))

    if file:
        try:
            saved_file_info = web_file_service.save_file(file)
            flash(f"檔案 '{saved_file_info.original_name}' (大小: {saved_file_info.formatted_size}) 上傳成功!", 'success')
        except Exception as e:
            flash(f"An error occurred while uploading: {e}", 'danger')
    
    return redirect(url_for('web.index'))

@web_bp.route('/download/<path:stored_name>')
def download_file(stored_name):
    """Handles file downloads for the web UI from the 'uploads' folder."""
    web_file_service = current_app.config['WEB_FILE_SERVICE']
    try:
        original_name = web_file_service.get_original_filename(stored_name)
        if not original_name:
            flash(f"File metadata not found for {stored_name}.", 'danger')
            return redirect(url_for('web.index'))

        return send_from_directory(
            web_file_service.upload_folder,
            stored_name,
            as_attachment=True,
            download_name=original_name
        )
    except FileNotFoundError:
        flash(f"File not found on disk.", 'danger')
        return redirect(url_for('web.index'))

@web_bp.route('/delete/<path:stored_name>', methods=['POST'])
def delete_file_route(stored_name):
    """Handles file deletions for the web UI from the 'uploads' folder."""
    web_file_service = current_app.config['WEB_FILE_SERVICE']
    try:
        original_name = web_file_service.delete_file(stored_name)
        if original_name:
            flash(f"檔案 '{original_name}' 已成功刪除。", 'success')
        else:
            flash(f"檔案記錄已移除，但檔案先前已不存在於磁碟上。", 'warning')
    except Exception as e:
        flash(f"刪除檔案時發生錯誤: {e}", 'danger')
    
    return redirect(url_for('web.index'))
