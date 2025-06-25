# 智慧瓦斯 AI 管理系統 - 企業級App模式

> **本系統目前AI模型：Google Gemini 1.5 Pro，API Key 已於 config.py 設定。**
> 
> 請勿將金鑰公開於公開文件或網路。

> Jy技術團隊 - 專業瓦斯行管理AI助手  
> 支援 PWA、原生App、多API備援、快取配額管理

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Web%20%7C%20PWA%20%7C%20Mobile-blue.svg)

## 🚀 企業級特性

### ✨ 前端特性
- **完全RWD響應式** - 桌機/平板/手機無縫體驗
- **PWA支援** - 可「加入主畫面」變App，支援離線/推播功能
- **原生App包裝** - 支援 Capacitor/Tauri/React Native 上架
- **企業級UI/UX** - Orbitron字型、科技感設計、動畫效果

### 🤖 AI與API特性
- **多API KEY輪流備援** - 某家用盡自動切換下一組
- **本地Ollama優先** - 本地推理優先，雲端API備援
- **智能快取系統** - 查詢結果自動快取，避免重複請求
- **配額管理** - 小時/日/月配額限制，友善提示
- **健康監控** - 即時API狀態、配額使用、快取狀態

### 📱 行動裝置體驗
- **一鍵完成** - 查詢、帳務、維修、派工、優惠、公告、健康檢查
- **自動驗證** - App啟動時自動檢查API金鑰、健康狀態、公告
- **權限分級** - 行動端權限管理，UI自適應
- **行為記錄** - 同步後台，完整追蹤

### 🏢 企業後台
- **全模組管理** - 公告、帳務、流量、優惠、員工、維修、推播
- **跨平台同步** - Web/APP後台同等功能，差異化UI
- **即時監控** - 系統健康、API狀態、配額使用、快取狀態

### 🔔 推播與通知
- **即時推播** - 維修預約、推播消息、優惠到期提醒
- **離線支援** - Service Worker快取，離線時仍可查看歷史
- **背景同步** - 網路恢復時自動同步

## 📦 快速開始

### 環境需求
- Node.js 18+ / Python 3.8+
- Ollama (可選，本地AI推理)
- 現代瀏覽器 (支援PWA)

### 1. 後端啟動
```bash
# 安裝依賴
pip install -r requirements.txt

# 配置環境變數
cp env_example.txt .env
# 編輯 .env 檔案，填入API金鑰

# 啟動後端服務
python app.py
```

### 2. 前端啟動
```bash
cd gas-ai-frontend

# 安裝依賴
npm install

# 啟動開發服務器
npm start
```

### 3. 訪問系統
- **Web版**: http://localhost:3000
- **後端API**: http://localhost:8600
- **API文檔**: http://localhost:8600/api_doc

## 📱 App模式部署

### PWA模式 (推薦)
1. **自動安裝提示** - 瀏覽器會自動提示「加入主畫面」
2. **手動安裝** - 點擊地址欄的安裝圖標
3. **離線使用** - 安裝後支援離線查看歷史記錄

### Capacitor原生App (Android/iOS)
```bash
# 安裝Capacitor
npm install @capacitor/core @capacitor/cli
npm install @capacitor/android @capacitor/ios

# 初始化Capacitor
npx cap init "智慧瓦斯AI" "com.jytech.gasai"

# 建置React應用
npm run build

# 添加平台
npx cap add android
npx cap add ios

# 同步代碼
npx cap sync

# 打開IDE
npx cap open android  # Android Studio
npx cap open ios      # Xcode
```

### Tauri桌面App (Windows/macOS/Linux)
```bash
# 安裝Tauri CLI
npm install -g @tauri-apps/cli

# 初始化Tauri
npm run tauri init

# 建置並運行
npm run tauri dev

# 建置發布版
npm run tauri build
```

### React Native (跨平台)
```bash
# 安裝React Native CLI
npm install -g react-native-cli

# 創建新專案
npx react-native init GasAIApp --template react-native-template-typescript

# 複製現有組件到新專案
# 修改API端點為實際後端地址
```

## 🏪 應用商店上架

### Google Play Store (Android)
1. **建置APK/AAB**
   ```bash
   npx cap build android --release
   ```
2. **簽名APK**
   ```bash
   jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my-release-key.keystore app-release-unsigned.apk alias_name
   ```
3. **上傳Google Play Console**
   - 創建開發者帳號
   - 上傳APK/AAB檔案
   - 填寫應用資訊、截圖、描述
   - 提交審核

### Apple App Store (iOS)
1. **建置IPA**
   ```bash
   npx cap build ios --release
   ```
2. **使用Xcode建置**
   - 打開 `ios/App.xcworkspace`
   - 選擇Release配置
   - Product → Archive
3. **上傳App Store Connect**
   - 創建開發者帳號
   - 使用Xcode或Application Loader上傳
   - 填寫應用資訊、截圖、描述
   - 提交審核

### Microsoft Store (Windows)
1. **建置MSIX**
   ```bash
   npm run tauri build
   ```
2. **使用Microsoft Partner Center**
   - 創建開發者帳號
   - 上傳MSIX檔案
   - 填寫應用資訊
   - 提交審核

## ⚙️ 配置說明

