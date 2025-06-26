#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧瓦斯 AI 管理系統 - 本地 Ollama Prompt Router
專業級多模型分流 API，整合智慧瓦斯提示詞集
支援自動模型選擇、系統提示詞優化、高可用架構
"""

import json
import logging
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
from dataclasses import dataclass
import threading
import queue

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """模型配置"""
    name: str
    url: str = "https://333d-49-158-216-180.ngrok-free.app/api/chat"
    timeout: int = 30
    max_retries: int = 3
    priority: int = 1
    is_active: bool = True

class ModelHealthChecker:
    """模型健康檢查器"""
    
    def __init__(self):
        self.health_status = {}
        self.check_interval = 60  # 60秒檢查一次
        self._start_health_check()
    
    def _start_health_check(self):
        """啟動健康檢查線程"""
        def health_check_worker():
            while True:
                self._check_all_models()
                time.sleep(self.check_interval)
        
        thread = threading.Thread(target=health_check_worker, daemon=True)
        thread.start()
    
    def _check_all_models(self):
        """檢查所有模型健康狀態"""
        for model_name in PROMPT_MODEL_MAP.values():
            try:
                response = requests.post(
                    "https://333d-49-158-216-180.ngrok-free.app/api/chat",
                    json={
                        "model": model_name,
                        "messages": [{"role": "user", "content": "ping"}]
                    },
                    timeout=5
                )
                self.health_status[model_name] = response.status_code == 200
            except Exception as e:
                logger.warning(f"模型 {model_name} 健康檢查失敗: {e}")
                self.health_status[model_name] = False
    
    def is_model_healthy(self, model_name: str) -> bool:
        """檢查模型是否健康"""
        return self.health_status.get(model_name, True)

class PromptRouter:
    """智慧瓦斯提示詞路由器"""
    
    def __init__(self):
        self.health_checker = ModelHealthChecker()
        self.cache = {}
        self.cache_ttl = 3600  # 1小時快取
        
        # 智慧瓦斯系統提示詞集
        self.system_prompts = {
            "帳務": """你是一個專業的瓦斯行帳務管理 AI 助手，專門處理：
- 客戶應收帳款查詢與分析
- 信用風險評估與建議
- 逾期帳款管理與催收策略
- 付款條件優化建議
- 財務報表分析與解讀

請提供準確、實用的財務分析和建議，並考慮瓦斯行業的特殊性。""",
            
            "成本": """你是一個專業的瓦斯行成本分析 AI 助手，專門處理：
- 瓦斯裝瓶成本計算與分析
- 利潤趨勢分析與預測
- 分裝廠效能評估
- 成本控制策略建議
- 投資報酬率分析

請提供深入的財務分析和實用建議，幫助優化營運效率。""",
            
            "派工": """你是一個專業的瓦斯行派工管理 AI 助手，專門處理：
- 派工路線優化與規劃
- 員工效能分析與評估
- 任務分配策略建議
- 時間管理優化
- 成本效益分析

請提供實用的派工建議和效率提升方案，考慮瓦斯配送的特殊需求。""",
            
            "維修": """你是一個專業的瓦斯行維修管理 AI 助手，專門處理：
- 設備維修分析與預測
- 維護排程安排與優化
- 安全檢查提醒與追蹤
- 設備壽命預測與更換建議
- 維修成本分析與控制

請提供專業的維修建議和安全提醒，確保設備安全可靠運行。""",
            
            "FAQ": """你是一個專業的瓦斯行客服 AI 助手，專門處理：
- 客戶常見問題解答
- 合約條款解釋與建議
- 優惠活動說明與推薦
- 安全使用指導
- 政策法規解讀

請提供友善、準確的客服回應，並主動提供相關建議。""",
            
            "合約": """你是一個專業的瓦斯行合約管理 AI 助手，專門處理：
- 合約條款分析與建議
- 合約風險評估
- 合約優化建議
- 法律條文解讀
- 合約談判策略

