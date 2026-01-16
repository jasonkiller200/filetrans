# 檔案傳輸應用程式 (File Transfer App)

一個基於 Flask 的區網檔案傳輸系統，提供 Web 介面和 API 端點，用於在區域網路內輕鬆共享和管理檔案。

## 功能特色

- 📤 **Web 介面上傳**：透過瀏覽器直接上傳和下載檔案
- 🔌 **SAP API 整合**：提供 API 端點供 SAP 腳本自動化上傳
- 📁 **雙資料夾管理**：分別管理 Web 上傳和 SAP 暫存檔案
- 🔐 **API 金鑰驗證**：保護 SAP 端點的安全性
- 🌐 **區網存取**：自動偵測本機 IP，方便區網內其他裝置存取
- 💾 **檔案元資料管理**：使用 JSON 檔案追蹤檔案資訊

## 系統需求

- Python 3.8 或以上版本
- Windows/Linux/macOS

## 安裝說明

### 1. 建立虛擬環境

在專案目錄下執行：

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. 安裝依賴套件

啟動虛擬環境後，安裝所需套件：

```bash
pip install -r requirements.txt
```

## 使用方式

### 啟動應用程式

**方法一：使用 PowerShell 腳本（Windows）**
```powershell
.\start_app.ps1
```

**方法二：直接執行 Python**
```bash
python run.py
```

### 存取應用程式

應用程式啟動後，終端機會顯示：
```
--- 區網檔案傳輸伺服器已啟動 ---
 * 網頁介面請瀏覽: http://192.168.x.x:5000
 * SAP 腳本請上傳至: http://192.168.x.x:5000/api/sap_upload
---------------------------------
```

- **Web 介面**：在瀏覽器開啟顯示的網址
- **SAP API**：使用顯示的 API 端點進行自動化上傳

## 專案結構

```
file_transfer_app/
├── app/
│   ├── __init__.py           # Flask 應用程式工廠
│   ├── sap_api/              # SAP API 端點
│   │   └── routes.py
│   ├── web_ui/               # Web 介面路由
│   │   └── routes.py
│   ├── static/               # 靜態資源 (CSS, JS)
│   ├── templates/            # HTML 模板
│   ├── uploads/              # Web 上傳檔案儲存區
│   └── sap_staging/          # SAP 暫存檔案區
├── models.py                 # 資料模型
├── services.py               # 業務邏輯服務
├── run.py                    # 應用程式入口點
├── requirements.txt          # Python 依賴套件
└── start_app.ps1            # Windows 啟動腳本
```

## API 使用說明

### SAP 檔案上傳 API

**端點：** `POST /api/sap_upload`

**Headers：**
```
X-API-Key: 5132135788
```

**Body：**
- `file`: 要上傳的檔案（multipart/form-data）

**範例（使用 curl）：**
```bash
curl -X POST http://192.168.x.x:5000/api/sap_upload \
  -H "X-API-Key: 5132135788" \
  -F "file=@/path/to/your/file.txt"
```

**回應：**
- `200`: 上傳成功
- `401`: API 金鑰無效
- `400`: 請求格式錯誤
- `500`: 伺服器錯誤

## 設定

您可以在 [app/__init__.py](app/__init__.py) 中修改以下設定：

- `SECRET_KEY`: Flask 密鑰（建議在生產環境中使用環境變數）
- `API_KEY_SECRET`: SAP API 的認證金鑰
- `MPS_DESTINATION_FOLDER`: SAP 檔案的最終目的地資料夾

## 安全性注意事項

1. **變更預設密鑰**：在生產環境中務必修改 `SECRET_KEY` 和 `API_KEY_SECRET`
2. **防火牆設定**：確保只有可信任的網路能存取此服務
3. **檔案驗證**：考慮添加檔案類型和大小限制
4. **HTTPS**：在生產環境中使用 HTTPS 保護資料傳輸

## 除錯模式

應用程式預設以除錯模式執行（`debug=True`），在生產環境中應該關閉此選項：

在 [run.py](run.py) 中修改：
```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

## 常見問題

**Q: 無法存取應用程式？**
A: 檢查防火牆設定，確保 Port 5000 未被封鎖。

**Q: 上傳的檔案在哪裡？**
A: Web 上傳的檔案在 `app/uploads/`，SAP 上傳的檔案會自動移至設定的 MPS 資料夾。

**Q: 如何變更 Port？**
A: 在 [run.py](run.py) 中修改 `port = 5000` 為您需要的 Port 號。

## 授權

此專案為內部使用工具，請勿用於商業用途。

## 聯絡資訊

如有問題或建議，請聯絡開發團隊。
