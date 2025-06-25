#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧瓦斯 AI 管理系統
專為瓦斯行 ERP 設計的 AI 輔助決策系統
"""

import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import asyncio
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Customer:
    """客戶資料結構"""
    id: int
    name: str
    phone: str
    address: str
    credit_limit: float
    payment_terms: str
    created_at: datetime

@dataclass
class AccountReceivable:
    """應收帳款結構"""
    id: int
    customer_id: int
    amount: float
    due_date: datetime
    status: str
    created_at: datetime

class PromptTemplate:
    """提示詞模板管理"""
    
    def __init__(self):
        self.templates = {
            'accounting': {
                'balance_check': "你是一個瓦斯行帳務管理專家。請查詢客戶 {customer_name} 的應收帳款狀況，包括：\n1. 總欠款金額\n2. 逾期天數\n3. 最近付款紀錄\n4. 信用風險評估",
                'credit_analysis': "分析客戶 {customer_name} 的信用風險，考慮以下因素：\n1. 付款歷史\n2. 回購頻率\n3. 欠款金額\n4. 建議是否轉為月結客戶",
                'overdue_list': "列出超過 {days} 天未收款的客戶，按逾期天數排序，並提供催收建議"
            },
            'cost_analysis': {
                'cost_calculation': "計算 {period} 期間的平均每桶瓦斯成本，包括：\n1. 進貨成本\n2. 運輸成本\n3. 人工成本\n4. 設備折舊\n5. 其他營運成本",
                'profit_analysis': "分析 {period} 期間的利潤變化原因，重點關注：\n1. 成本上升因素\n2. 銷售量變化\n3. 價格調整影響\n4. 效率指標",
                'trend_prediction': "基於歷史數據預測未來 {months} 個月的成本趨勢，考慮季節性因素和市場變化"
            },
            'dispatch': {
                'task_optimization': "優化 {date} 的派工安排，考慮：\n1. 員工位置和可用性\n2. 客戶位置和需求\n3. 瓦斯桶庫存\n4. 交通狀況\n5. 時間窗限制",
                'employee_performance': "分析員工 {employee_name} 的派工效率，包括：\n1. 完成任務數量\n2. 平均用時\n3. 客戶滿意度\n4. 成本效益"
            },
            'maintenance': {
                'equipment_analysis': "分析設備 {equipment_model} 的維修狀況：\n1. 故障頻率\n2. 維修成本\n3. 使用壽命預測\n4. 更換建議",
                'maintenance_schedule': "安排 {location} 地區的維修任務：\n1. 可用技師\n2. 設備狀況\n3. 客戶需求\n4. 優先級排序"
            }
        }
    
    def get_prompt(self, module: str, action: str, **kwargs) -> str:
        """獲取格式化的提示詞"""
        if module not in self.templates or action not in self.templates[module]:
            raise ValueError(f"未找到模組 {module} 的動作 {action}")
        
        template = self.templates[module][action]
        return template.format(**kwargs)

class AICache:
    """AI 回應快取系統"""
    
    def __init__(self, ttl: int = 3600):
        self.cache = {}
        self.ttl = ttl
    
    def get_cached_response(self, query_hash: str) -> Optional[str]:
        """獲取快取的回應"""
        if query_hash in self.cache:
            cached = self.cache[query_hash]
            if time.time() - cached['timestamp'] < self.ttl:
                logger.info(f"使用快取回應: {query_hash}")
                return cached['response']
            else:
                del self.cache[query_hash]
        return None
    
    def cache_response(self, query_hash: str, response: str):
        """快取回應"""
        self.cache[query_hash] = {
            'response': response,
            'timestamp': time.time()
        }
        logger.info(f"快取回應: {query_hash}")

class BaseAIModule:
    """AI 模組基礎類別"""
    
    def __init__(self, system_prompt: str, cache: AICache):
        self.system_prompt = system_prompt
        self.cache = cache
        self.context = []
    
    def process(self, user_input: str, **kwargs) -> Dict[str, Any]:
        """處理用戶查詢"""
        # 生成查詢雜湊
        query_hash = self._generate_query_hash(user_input, kwargs)
        
        # 檢查快取
        cached_response = self.cache.get_cached_response(query_hash)
        if cached_response:
            return json.loads(cached_response)
        
        # 構建完整提示詞
        full_prompt = self.build_prompt(user_input, **kwargs)
        
        # 調用 AI API (模擬)
        response = self.call_ai_api(full_prompt)
        
        # 後處理回應
        processed_response = self.post_process(response)
        
        # 快取回應
        self.cache.cache_response(query_hash, json.dumps(processed_response))
        
        return processed_response
    
    def build_prompt(self, user_input: str, **kwargs) -> str:
        """構建完整提示詞"""
        return f"""
{self.system_prompt}

