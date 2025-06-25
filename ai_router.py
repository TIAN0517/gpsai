import requests
import logging
from flask import session
from config import GEMINI_API_KEY, AI_MODEL, MODULE_PERMISSIONS
from datetime import datetime

logger = logging.getLogger(__name__)

def ai_router(query, module):
    prompt = f"請用繁體中文詳細回答：({module}) {query}"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-002:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        if resp.status_code == 200:
            result = resp.json()
            try:
                answer = result['candidates'][0]['content']['parts'][0]['text']
            except Exception:
                answer = str(result)
            logger.info(f"AI查詢成功: module={module}, user={session.get('user', {}).get('username')}")
            return {
                'success': True,
                'code': 0,
                'data': {
                    'ai_model': AI_MODEL,
                    'module': module,
                    'response': answer,
                    'timestamp': datetime.now().isoformat(),
                    'user': session.get('user', {}).get('username')
                },
                'error': None
            }
        else:
            logger.error(f"AI服務錯誤: {resp.status_code}, {resp.text}")
            return {
                'success': False,
                'code': 500,
                'data': None,
                'error': {
                    'msg': f'AI服務錯誤({resp.status_code})',
                    'details': resp.text,
                    'suggestion': '請稍後再試或聯絡管理員'
                }
            }
    except Exception as e:
        logger.error(f"AI查詢異常: {str(e)}")
        return {
            'success': False,
            'code': 500,
            'data': None,
            'error': {
                'msg': 'AI查詢異常',
                'details': str(e),
                'suggestion': '請檢查網路或聯絡管理員'
            }
        } 