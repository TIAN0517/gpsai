from flask import Blueprint, request, session
from auth import login_required
from ai_router import ai_router
from logging_utils import log_query
from config import MODULE_PERMISSIONS
import os
import json
from datetime import datetime

bp = Blueprint('cost', __name__)

@bp.route('/api/cost', methods=['POST'])
@login_required(roles=MODULE_PERMISSIONS['cost'])
def cost_api():
    user = session.get('user', {}).get('username')
    query = request.get_json().get('query', '')
    try:
        ai_result = ai_router(query, 'cost')
        error_str = str(ai_result.get('error', '')) if not ai_result.get('success') else ''
        log_query(user, 'cost', query, ai_result['data']['response'] if ai_result['success'] else error_str, ai_result['success'])
        return {
            'success': ai_result.get('success', False),
            'data': ai_result.get('data', None),
            'error': error_str if error_str else None
        }
    except Exception as e:
        log_query(user, 'cost', query, str(e), False)
        return {
            'success': False,
            'data': None,
            'error': str(e)
        }, 500 

@bp.route('/api/cost/enterprise_analysis', methods=['POST'])
@login_required(roles=MODULE_PERMISSIONS['cost'])
def enterprise_analysis():
    period = request.json.get('period', datetime.now().strftime('%Y-%m'))
    # 假資料，可改為資料庫查詢或AI分析
    data = {
        "total": {
            "buyTon": 32,
            "buyKg": 32000,
            "rawCost": 384000,
            "labor": 102000,
            "daily": 26000,
            "insurance": 19200,
            "carInsurance": 14000,
            "depreciation": 23000,
            "other": 10000,
            "sale": 576000
        },
        "stations": [
            {
                "name": "吉安站",
                "buyTon": 10,
                "buyKg": 10000,
                "rawCost": 120000,
                "labor": 32000,
                "daily": 8000,
                "insurance": 6000,
                "carInsurance": 4000,
                "depreciation": 7000,
                "other": 3000,
                "sale": 180000
            },
            {
                "name": "美崙站",
                "buyTon": 7,
                "buyKg": 7000,
                "rawCost": 84000,
                "labor": 22000,
                "daily": 6000,
                "insurance": 4200,
                "carInsurance": 3000,
                "depreciation": 5000,
                "other": 2000,
                "sale": 126000
            },
            {
                "name": "市區站",
                "buyTon": 15,
                "buyKg": 15000,
                "rawCost": 180000,
                "labor": 48000,
                "daily": 12000,
                "insurance": 9000,
                "carInsurance": 7000,
                "depreciation": 11000,
                "other": 5000,
                "sale": 270000
            }
        ]
    }
    # 自動保存查詢結果到本地JSON
    save_dir = os.path.join(os.path.dirname(__file__), '../data')
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f'enterprise_cost_analysis_{period}.json')
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump({"period": period, "data": data, "timestamp": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)
    return {
        "success": True,
        "period": period,
        "data": data,
        "timestamp": datetime.now().isoformat()
    } 