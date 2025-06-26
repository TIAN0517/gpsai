from flask import Blueprint, request, session
from auth import login_required
from ai_router import ai_router
from logging_utils import log_query
from config import MODULE_PERMISSIONS

bp = Blueprint('equipment', __name__)

@bp.route('/api/equipment', methods=['POST'])
@login_required(roles=MODULE_PERMISSIONS['equipment'])
def equipment_api():
    user = session.get('user', {}).get('username')
    query = request.get_json().get('query', '')
    try:
        ai_result = ai_router(query, 'equipment')
        error_str = str(ai_result.get('error', '')) if not ai_result.get('success') else ''
        log_query(user, 'equipment', query, ai_result['data']['response'] if ai_result['success'] else error_str, ai_result['success'])
        return {
            'success': ai_result.get('success', False),
            'data': ai_result.get('data', None),
            'error': error_str if error_str else None
        }
    except Exception as e:
        log_query(user, 'equipment', query, str(e), False)
        return {
            'success': False,
            'data': None,
            'error': str(e)
        }, 500 