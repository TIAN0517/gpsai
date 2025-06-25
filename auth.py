import functools
from flask import session, request, jsonify
import logging
from config import USERS
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
SESSION_TIMEOUT = 3600  # 1小時

def is_logged_in():
    user = session.get('user')
    last_active = session.get('last_active')
    if not user or not last_active:
        return False
    if datetime.now() > datetime.fromisoformat(last_active) + timedelta(seconds=SESSION_TIMEOUT):
        session.clear()
        return False
    # 更新活動時間
    session['last_active'] = datetime.now().isoformat()
    return True

def login_required(roles=None):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if not is_logged_in():
                logger.warning('未登入存取: %s', request.path)
                return jsonify({
                    'success': False,
                    'code': 401,
                    'error': {
                        'msg': '未登入或權限不足',
                        'details': '請先登入後再操作',
                        'suggestion': '請調用 /api/login 登入'
                    },
                    'data': None
                })
            user = session.get('user')
            if roles and user['role'] not in roles:
                logger.warning('權限不足: %s, user=%s', request.path, user)
                return jsonify({
                    'success': False,
                    'code': 401,
                    'error': {
                        'msg': '未登入或權限不足',
                        'details': '請先登入後再操作',
                        'suggestion': '請調用 /api/login 登入'
                    },
                    'data': None
                })
            return f(*args, **kwargs)
        return wrapper
    return decorator

def login(username, password):
    user = USERS.get(username)
    if user and user['password'] == password:
        session['user'] = {'username': username, 'role': user['role']}
        session['last_active'] = datetime.now().isoformat()
        logger.info('用戶登入成功: %s', username)
        return True
    logger.warning('登入失敗: %s', username)
    return False 