請提供專業的合約建議，確保合約條款合理且符合法規要求。"""
        }
    
    def detect_module(self, text: str) -> str:
        """檢測查詢模組"""
        text_lower = text.lower()
        
        # 模組關鍵字映射
        module_keywords = {
            "帳務": ["欠", "月結", "帳款", "已收", "未收", "查帳", "付款", "信用", "逾期", "對帳", "欠多少錢", "欠錢", "收帳"],
            "成本": ["利潤", "成本", "裝瓶", "損耗", "退桶", "產能", "價格", "費用", "預算", "下降", "上升", "趨勢", "分裝廠"],
            "派工": ["司機", "派工", "任務", "安排", "分配", "桶子", "路線", "配送", "員工", "最多", "GPS", "送貨"],
            "維修": ["報修", "維修", "型號", "安檢", "設備", "故障", "保養", "安排", "檢查", "維護"],
            "FAQ": ["合約", "優惠", "價格", "政策", "安檢多久", "知識庫", "為什麼", "如何", "請問", "多久"],
            "合約": ["合約", "條款", "解約", "違約金", "續約", "簽約", "合約內容", "法律"]
        }
        
        # 計算每個模組的匹配分數
        module_scores = {}
        for module, keywords in module_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                module_scores[module] = score
        
        # 返回分數最高的模組
        if module_scores:
            return max(module_scores, key=module_scores.get)
        
        return "FAQ"  # 預設模組
    
    def get_best_model(self, module: str) -> str:
        """獲取最佳模型"""
        # 僅允許三個模型
        model_configs = {
            "帳務": ["openchat:7b", "llama3:latest", "deepseek-r1:8b"],
            "成本": ["openchat:7b", "llama3:latest", "deepseek-r1:8b"],
            "派工": ["openchat:7b", "llama3:latest", "deepseek-r1:8b"],
            "維修": ["openchat:7b", "llama3:latest", "deepseek-r1:8b"],
            "FAQ": ["openchat:7b", "llama3:latest", "deepseek-r1:8b"],
            "合約": ["openchat:7b", "llama3:latest", "deepseek-r1:8b"]
        }
        models = model_configs.get(module, ["openchat:7b"])
        for model in models:
            if self.health_checker.is_model_healthy(model):
                return model
        return "openchat:7b"
    
    def build_prompt(self, user_input: str, module: str) -> Dict[str, Any]:
        """構建完整的提示詞"""
        system_prompt = self.system_prompts.get(module, self.system_prompts["FAQ"])
        
        # 根據模組添加特定的上下文
        context_prompts = {
            "帳務": f"\n\n用戶查詢: {user_input}\n\n請提供詳細的帳務分析，包括：\n1. 具體數據和金額\n2. 風險評估\n3. 建議行動\n4. 後續追蹤事項",
            "成本": f"\n\n用戶查詢: {user_input}\n\n請提供深入的成本分析，包括：\n1. 成本構成分析\n2. 趨勢預測\n3. 優化建議\n4. 風險提醒",
            "派工": f"\n\n用戶查詢: {user_input}\n\n請提供實用的派工建議，包括：\n1. 路線優化\n2. 人員配置\n3. 時間安排\n4. 效率提升方案",
            "維修": f"\n\n用戶查詢: {user_input}\n\n請提供專業的維修建議，包括：\n1. 問題診斷\n2. 維修方案\n3. 安全提醒\n4. 預防措施",
            "FAQ": f"\n\n用戶查詢: {user_input}\n\n請提供友善的客服回應，包括：\n1. 直接答案\n2. 相關資訊\n3. 實用建議\n4. 後續服務",
            "合約": f"\n\n用戶查詢: {user_input}\n\n請提供專業的合約建議，包括：\n1. 條款分析\n2. 風險評估\n3. 優化建議\n4. 法律提醒"
        }

        
        context = context_prompts.get(module, context_prompts["FAQ"])
        
        return {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input + context}
            ]
        }
    
    def get_cached_response(self, query_hash: str) -> Optional[Dict]:
        """獲取快取回應"""
        if query_hash in self.cache:
            cached = self.cache[query_hash]
            if time.time() - cached['timestamp'] < self.cache_ttl:
                return cached['response']
            else:
                del self.cache[query_hash]
        return None
    
    def cache_response(self, query_hash: str, response: Dict):
        """快取回應"""
        self.cache[query_hash] = {
            'response': response,
            'timestamp': time.time()
        }
    
    def process_query(self, user_input: str) -> Dict[str, Any]:
        """處理查詢"""
        start_time = time.time()
        
        # 生成查詢雜湊
        query_hash = hashlib.md5(user_input.encode()).hexdigest()
        
        # 檢查快取
        cached_response = self.get_cached_response(query_hash)
        if cached_response:
            cached_response['cached'] = True
            return cached_response
        
        # 檢測模組
        module = self.detect_module(user_input)
        
        # 選擇最佳模型
        model = self.get_best_model(module)
        
        # 構建提示詞
        prompt_data = self.build_prompt(user_input, module)
        
        # 調用 Ollama API
        try:
            payload = {
                "model": model,
                **prompt_data
            }
            
            response = requests.post(
                "https://333d-49-158-216-180.ngrok-free.app/api/chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("message", {}).get("content", "")
                
                result = {
                    "success": True,
                    "module": module,
                    "model": model,
                    "reply": ai_response,
                    "processing_time": time.time() - start_time,
                    "timestamp": datetime.now().isoformat(),
                    "cached": False
                }
                
                # 快取回應
                self.cache_response(query_hash, result)
                
                return result
            else:
                return {
                    "success": False,
                    "error": f"API 錯誤: {response.status_code}",
                    "module": module,
                    "model": model,
                    "processing_time": time.time() - start_time,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"處理查詢時發生錯誤: {e}")
            return {
                "success": False,
                "error": str(e),
                "module": module,
                "model": model,
                "processing_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }

# 初始化 Flask 應用
app = Flask(__name__)
CORS(app)  # 啟用 CORS

# 初始化路由器
router = PromptRouter()

@app.route("/", methods=["GET"])
def root():
    """根路徑"""
    return jsonify({
        "message": "智慧瓦斯 AI 管理系統 - Ollama Prompt Router",
        "version": "1.0.0",
        "status": "running",
        "modules": list(router.system_prompts.keys()),
        "timestamp": datetime.now().isoformat()
    })

@app.route("/health", methods=["GET"])
def health_check():
    """健康檢查"""
    return jsonify({
        "status": "healthy",
        "models": router.health_checker.health_status,
        "cache_size": len(router.cache),
        "timestamp": datetime.now().isoformat()
    })

@app.route("/ai_ask", methods=["POST"])
def ai_ask():
    """AI 查詢端點"""
    try:
        data = request.get_json()
        if not data or "q" not in data:
            return jsonify({
                "success": False,
                "error": "缺少查詢參數 'q'"
            }), 400
        
        user_input = data["q"].strip()
        if not user_input:
            return jsonify({
                "success": False,
                "error": "查詢內容不能為空"
            }), 400
        
        # 處理查詢
        result = router.process_query(user_input)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API 錯誤: {e}")
        return jsonify({
            "success": False,
            "error": f"系統錯誤: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route("/batch_ask", methods=["POST"])
def batch_ask():
    """批量查詢端點"""
    try:
        data = request.get_json()
        if not data or "queries" not in data:
            return jsonify({
                "success": False,
                "error": "缺少查詢列表 'queries'"
            }), 400
        
        queries = data["queries"]
        if not isinstance(queries, list) or len(queries) == 0:
            return jsonify({
                "success": False,
                "error": "查詢列表不能為空"
            }), 400
        
        if len(queries) > 10:  # 限制批量查詢數量
            return jsonify({
                "success": False,
                "error": "批量查詢數量不能超過 10 個"
            }), 400
        
        results = []
        for query in queries:
            result = router.process_query(query)
            results.append({
                "query": query,
                **result
            })
        
        return jsonify({
            "success": True,
            "results": results,
            "total_queries": len(queries),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"批量查詢錯誤: {e}")
        return jsonify({
            "success": False,
            "error": f"系統錯誤: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route("/cache/stats", methods=["GET"])
def cache_stats():
    """快取統計"""
    return jsonify({
        "cache_size": len(router.cache),
        "cache_ttl": router.cache_ttl,
        "timestamp": datetime.now().isoformat()
    })

@app.route("/cache/clear", methods=["DELETE"])
def clear_cache():
    """清除快取"""
    router.cache.clear()
    return jsonify({
        "success": True,
        "message": "快取已清除",
        "timestamp": datetime.now().isoformat()
    })

@app.route("/models", methods=["GET"])
def get_models():
    """獲取可用模型列表"""
    return jsonify({
        "models": list(set(router.health_checker.health_status.keys())),
        "health_status": router.health_checker.health_status,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    print("=== 智慧瓦斯 AI 管理系統 - Ollama Prompt Router ===")
    print("支援模組:", list(router.system_prompts.keys()))
    print("服務地址: http://localhost:8600")
    print("API 端點: /ai_ask (單一查詢), /batch_ask (批量查詢)")
    print("健康檢查: /health")
    print("=" * 60)
    
    app.run(host="0.0.0.0", port=8600, debug=True) 