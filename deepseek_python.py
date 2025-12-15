# file_receiver.py - 在 192.168.6.119 上运行
from flask import Flask, request, jsonify
import os
import logging
from datetime import datetime

app = Flask(__name__)

# 配置
UPLOAD_FOLDER = r'P:\F004\MPS维护'  # 你的网络磁盘路径
ALLOWED_EXTENSIONS = {'xlsx', 'txt', 'csv'}  # 允许的文件类型
API_KEY = 'YOUR_SECURE_API_KEY_HERE'  # 设置一个复杂的密钥，用于验证

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传请求"""
    # 1. 验证 API 密钥
    auth_header = request.headers.get('X-API-Key')
    if auth_header != API_KEY:
        logging.warning(f"未授权的访问尝试: {request.remote_addr}")
        return jsonify({'error': 'Unauthorized'}), 401
    
    # 2. 检查是否有文件在请求中
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # 3. 检查文件类型
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # 4. 安全地保存文件
    try:
        filename = file.filename
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # 如果文件已存在，可以添加时间戳重命名，避免覆盖
        if os.path.exists(save_path):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{timestamp}{ext}"
            save_path = os.path.join(UPLOAD_FOLDER, filename)
        
        file.save(save_path)
        logging.info(f"文件上传成功: {filename} 来自 {request.remote_addr}")
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200
    
    except Exception as e:
        logging.error(f"文件保存失败: {str(e)}")
        return jsonify({'error': 'Failed to save file'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({'status': 'healthy', 'upload_folder': UPLOAD_FOLDER}), 200

if __name__ == '__main__':
    # 注意：在生产环境中，应使用 WSGI 服务器（如 gunicorn、waitress）而不是直接运行
    app.run(host='0.0.0.0', port=5000, debug=False)