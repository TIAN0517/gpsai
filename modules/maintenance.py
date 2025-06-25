from flask import Blueprint, request, session
from auth import login_required
from ai_router import ai_router
from logging_utils import log_query
from config import MODULE_PERMISSIONS

bp = Blueprint('maintenance', __name__)

@bp.route('/api/maintenance', methods=['POST'])
@login_required(roles=MODULE_PERMISSIONS['maintenance'])
def maintenance_api():
    user = session.get('user', {}).get('username')
    query = request.get_json().get('query', '')
    ai_result = ai_router(query, 'maintenance')
    log_query(user, 'maintenance', query, ai_result['data']['response'] if ai_result['success'] else ai_result['error'], ai_result['success'])
    return ai_result 