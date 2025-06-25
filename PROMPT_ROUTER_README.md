# 智慧瓦斯 AI 管理系統 - Ollama Prompt Router

專業級本地多模型分流 API，整合智慧瓦斯提示詞集，支援自動模型選擇、系統提示詞優化、高可用架構。

## 🚀 功能特色

- **智能模組識別**：自動識別查詢意圖（帳務、成本、派工、維修、FAQ、合約）
- **多模型分流**：根據查詢類型自動選擇最適合的模型
- **專業提示詞**：整合智慧瓦斯行業專業知識
- **高可用架構**：模型健康檢查、自動降級、快取機制
- **RESTful API**：完整的 Web API 接口
- **Web 界面**：美觀的測試界面

## 📋 支援模組

| 模組 | 關鍵字 | 推薦模型 | 功能描述 |
|------|--------|----------|----------|
| 帳務 | 欠款、月結、帳款、已收、未收、查帳 | deepseek-r1:8b | 客戶應收帳款查詢與分析 |
| 成本 | 利潤、成本、裝瓶、損耗、退桶、產能 | qwen3:32b | 成本計算與利潤分析 |
| 派工 | 司機、派工、任務、安排、分配、桶子 | llama3:8b-instruct-q4_0 | 派工路線優化與管理 |
| 維修 | 報修、維修、型號、安檢、設備、故障 | qwen3:32b | 設備維修分析與安排 |
| FAQ | 合約、優惠、價格、政策、知識庫 | deepseek-r1:8b | 客戶服務與問題解答 |
| 合約 | 合約、條款、解約、違約金、續約 | deepseek-r1:8b | 合約管理與法律諮詢 |

## 🛠️ 安裝與設定

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 啟動 Ollama 服務

確保 Ollama 已安裝並運行：

```bash
# 安裝模型（根據需要選擇）
ollama pull deepseek-r1:8b
ollama pull qwen3:32b
ollama pull llama3:8b-instruct-q4_0
```

### 3. 啟動 Prompt Router

```bash
python prompt_router.py
```

服務將在 `http://localhost:8600` 啟動。

## 📚 API 使用

### 1. 單一查詢

```bash
curl -X POST http://localhost:8600/ai_ask \
  -H "Content-Type: application/json" \
  -d '{"q": "幫我查王小明現在欠多少錢？"}'
```

回應範例：
```json
{
  "success": true,
  "module": "帳務",
  "model": "deepseek-r1:8b",
  "reply": "根據查詢，我來幫您分析王小明的帳務狀況...",
  "processing_time": 2.34,
  "timestamp": "2024-01-15T10:30:00",
  "cached": false
}
```

### 2. 批量查詢

```bash
curl -X POST http://localhost:8600/batch_ask \
  -H "Content-Type: application/json" \
  -d '{
    "queries": [
      "幫我查王小明現在欠多少錢？",
      "最近利潤下降原因是什麼？",
      "今天哪個司機任務最多？"
    ]
  }'
```

### 3. 健康檢查

```bash
curl http://localhost:8600/health
```

### 4. 快取管理

```bash
# 查看快取統計
curl http://localhost:8600/cache/stats

# 清除快取
curl -X DELETE http://localhost:8600/cache/clear
```

## 🌐 Web 界面

啟動服務後，在瀏覽器中打開 `web_interface.html` 文件，即可使用美觀的 Web 界面進行測試。

功能包括：
- 即時查詢測試
- 系統狀態監控
- 快取管理
- 範例查詢
- 結果歷史記錄

## 🔧 自定義配置

### 1. 修改模型配置

在 `prompt_router.py` 中修改 `get_best_model` 方法：

```python
def get_best_model(self, module: str) -> str:
    model_configs = {
        "帳務": ["your-model-1", "your-model-2", "llama3:8b-instruct-q4_0"],
        "成本": ["your-model-3", "your-model-4", "llama3:8b-instruct-q4_0"],
        # ... 其他模組
    }
```

### 2. 添加新模組

1. 在 `system_prompts` 中添加新的系統提示詞
2. 在 `detect_module` 方法中添加關鍵字映射
3. 在 `get_best_model` 方法中添加模型配置

### 3. 調整快取設定

```python
self.cache_ttl = 3600  # 快取時間（秒）
```

## 🧪 測試

### 1. 運行測試腳本

```bash
python test_prompt_router.py
```

### 2. 測試範例查詢

```python
import requests

# 帳務查詢
response = requests.post("http://localhost:8600/ai_ask", 
    json={"q": "幫我查王小明現在欠多少錢？"})

# 成本分析
response = requests.post("http://localhost:8600/ai_ask", 
    json={"q": "最近利潤下降原因是什麼？"})

# 派工管理
response = requests.post("http://localhost:8600/ai_ask", 
    json={"q": "今天哪個司機任務最多？"})

# 維修管理
response = requests.post("http://localhost:8600/ai_ask", 
    json={"q": "JY-500型號最近報修率怎樣？"})
```

## 📊 監控與日誌

### 1. 系統日誌

服務會自動記錄：
- 查詢處理日誌
- 模型健康檢查日誌
- 錯誤和異常日誌

### 2. 效能監控

- 查詢處理時間
- 快取命中率
- 模型使用統計
- 系統健康狀態

## 🔒 安全考量

- 本地部署，資料不外洩
- 可配置 API 認證
- 輸入驗證和清理
- 錯誤處理和日誌記錄

## 🚀 進階功能

### 1. 模型健康檢查

系統會定期檢查所有模型的健康狀態，自動選擇可用的模型。

### 2. 智能降級

當首選模型不可用時，自動降級到備用模型。

### 3. 快取優化

相同查詢會使用快取結果，提升回應速度。

### 4. 批量處理

支援批量查詢，提升處理效率。

## 🔄 擴展建議

1. **資料庫整合**：連接實際的客戶、帳務資料
2. **RAG 知識庫**：整合 FAQ、合約條款等知識庫
3. **通知系統**：整合 LINE Notify、Email 通知
4. **前端優化**：使用 Vue/React 開發更豐富的界面
5. **容器化部署**：使用 Docker 進行部署

## 📞 支援

如有問題或建議，請：
1. 檢查 Ollama 服務是否正常運行
2. 確認模型是否已正確安裝
3. 查看系統日誌了解詳細錯誤信息
4. 聯繫開發團隊

---

*智慧瓦斯 AI 管理系統 - 讓瓦斯行管理更智能、更高效！* 