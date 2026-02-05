import os
from flask import Blueprint, render_template, request, send_from_directory, redirect, url_for, flash, current_app, session

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    """Renders the main page with files from the 'uploads' folder."""
    web_file_service = current_app.config['WEB_FILE_SERVICE']
    marquee_service = current_app.config['MARQUEE_SERVICE']
    
    sort_by = request.args.get('sort', 'name')
    order = request.args.get('order', 'asc')
    
    try:
        all_files = web_file_service.get_all_files(sort_by=sort_by, order=order)
        marquee_text = marquee_service.get_marquee()
        return render_template('index.html', files=all_files, current_sort=sort_by, current_order=order, marquee_text=marquee_text)
    except Exception as e:
        flash(f"Error loading file list: {e}", "danger")
        return render_template('index.html', files=[], marquee_text="System Error")

@web_bp.route('/upload', methods=['POST'])
def upload_file_web():
    """Handles multiple file uploads from the web UI to the 'uploads' folder."""
    web_file_service = current_app.config['WEB_FILE_SERVICE']
    
    if 'files' not in request.files:
        flash('請求中沒有檔案部分。', 'warning')
        return redirect(url_for('web.index'))

    files = request.files.getlist('files')

    if not files or all(f.filename == '' for f in files):
        flash('沒有選擇任何檔案。', 'warning')
        return redirect(url_for('web.index'))

    protection_password = request.form.get('protection_password')

    successful_uploads = 0
    failed_uploads = 0
    
    for file in files:
        if file and file.filename != '':
            try:
                web_file_service.save_file(file, password=protection_password)
                successful_uploads += 1
            except Exception as e:
                flash(f"上傳檔案 '{file.filename}' 時發生錯誤: {e}", 'danger')
                failed_uploads += 1

    if successful_uploads > 0:
        flash(f"成功上傳 {successful_uploads} 個檔案。", 'success')
    if failed_uploads > 0:
        flash(f"有 {failed_uploads} 個檔案上傳失敗。", 'danger')
    
    return redirect(url_for('web.index'))

@web_bp.route('/download/<path:stored_name>', methods=['GET', 'POST'])
def download_file(stored_name):
    """Handles file downloads for the web UI from the 'uploads' folder."""
    web_file_service = current_app.config['WEB_FILE_SERVICE']
    try:
        original_name = web_file_service.get_original_filename(stored_name)
        if not original_name:
            flash(f"File metadata not found for {stored_name}.", 'danger')
            return redirect(url_for('web.index'))

        # Check if password protected
        # Need to check metadata directly or via a service method efficiently?
        # verify_password handles checks.
        
        # If POST, it's a password attempt or a direct download if no password needed (but GET handles no password usually)
        if request.method == 'POST':
            password = request.form.get('password')
            if not web_file_service.verify_password(stored_name, password):
                flash("密碼錯誤，無法下載。", 'danger')
                return redirect(url_for('web.index'))
        else:
            # GET request: Check if file needs password
            # We can't easily check "needs password" without FileInfo details exposed here, 
            # but we can try to verify with empty password? No.
            # We should rely on frontend to only send POST if locked.
            # But for security, we MUST check on backend.
            # If has password and method is GET -> Redirect to index with error or show password page?
            # Ideally: Frontend Modal sends POST.
            # If backend detects protected file on GET, deny.
            
            # To do this, we need to know if it has a password.
            # web_file_service.get_all_files returns list, expensive.
            # Let's peek metadata?
            # Reusing verify_password with None password? 
            # verify_password(stored, None) returns False if has_password is set.
            # Wait, verify_password internal logic: if not stored_hash return True.
            # So if verify_password(stored, None) returns False, it means it HAS a password and we didn't provide one.
            if not web_file_service.verify_password(stored_name, None):
                flash("此檔案受密碼保護，請輸入密碼。", 'warning')
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
    password = request.form.get('password')
    
    try:
        if not web_file_service.verify_password(stored_name, password):
             flash("密碼錯誤，無法刪除。", 'danger')
             return redirect(url_for('web.index'))
             
        original_name = web_file_service.delete_file(stored_name)
        if original_name:
            flash(f"檔案 '{original_name}' 已成功刪除。", 'success')
        else:
            flash(f"檔案記錄已移除，但檔案先前已不存在於磁碟上。", 'warning')
    except Exception as e:
        flash(f"刪除檔案時發生錯誤: {e}", 'danger')
    
    return redirect(url_for('web.index'))

@web_bp.route('/check_lock/<path:stored_name>')
def check_lock(stored_name):
    """API to check if file is locked (for frontend JS)."""
    web_file_service = current_app.config['WEB_FILE_SERVICE']
@web_bp.route('/admin', methods=['GET'])
def admin_page():
    """Renders the admin page."""
    if not session.get('is_admin'):
        return render_template('admin.html', logged_in=False)
    
    marquee_service = current_app.config['MARQUEE_SERVICE']
    current_text = marquee_service.get_marquee()
    return render_template('admin.html', logged_in=True, marquee_text=current_text)

@web_bp.route('/admin/login', methods=['POST'])
def admin_login():
    """Handles admin login."""
    password = request.form.get('password')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    
    if admin_password and password == admin_password:
        session['is_admin'] = True
        flash('登入成功', 'success')
    else:
        flash('密碼錯誤', 'danger')
        
    return redirect(url_for('web.admin_page'))

@web_bp.route('/admin/logout')
def admin_logout():
    """Handles admin logout."""
    session.pop('is_admin', None)
    flash('已登出', 'success')
    return redirect(url_for('web.admin_page'))

@web_bp.route('/admin/update_marquee', methods=['POST'])
def update_marquee():
    """Updates the marquee text."""
    if not session.get('is_admin'):
        return redirect(url_for('web.admin_page'))
        
    text = request.form.get('marquee_text')
    marquee_service = current_app.config['MARQUEE_SERVICE']
    marquee_service.set_marquee(text)
    
    flash('跑馬燈訊息已更新', 'success')
    return redirect(url_for('web.admin_page'))