### 環境變數配置
```bash
# .env 檔案範例
GEMINI_API_KEY_1=your_gemini_key_1
GEMINI_API_KEY_2=your_gemini_key_2
OPENAI_API_KEY_1=your_openai_key_1
DEEPSEEK_API_KEY_1=your_deepseek_key_1

# Ollama配置
OLLAMA_URL=http://localhost:11434

# 快取配置
CACHE_ENABLED=true
CACHE_TTL=3600
CACHE_MAX_SIZE=1000

# 配額配置
QUOTA_ENABLED=true
QUOTA_HOURLY=100
QUOTA_DAILY=1000
QUOTA_MONTHLY=10000

# 管理員帳號
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
```

### API端點配置
```javascript
// gas-ai-frontend/src/config.js
export const API_URL = process.env.REACT_APP_API_URL || "/ai_ask";
export const HEALTH_URL = process.env.REACT_APP_HEALTH_URL || "/health";
// ... 其他端點
```

## 🔧 開發指南

### 新增API KEY
1. 在 `config.py` 的 `GEMINI_API_KEYS` 陣列中添加新KEY
2. 系統會自動輪流使用所有可用KEY
3. 某個KEY用盡時自動切換到下一個

### 新增AI模型
1. 在 `config.py` 的 `OLLAMA_MODELS` 中添加模型名稱
2. 在 `app.py` 的 `get_available_apis()` 中註冊新模型
3. 實現對應的API調用函數

### 自定義UI主題
```css
/* gas-ai-frontend/src/index.css */
:root {
  --primary-color: #2676ff;
  --secondary-color: #ff9800;
  --font-family: 'Orbitron', 'Noto Sans TC', '微軟正黑體';
}
```

## 📊 監控與維護

### 健康檢查
- **API**: `GET /health` - 完整系統狀態
- **配額**: `GET /quota` - 配額使用情況
- **快取**: `GET /cache/status` - 快取狀態

### 日誌監控
```bash
# 查看後端日誌
tail -f app.log

# 查看錯誤日誌
grep ERROR app.log
```

### 性能優化
- **快取清理**: `POST /cache/clear` (需管理員權限)
- **配額重置**: 自動按小時/日/月重置
- **API輪流**: 自動負載均衡

## 🛡️ 安全考量

### 生產環境部署
1. **HTTPS強制**: 所有API端點使用HTTPS
2. **API金鑰保護**: 使用環境變數，不在代碼中硬編碼
3. **CORS配置**: 限制允許的域名
4. **速率限制**: 防止API濫用

### 權限管理
- **管理員**: 完整系統管理權限
- **一般用戶**: 查詢和歷史記錄權限
- **API訪問**: 基於配額的訪問控制

## 📞 支援與聯繫

### 技術支援
- **開發團隊**: Jy技術團隊
- **聯繫方式**: [your-email@example.com]
- **文檔**: [https://your-docs-url.com]

### 常見問題
1. **PWA無法安裝**: 確保使用HTTPS或localhost
2. **API調用失敗**: 檢查網路連線和API金鑰
3. **配額用盡**: 等待重置或聯繫管理員
4. **離線功能**: 僅支援查看歷史記錄

## 📄 授權條款

MIT License - 詳見 [LICENSE](LICENSE) 檔案

## 後端AI管理系統架構與API設計（2024/06/25自動優化）

### 目標
- 所有業務模組（帳務、成本、派工、維修、FAQ、合約、活動、優惠、設備、員工）皆有獨立API，並支援自然語言查詢
- 所有AI查詢、業務查詢、FAQ等均經AI Router語意分流，回應標準格式
- 嚴格登入/權限分級控管，未登入一律拒絕
- 日誌、查詢歷史、API用量統一後端管理
- 健康檢查、用量警示、API金鑰安全管理
- 預留多模型/新模組擴充能力

### 主要結構
- app.py：主Flask應用，註冊所有API路由
- config.py：設定、金鑰、權限、模組定義
- ai_router.py：AI中樞分流/語意分析/模組分派
- auth.py：登入、session驗證、權限控管
- logging_utils.py：日誌與查詢歷史管理
- modules/：各業務模組API（accounting, cost, dispatch, ...）

### 權限分級
- 管理員/會計/維修/派工/業務/主管/工程等
- 每個API可自訂可用權限

### AI分流與回應
- /api/ai_ask：自然語言查詢自動分流到對應業務模組
- 各模組API支援自然語言查詢，AI能針對每張卡片給出最適合的答案
- 回應格式統一，標示ai_model

### 日誌/查詢歷史/用量
- 所有查詢、用戶、API用量統一後端管理
- 可查詢歷史、API用量、用戶行為

### 健康檢查/用量警示
- /api/health：API健康狀態、用量、金鑰狀態
- 用量達警戒自動警示

### API金鑰安全
- 所有AI金鑰僅後端管理，前端無法取得

### 擴充能力
- 可隨時新增新業務模組、新AI模型

### API回應格式規範
- 所有API回應HTTP Status永遠為200
- 錯誤、權限不足、資料異常等皆於response JSON內結構化呈現
- 標準格式：
```json
{
  "success": true/false,
  "code": 0/非零,
  "data": {...},
  "error": {"msg": "...", "details": "...", "suggestion": "..."}
}
```
- 所有異常自動日誌，並於error.suggestion給出修正建議

---

**智慧瓦斯 AI 管理系統 v2.0.0**  
*Jy技術團隊 - 專業瓦斯行管理AI助手* #   g p s a i  
 