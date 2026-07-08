# Name_card_system

名片 OCR 系統：上傳 PDF、自動解析欄位、寫入 Excel，並提供 Web 搜尋與預覽介面。

## Windows 使用方式

### 第一次使用（電腦未安裝 Python）

1. 雙擊 `install_python_windows.bat`
2. 依畫面指示安裝 Python 3.11 或 3.12
3. 安裝時**務必勾選** `Add python.exe to PATH`
4. 安裝完成後，雙擊 `啟動名片系統_Windows.bat`

### 日常使用

雙擊 `啟動名片系統_Windows.bat`（或 `start_upload_app_windows_auto_venv.bat`）

系統會自動：

- 建立 `.venv` 虛擬環境
- 安裝所需套件
- 開啟瀏覽器到 `http://127.0.0.1:5000`

> 請保持黑色命令視窗開啟；關閉視窗即停止 Web App。

### 其他電腦不裝 Python 也能用（推薦）

只需**一台電腦**安裝 Python 並執行系統，其他電腦用瀏覽器開啟即可：

1. 在主機電腦雙擊 `啟動名片系統_區域網路_Windows.bat`
2. 記下命令視窗顯示的「區域網路網址」，例如：`http://192.168.1.50:5000`
3. 同一 Wi‑Fi / 公司網路的其他電腦，用 Chrome / Edge 開啟該網址

> 其他電腦**不需要**安裝 Python，只要有瀏覽器。

注意：

- 主機電腦必須保持開機，且命令視窗不能關
- 兩台電腦要在同一個區域網路
- 若無法連線，檢查 Windows 防火牆是否允許 Python

## macOS 使用方式

雙擊 `start_webapp.command`

其他電腦用瀏覽器連線（主機先執行）：

```bash
NAMECARD_HOST=0.0.0.0 .venv/bin/python app.py
```

## 打包成 Windows .exe（免安裝 Python）

> **必須在 Windows 電腦上打包**，無法在 Mac 直接產生 `.exe`。

### 打包步驟（只需做一次）

1. 在 Windows 安裝 Python 3.11 或 3.12
2. 下載專案後，雙擊 `build_windows_exe.bat`
3. 完成後會產生：`dist\Name_card_system\`

### 分發給其他電腦

把整個資料夾 `dist\Name_card_system\` 複製到其他 Windows 電腦，雙擊：

```
Name_card_system.exe
```

資料會保存在 exe 同一層：

- `A Namecard-system-database.xlsx`
- `file Name_Card_system\`

### 注意

- 整個資料夾約 **300MB～800MB**（含 OCR 模型）
- 第一次啟動可能較慢
- 防毒軟體可能誤判，必要時加入白名單
