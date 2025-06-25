import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# 查詢歷史統一管理
query_history = []

# 記錄查詢
def log_query(user, module, query, response, success=True):
    entry = {
        'timestamp': datetime.now().isoformat(),
        'user': user,
        'module': module,
        'query': query,
        'response': response,
        'success': success
    }
    query_history.append(entry)
    logger.info(f"查詢歷史記錄: {entry}")

# 查詢歷史API
def get_history(user=None, module=None, limit=50):
    filtered = query_history
    if user:
        filtered = [h for h in filtered if h['user'] == user]
    if module:
        filtered = [h for h in filtered if h['module'] == module]
    return filtered[-limit:]

# 清空歷史
def clear_history():
    query_history.clear()
    logger.info("查詢歷史已清空") 