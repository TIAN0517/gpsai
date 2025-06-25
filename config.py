#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧瓦斯 AI 管理系統 - 配置檔案
本專案目前僅支援 Google Gemini 1.5 Pro (modelVersion: gemini-1.5-pro-002)
AI API Key: AIzaSyD7bIKgCLX4A6bn8uIoNQQPon1PRCXYMA8
"""

import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# ===== 系統基本設定 =====
SYSTEM_NAME = "智慧瓦斯 AI 管理系統"
SYSTEM_VERSION = "2.0.0"
SYSTEM_DESCRIPTION = "專業瓦斯行管理AI助手 - Jy技術團隊"
PORT = int(os.getenv('PORT', 8600))

# ===== Google Gemini 1.5 Pro 專用設定 =====
# 目前僅支援 Google Gemini 1.5 Pro (modelVersion: gemini-1.5-pro-002)
# 本專案AI API Key: AIzaSyD7bIKgCLX4A6bn8uIoNQQPon1PRCXYMA8
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyD7bIKgCLX4A6bn8uIoNQQPon1PRCXYMA8')
GEMINI_MODEL = "gemini-1.5-pro"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"

# Gemini API 設定
GEMINI_CONFIG = {
    'model': GEMINI_MODEL,
    'api_key': GEMINI_API_KEY,
    'api_url': GEMINI_API_URL,
    'timeout': 30,
    'max_tokens': 2048,
    'temperature': 0.7
}

# ===== 企業品牌設定 =====
COMPANY_NAME = os.getenv('COMPANY_NAME', 'Jy技術團隊')
COMPANY_LOGO = os.getenv('COMPANY_LOGO', '''
<svg width="120" height="40" viewBox="0 0 120 40" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#00ff88;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#0088ff;stop-opacity:1" />
        </linearGradient>
    </defs>
    <text x="10" y="25" font-family="Orbitron, monospace" font-size="14" font-weight="bold" fill="url(#logoGradient)">
        Jy技術團隊
    </text>
</svg>
''')

# ===== 管理員設定 =====
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

# ===== 系統設定 =====
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
SESSION_SECRET = os.getenv('SESSION_SECRET', 'gas-ai-system-secret-key-2024')

# ===== 快取設定 =====
CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'True').lower() == 'true'
CACHE_MAX_SIZE = int(os.getenv('CACHE_MAX_SIZE', 1000))
CACHE_TTL = int(os.getenv('CACHE_TTL', 3600))  # 1小時

# ===== 配額設定 =====
QUOTA_ENABLED = os.getenv('QUOTA_ENABLED', 'True').lower() == 'true'
QUOTA_LIMITS = {
    'hourly': int(os.getenv('QUOTA_HOURLY', 100)),
    'daily': int(os.getenv('QUOTA_DAILY', 1000)),
    'monthly': int(os.getenv('QUOTA_MONTHLY', 10000))
}
QUOTA_COOLDOWN = int(os.getenv('QUOTA_COOLDOWN', 60))  # 秒

# ===== 業務模組設定 =====
MODULES = [
    {'id': 'accounting', 'name': '帳務管理', 'description': '瓦斯費計算、帳單處理、收費記錄'},
    {'id': 'cost', 'name': '成本分析', 'description': '瓦斯成本、運輸成本、營運成本分析'},
    {'id': 'dispatch', 'name': '派工管理', 'description': '瓦斯配送、派工安排、路線規劃'},
    {'id': 'maintenance', 'name': '維修服務', 'description': '瓦斯設備維修、安全檢查、故障排除'},
    {'id': 'faq', 'name': '常見問題', 'description': '瓦斯使用、安全知識、服務說明'},
    {'id': 'contracts', 'name': '合約管理', 'description': '客戶合約、服務條款、續約提醒'},
    {'id': 'promotions', 'name': '促銷活動', 'description': '優惠方案、活動推廣、客戶回饋'},
    {'id': 'equipment', 'name': '設備管理', 'description': '瓦斯桶、設備登記、檢驗記錄'},
    {'id': 'staff', 'name': '員工管理', 'description': '員工資料、排班安排、績效考核'}
]

MODULE_CATEGORIES = {
    '業務管理': ['accounting', 'cost', 'dispatch'],
    '服務支援': ['maintenance', 'faq', 'contracts'],
    '營運管理': ['promotions', 'equipment', 'staff']
}

# ===== 關鍵字分流設定 =====
KEYWORDS = {
    'accounting': ['帳務', '帳單', '收費', '瓦斯費', '計費', '付款', '發票', '收據'],
    'cost': ['成本', '費用', '價格', '報價', '預算', '支出', '開銷', '財務'],
    'dispatch': ['派工', '配送', '送貨', '路線', '司機', '車輛', '排程', '運送'],
    'maintenance': ['維修', '保養', '檢查', '故障', '安全', '設備', '技術', '服務'],
    'faq': ['問題', '疑問', '說明', '如何', '為什麼', '怎麼辦', '常見', 'FAQ'],
    'contracts': ['合約', '合約', '條款', '續約', '簽約', '解約', '服務', '協議'],
    'promotions': ['促銷', '優惠', '活動', '折扣', '回饋', '贈品', '特價', '推廣'],
    'equipment': ['設備', '瓦斯桶', '檢驗', '登記', '器材', '工具', '儀器'],
    'staff': ['員工', '人員', '排班', '績效', '薪資', '培訓', '人事', '管理']
}

# ===== 系統提示詞 =====
SYSTEM_PROMPTS = {
    'DEFAULT': '''您是智慧瓦斯AI管理系統的專業助理，專門協助瓦斯行業務管理。
請用繁體中文詳細回答，並提供專業、友善、實用的建議。
回答時請考慮瓦斯行業的特殊性，包含安全、法規、客戶服務等面向。''',
    
    'accounting': '''您是專業的瓦斯行帳務管理助理。
請協助處理瓦斯費計算、帳單處理、收費記錄等相關問題。
回答時請提供準確的計算方式、收費標準、帳務流程等專業建議。''',
    
    'cost': '''您是專業的瓦斯行成本分析助理。
請協助分析瓦斯成本、運輸成本、營運成本等相關問題。
回答時請提供詳細的成本結構、節省建議、財務分析等專業意見。''',
    
    'dispatch': '''您是專業的瓦斯行派工管理助理。
請協助處理瓦斯配送、派工安排、路線規劃等相關問題。
回答時請提供效率優化、安全考量、客戶服務等專業建議。''',
    
    'maintenance': '''您是專業的瓦斯行維修服務助理。
請協助處理瓦斯設備維修、安全檢查、故障排除等相關問題。
回答時請強調安全第一、專業技術、服務品質等重點。''',
    
    'faq': '''您是專業的瓦斯行客服助理。
請協助回答瓦斯使用、安全知識、服務說明等常見問題。
回答時請提供清楚、易懂、實用的說明，並注意安全提醒。''',
    
    'contracts': '''您是專業的瓦斯行合約管理助理。
請協助處理客戶合約、服務條款、續約提醒等相關問題。
回答時請提供合約要點、權益保障、服務承諾等專業建議。''',
    
    'promotions': '''您是專業的瓦斯行促銷活動助理。
請協助規劃優惠方案、活動推廣、客戶回饋等相關問題。
回答時請提供吸引客戶、提升業績、建立關係等策略建議。''',
    
    'equipment': '''您是專業的瓦斯行設備管理助理。
請協助處理瓦斯桶、設備登記、檢驗記錄等相關問題。
回答時請提供設備維護、安全檢查、法規遵循等專業建議。''',
    
    'staff': '''您是專業的瓦斯行員工管理助理。
請協助處理員工資料、排班安排、績效考核等相關問題。
回答時請提供人力資源、團隊管理、績效提升等專業建議。'''
}

# ===== 公告設定 =====
NOTICE = {
    'title': '智慧瓦斯AI管理系統',
    'content': '本系統目前使用 Google Gemini 1.5 Pro AI模型，提供專業瓦斯行管理協助。如有任何問題，請聯絡管理員。',
    'type': 'info',
    'timestamp': '2024-12-25'
}

# ===== 前端設定 =====
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
FRONTEND_CONFIG = {
    'api_base_url': f'http://localhost:{PORT}',
    'ai_model': 'Gemini 1.5 Pro',
    'company_name': COMPANY_NAME,
    'system_name': SYSTEM_NAME
}

# ========== 系統配置 ==========
SYSTEM_NAME = "智慧瓦斯 AI 管理系統"
SYSTEM_VERSION = "2.0.0"
SYSTEM_DESCRIPTION = "Jy技術團隊 - 專業瓦斯行管理AI助手"

# ========== 服務配置 ==========
HOST = "0.0.0.0"
PORT = 8600
DEBUG = True

# ========== 模組配置 ==========
SUPPORTED_MODULES = [
    "帳務", "成本", "派工", "維修", "FAQ", 
    "合約", "活動", "優惠", "設備管理", "員工管理"
]

# ========== API 配置 ==========
MAX_RETRIES = 3
RETRY_DELAY = 1  # 秒

# ========== 日誌配置 ==========
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ========== 安全配置 ==========
CORS_ORIGINS = ["*"]  # 開發環境，生產環境應限制具體域名
RATE_LIMIT = 100  # 每分鐘請求限制 

# ===== 用戶與權限設定 =====
# 用戶帳號密碼與角色
USERS = {
    "lstjks": {"password": "Ss520520", "role": "admin"},
    # 可擴充更多用戶
}
# 角色列表
ROLES = ["admin", "accounting", "maintenance", "dispatch", "staff", "manager", "sales"]
# 各模組API權限
MODULE_PERMISSIONS = {
    "accounting": ["admin", "accounting"],
    "cost": ["admin", "accounting", "manager"],
    "dispatch": ["admin", "dispatch", "manager"],
    "maintenance": ["admin", "maintenance", "manager"],
    "faq": ROLES,
    "contracts": ["admin", "manager", "sales"],
    "promotions": ["admin", "manager", "sales"],
    "offers": ["admin", "manager", "sales"],
    "equipment": ["admin", "maintenance", "manager"],
    "staff": ["admin", "manager"],
}

# ===== AI金鑰與模型設定 =====
GEMINI_API_KEY = "AIzaSyD7bIKgCLX4A6bn8uIoNQQPon1PRCXYMA8"
AI_MODEL = "Gemini 1.5 Pro"

# ===== API標準回應格式說明 =====
# {
#   "success": true,
#   "ai_model": "Gemini 1.5 Pro",
#   "module": "accounting",
#   "response": "AI回覆內容...",
#   "timestamp": "2024-06-25T12:00:00",
#   "user": "lstjks"
# } 