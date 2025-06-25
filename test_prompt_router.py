#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧瓦斯 AI 管理系統 - Prompt Router 測試腳本
測試多模型分流、模組識別、API 功能
"""

import requests
import json
import time
from datetime import datetime

# API 配置
API_BASE = "http://localhost:8600"

def test_single_query(query: str):
    """測試單一查詢"""
    print(f"\n🔍 測試查詢: {query}")
    print("-" * 50)
    
    try:
        response = requests.post(
            f"{API_BASE}/ai_ask",
            json={"q": query},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 成功")
            print(f"📊 模組: {result.get('module', 'N/A')}")
            print(f"🤖 模型: {result.get('model', 'N/A')}")
            print(f"⏱️  處理時間: {result.get('processing_time', 0):.2f}秒")
            print(f"💾 快取: {'是' if result.get('cached', False) else '否'}")
            print(f"📝 回應: {result.get('reply', 'N/A')[:200]}...")
        else:
            print(f"❌ 錯誤: {response.status_code}")
            print(f"📄 回應: {response.text}")
            
    except Exception as e:
        print(f"❌ 請求失敗: {e}")

def test_batch_queries(queries: list):
    """測試批量查詢"""
    print(f"\n🔄 批量測試 {len(queries)} 個查詢")
    print("=" * 60)
    
    try:
        response = requests.post(
            f"{API_BASE}/batch_ask",
            json={"queries": queries},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 批量查詢成功")
            print(f"📊 總查詢數: {result.get('total_queries', 0)}")
            
            for i, item in enumerate(result.get('results', []), 1):
                print(f"\n{i}. {item.get('query', 'N/A')}")
                print(f"   模組: {item.get('module', 'N/A')}")
                print(f"   模型: {item.get('model', 'N/A')}")
                print(f"   回應: {item.get('reply', 'N/A')[:100]}...")
        else:
            print(f"❌ 錯誤: {response.status_code}")
            print(f"📄 回應: {response.text}")
            
    except Exception as e:
        print(f"❌ 批量請求失敗: {e}")

def test_health_check():
    """測試健康檢查"""
    print("\n🏥 健康檢查")
    print("-" * 30)
    
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 系統狀態: {result.get('status', 'N/A')}")
            print(f"📊 快取大小: {result.get('cache_size', 0)}")
            print(f"🤖 模型狀態: {result.get('models', {})}")
        else:
            print(f"❌ 健康檢查失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 健康檢查請求失敗: {e}")

def test_cache_stats():
    """測試快取統計"""
    print("\n💾 快取統計")
    print("-" * 30)
    
    try:
        response = requests.get(f"{API_BASE}/cache/stats", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"📊 快取大小: {result.get('cache_size', 0)}")
            print(f"⏰ TTL: {result.get('cache_ttl', 0)}秒")
        else:
            print(f"❌ 快取統計失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 快取統計請求失敗: {e}")

def test_models():
    """測試模型列表"""
    print("\n🤖 可用模型")
    print("-" * 30)
    
    try:
        response = requests.get(f"{API_BASE}/models", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"📋 模型列表: {result.get('models', [])}")
            print(f"🏥 健康狀態: {result.get('health_status', {})}")
        else:
            print(f"❌ 模型列表失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 模型列表請求失敗: {e}")

def main():
    """主測試函數"""
    print("=== 智慧瓦斯 AI 管理系統 - Prompt Router 測試 ===")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 檢查服務是否運行
    try:
        response = requests.get(f"{API_BASE}/", timeout=5)
        if response.status_code != 200:
            print("❌ Prompt Router 服務未運行，請先啟動服務：")
            print("   python prompt_router.py")
            return
    except Exception as e:
        print("❌ 無法連接到 Prompt Router 服務")
        print("請確保服務正在運行：python prompt_router.py")
        return
    
    # 測試健康檢查
    test_health_check()
    
    # 測試模型列表
    test_models()
    
    # 測試快取統計
    test_cache_stats()
    
    # 測試各種查詢類型
    test_queries = [
        # 帳務相關
        "幫我查王小明現在欠多少錢？",
        "這個月應收帳款回收率如何？",
        "列出所有30天以上未收的客戶",
        
        # 成本相關
        "最近利潤下降原因是什麼？",
        "請幫我計算上週平均每桶瓦斯的裝瓶成本",
        "分裝廠效能是否下降？",
        
        # 派工相關
        "今天哪個司機任務最多？",
        "幫我優化明天的派工路線",
        "哪位員工近一週平均用時最久？",
        
        # 維修相關
        "JY-500型號最近報修率怎樣？",
        "幫我安排週三下午台東的維修任務",
        "哪些客戶超過1年沒做安檢？",
        
        # FAQ相關
        "為什麼這桶瓦斯變貴了？",
        "請問安檢多久要做一次？",
        "合約可以提早解約嗎？"
    ]
    
    # 單一查詢測試
    print("\n🧪 單一查詢測試")
    print("=" * 60)
    
    for query in test_queries[:6]:  # 測試前6個查詢
        test_single_query(query)
        time.sleep(1)  # 避免請求過於頻繁
    
    # 批量查詢測試
    print("\n🔄 批量查詢測試")
    print("=" * 60)
    
    batch_queries = [
        "幫我查王小明現在欠多少錢？",
        "最近利潤下降原因是什麼？",
        "今天哪個司機任務最多？",
        "JY-500型號最近報修率怎樣？"
    ]
    
    test_batch_queries(batch_queries)
    
    # 最終統計
    print("\n📊 測試完成")
    print("=" * 60)
    test_cache_stats()
    
    print("\n✅ 所有測試完成！")
    print("💡 提示：")
    print("   - 檢查模組識別是否正確")
    print("   - 確認模型選擇是否合理")
    print("   - 驗證回應內容是否符合預期")
    print("   - 觀察快取機制是否正常運作")

if __name__ == "__main__":
    main() 