用戶查詢: {user_input}

請根據以上系統設定，提供詳細的分析和建議。回應格式應包含：
1. 分析結果
2. 具體數據
3. 建議行動
4. 風險提醒
"""
    
    def call_ai_api(self, prompt: str) -> str:
        """調用 AI API (模擬實現)"""
        # 這裡應該調用實際的 AI API (OpenAI, Claude, DeepSeek 等)
        # 目前使用模擬回應
        return f"AI 分析結果: {prompt[:100]}..."
    
    def post_process(self, response: str) -> Dict[str, Any]:
        """後處理 AI 回應"""
        return {
            'type': 'ai_response',
            'content': response,
            'timestamp': datetime.now().isoformat(),
            'module': self.__class__.__name__
        }
    
    def _generate_query_hash(self, user_input: str, kwargs: Dict) -> str:
        """生成查詢雜湊"""
        query_str = f"{user_input}:{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(query_str.encode()).hexdigest()

class AccountingModule(BaseAIModule):
    """客戶帳務 AI 模組"""
    
    def __init__(self, cache: AICache):
        system_prompt = """
你是一個專業的瓦斯行帳務管理 AI 助手，專門處理：
- 客戶應收帳款查詢
- 信用風險評估
- 逾期帳款管理
- 付款建議
- 財務報表分析

請提供準確、實用的財務分析和建議。
"""
        super().__init__(system_prompt, cache)
    
    def check_customer_balance(self, customer_name: str) -> Dict[str, Any]:
        """查詢客戶欠款"""
        return self.process(f"查詢客戶 {customer_name} 的欠款狀況")
    
    def analyze_credit_risk(self, customer_name: str) -> Dict[str, Any]:
        """分析客戶信用風險"""
        return self.process(f"分析客戶 {customer_name} 的信用風險")
    
    def get_overdue_customers(self, days: int = 30) -> Dict[str, Any]:
        """獲取逾期客戶列表"""
        return self.process(f"列出超過 {days} 天未收款的客戶")

class CostAnalysisModule(BaseAIModule):
    """成本分析 AI 模組"""
    
    def __init__(self, cache: AICache):
        system_prompt = """
你是一個專業的瓦斯行成本分析 AI 助手，專門處理：
- 成本計算與分析
- 利潤趨勢分析
- 成本預測
- 效率優化建議
- 投資報酬率分析

請提供深入的財務分析和實用建議。
"""
        super().__init__(system_prompt, cache)
    
    def calculate_cost_per_cylinder(self, period: str) -> Dict[str, Any]:
        """計算每桶瓦斯成本"""
        return self.process(f"計算 {period} 期間的平均每桶瓦斯成本")
    
    def analyze_profit_trend(self, period: str) -> Dict[str, Any]:
        """分析利潤趨勢"""
        return self.process(f"分析 {period} 期間的利潤變化原因")
    
    def predict_cost_trend(self, months: int) -> Dict[str, Any]:
        """預測成本趨勢"""
        return self.process(f"預測未來 {months} 個月的成本趨勢")

class DispatchModule(BaseAIModule):
    """派工管理 AI 模組"""
    
    def __init__(self, cache: AICache):
        system_prompt = """
你是一個專業的瓦斯行派工管理 AI 助手，專門處理：
- 派工路線優化
- 員工效能分析
- 任務分配建議
- 時間管理優化
- 成本效益分析

請提供實用的派工建議和效率提升方案。
"""
        super().__init__(system_prompt, cache)
    
    def optimize_dispatch(self, date: str) -> Dict[str, Any]:
        """優化派工安排"""
        return self.process(f"優化 {date} 的派工安排")
    
    def analyze_employee_performance(self, employee_name: str) -> Dict[str, Any]:
        """分析員工效能"""
        return self.process(f"分析員工 {employee_name} 的派工效率")

class MaintenanceModule(BaseAIModule):
    """維修管理 AI 模組"""
    
    def __init__(self, cache: AICache):
        system_prompt = """
