#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速測試 Prompt Router API
"""

import requests
import json

def test_api():
    """測試 API 功能"""
    base_url = "http://localhost:8600"
    
    # 測試查詢
    test_queries = [
        "幫我查王小明現在欠多少錢？",
        "最近利潤下降原因是什麼？",
        "今天哪個司機任務最多？",
        "JY-500型號最近報修率怎樣？"
    ]
    
    print("=== 智慧瓦斯 AI 管理系統 - Prompt Router 測試 ===\n")
    
    for query in test_queries:
        print(f"🔍 測試查詢: {query}")
        print("-" * 50)
        
        try:
            response = requests.post(
                f"{base_url}/ai_ask",
                json={"q": query},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 成功")
                print(f"📊 模組: {result.get('module', 'N/A')}")
                print(f"🤖 模型: {result.get('model', 'N/A')}")
                print(f"⏱️  處理時間: {result.get('processing_time', 0):.2f}秒")
                print(f"💾 快取: {'是' if result.get('cached', False) else '否'}")
                
                if result.get('success'):
                    print(f"📝 回應: {result.get('reply', 'N/A')[:100]}...")
                else:
                    print(f"❌ 錯誤: {result.get('error', 'N/A')}")
            else:
                print(f"❌ HTTP 錯誤: {response.status_code}")
                print(f"📄 回應: {response.text}")
                
        except Exception as e:
            print(f"❌ 請求失敗: {e}")
        
        print()

if __name__ == "__main__":
    test_api() 