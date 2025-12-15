import socket
from app import create_app

def get_local_ip():
    """Gets the local IP address of the machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

app = create_app()

if __name__ == '__main__':
    host_ip = get_local_ip()
    port = 5000
    print("--- 區網檔案傳輸伺服器已啟動 ---")
    print(f" * 網頁介面請瀏覽: http://{host_ip}:{port}")
    print(f" * SAP 腳本請上傳至: http://{host_ip}:{port}/api/sap_upload")
    print("---------------------------------")
    app.run(host='0.0.0.0', port=port, debug=True)