你是一個專業的瓦斯行維修管理 AI 助手，專門處理：
- 設備維修分析
- 維護排程安排
- 安全檢查提醒
- 設備壽命預測
- 維修成本分析

請提供專業的維修建議和安全提醒。
"""
        super().__init__(system_prompt, cache)
    
    def analyze_equipment(self, equipment_model: str) -> Dict[str, Any]:
        """分析設備狀況"""
        return self.process(f"分析設備 {equipment_model} 的維修狀況")
    
    def schedule_maintenance(self, location: str) -> Dict[str, Any]:
        """安排維修任務"""
        return self.process(f"安排 {location} 地區的維修任務")

class PromptRouter:
    """AI 提示詞路由器"""
    
    def __init__(self):
        self.cache = AICache()
        self.modules = {
            'accounting': AccountingModule(self.cache),
            'cost_analysis': CostAnalysisModule(self.cache),
            'dispatch': DispatchModule(self.cache),
            'maintenance': MaintenanceModule(self.cache)
        }
        self.prompt_templates = PromptTemplate()
    
    def route_query(self, user_input: str) -> Dict[str, Any]:
        """路由用戶查詢到對應模組"""
        # 簡單的意圖識別 (實際應用中應使用更複雜的 NLP)
        intent = self.classify_intent(user_input)
        
        if intent in self.modules:
            return self.modules[intent].process(user_input)
        else:
            return {
                'type': 'error',
                'message': f'無法識別查詢意圖: {user_input}',
                'suggestions': ['請嘗試更明確的描述', '或聯繫系統管理員']
            }
    
    def classify_intent(self, user_input: str) -> str:
        """分類用戶查詢意圖"""
        user_input_lower = user_input.lower()
        
        # 帳務相關關鍵字
        if any(word in user_input_lower for word in ['欠款', '帳款', '付款', '信用', '逾期', '對帳', '欠多少錢', '欠錢']):
            return 'accounting'
        
        # 成本相關關鍵字
        elif any(word in user_input_lower for word in ['成本', '利潤', '價格', '費用', '預算', '下降', '上升', '趨勢']):
            return 'cost_analysis'
        
        # 派工相關關鍵字
        elif any(word in user_input_lower for word in ['派工', '司機', '路線', '配送', '員工', '任務', '最多']):
            return 'dispatch'
        
        # 維修相關關鍵字
        elif any(word in user_input_lower for word in ['維修', '設備', '安檢', '故障', '保養', '報修', '型號', '安排']):
            return 'maintenance'
        
        else:
            return 'unknown'

class GasAISystem:
    """智慧瓦斯 AI 管理系統主類別"""
    
    def __init__(self):
        self.router = PromptRouter()
        self.logger = logging.getLogger(__name__)
    
    def process_query(self, user_input: str) -> Dict[str, Any]:
        """處理用戶查詢"""
        try:
            self.logger.info(f"處理查詢: {user_input}")
            result = self.router.route_query(user_input)
            self.logger.info(f"查詢完成: {result.get('type', 'unknown')}")
            return result
        except Exception as e:
            self.logger.error(f"處理查詢時發生錯誤: {e}")
            return {
                'type': 'error',
                'message': f'系統錯誤: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        return {
            'status': 'running',
            'modules': list(self.router.modules.keys()),
            'cache_size': len(self.router.cache.cache),
            'timestamp': datetime.now().isoformat()
        }

# 使用範例
def main():
    """主函數 - 使用範例"""
    # 初始化系統
    ai_system = GasAISystem()
    
    # 測試查詢
    test_queries = [
        "幫我查王小明現在欠多少錢？",
        "最近利潤下降原因是什麼？",
        "幫我安排週三下午台東的維修任務",
        "今天哪個司機任務最多？",
        "JY-500型號最近報修率怎樣？"
    ]
    
    print("=== 智慧瓦斯 AI 管理系統測試 ===\n")
    
    for query in test_queries:
        print(f"查詢: {query}")
        result = ai_system.process_query(query)
        print(f"結果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        print("-" * 50)
    
    # 顯示系統狀態
    print("\n=== 系統狀態 ===")
    status = ai_system.get_system_status()
    print(json.dumps(status, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main() 