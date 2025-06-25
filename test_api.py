import requests
import time

BASE_URL = 'http://localhost:8600'

def test_health():
    """測試健康檢查API"""
    print('🩺 測試健康檢查 /health ...')
    try:
        resp = requests.get(f'{BASE_URL}/health')
        print(f'狀態: {resp.status_code}')
        print(f'內容: {resp.json()}')
        print('健康檢查通過 ✅\n')
    except Exception as e:
        print(f'健康檢查失敗 ❌: {e}\n')

def test_ai_ask():
    """測試AI查詢API"""
    print('🤖 測試 AI 查詢 /ai_ask ...')
    
    # 測試各種模組的查詢
    queries = [
        # 帳務模組
        {'query': '請查詢本月帳單明細', 'expected_module': '帳務'},
        {'query': '客戶A的應收帳款狀況', 'expected_module': '帳務'},
        
        # 成本模組  
        {'query': '本月成本分析報告', 'expected_module': '成本'},
        {'query': '裝瓶成本計算', 'expected_module': '成本'},
        
        # 派工模組
        {'query': '今日派工安排', 'expected_module': '派工'},
        {'query': '司機路線規劃', 'expected_module': '派工'},
        
        # 維修模組
        {'query': '設備維修進度', 'expected_module': '維修'},
        {'query': '安檢報告查詢', 'expected_module': '維修'},
        
        # FAQ模組
        {'query': '瓦斯價格政策', 'expected_module': 'FAQ'},
        {'query': '常見問題解答', 'expected_module': 'FAQ'},
        
        # 合約模組
        {'query': '合約到期提醒', 'expected_module': '合約'},
        
        # 活動模組
        {'query': '最新促銷活動', 'expected_module': '活動'},
        
        # 優惠模組
        {'query': '會員優惠方案', 'expected_module': '優惠'},
        
        # 設備管理模組
        {'query': '設備監控狀態', 'expected_module': '設備管理'},
        
        # 員工管理模組
        {'query': '員工排班表', 'expected_module': '員工管理'},
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(queries, 1):
        query = test_case['query']
        expected = test_case['expected_module']
        
        print(f'[{i:2d}] 查詢: {query}')
        
        try:
            resp = requests.post(f'{BASE_URL}/ai_ask', json={'query': query}, timeout=30)
            
            if resp.status_code == 200:
                data = resp.json()
                actual_module = data.get('module', 'Unknown')
                answer = data.get('answer', 'No answer')
                model = data.get('model', 'Unknown')
                response_time = data.get('response_time', 0)
                
                # 檢查分流是否正確
                if actual_module == expected:
                    print(f'     ✅ 分流正確: {actual_module}')
                    success_count += 1
                else:
                    print(f'     ⚠️  分流異常: 預期[{expected}] 實際[{actual_module}]')
                
                print(f'     🤖 模型: {model}')
                print(f'     ⏱️  回應時間: {response_time}秒')
                print(f'     💡 回覆: {answer[:100]}...' if len(answer) > 100 else f'     💡 回覆: {answer}')
                
            else:
                print(f'     ❌ HTTP錯誤: {resp.status_code}')
                print(f'     📄 錯誤內容: {resp.text}')
                
        except Exception as e:
            print(f'     ❌ 請求失敗: {e}')
        
        print()
        time.sleep(1)  # 避免API請求過於頻繁
    
    print(f'📊 測試總結: {success_count}/{len(queries)} 項測試通過 ({success_count/len(queries)*100:.1f}%)')

def test_web_interface():
    """測試Web介面是否可訪問"""
    print('🌐 測試 Web 介面 / ...')
    try:
        resp = requests.get(f'{BASE_URL}/')
        if resp.status_code == 200 and '智慧瓦斯 AI' in resp.text:
            print('Web介面正常 ✅\n')
        else:
            print(f'Web介面異常 ❌: {resp.status_code}\n')
    except Exception as e:
        print(f'Web介面訪問失敗 ❌: {e}\n')

def test_api_doc():
    """測試API文檔頁面"""
    print('📚 測試 API 文檔 /api_doc ...')
    try:
        resp = requests.get(f'{BASE_URL}/api_doc')
        if resp.status_code == 200 and 'API 文檔' in resp.text:
            print('API文檔頁面正常 ✅\n')
        else:
            print(f'API文檔頁面異常 ❌: {resp.status_code}\n')
    except Exception as e:
        print(f'API文檔頁面訪問失敗 ❌: {e}\n')

def test_gemini_connection():
    """測試 Gemini API 連接"""
    print('🔗 測試 Gemini API 連接...')
    try:
        resp = requests.post(f'{BASE_URL}/ai_ask', json={'query': '請回覆 OK 表示連接正常'}, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if 'OK' in data.get('answer', ''):
                print('Gemini API 連接正常 ✅\n')
            else:
                print('Gemini API 回應異常 ⚠️\n')
        else:
            print(f'Gemini API 連接失敗 ❌: {resp.status_code}\n')
    except Exception as e:
        print(f'Gemini API 連接測試失敗 ❌: {e}\n')

if __name__ == '__main__':
    print('\n' + '='*60)
    print('🚀 智慧瓦斯 AI 管理系統 - Gemini 自動化測試')
    print('='*60)
    print(f'📡 測試目標: {BASE_URL}')
    print('🤖 AI 模型: Google Gemini 1.5 Pro')
    print('='*60 + '\n')
    
    # 依序執行測試
    test_web_interface()
    test_health()
    test_api_doc()
    test_gemini_connection()
    test_ai_ask()
    
    print('='*60)
    print('✅ 測試完成！')
    print('='*60) 