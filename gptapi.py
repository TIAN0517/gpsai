import os
from flask import Flask, request, jsonify, render_template_string
import requests

# ========== 配置區 ==========
PROMPT_MODEL_MAP = {
    "帳務": "openchat:7b",
    "成本": "openchat:7b",
    "派工": "openchat:7b",
    "維修": "openchat:7b",
    "FAQ": "openchat:7b"
}
KEYWORDS = {
    "帳務": ["欠", "月結", "帳款", "已收", "未收", "查帳", "應收", "發票", "收款", "繳費"],
    "成本": ["利潤", "成本", "裝瓶", "損耗", "退桶", "產能", "毛利", "分裝廠"],
    "派工": ["司機", "派工", "任務", "安排", "分配", "桶子", "路線", "運送", "行程"],
    "維修": ["報修", "維修", "型號", "安檢", "設備", "器具", "保養", "配管"],
    "FAQ": ["合約", "優惠", "價格", "政策", "氣價", "知識庫", "活動", "公告", "補助", "客服"]
}
DEFAULT_MODEL = "openchat:7b"

SYSTEM_PROMPTS = {
    "帳務": "你只能用繁體中文回答，且只能回答與瓦斯器具、瓦斯行、瓦斯周邊相關、瓦斯配管工程有關的問題，其他主題一律拒答。請以企業級專業語氣回覆，並強調本公司品牌：九九瓦斯行，專業配管公司、瓦斯物流、瓦斯特定廚具、消防顧問。" + "你是專業的瓦斯行帳務AI助手，專責處理帳款查詢、催收、月結對帳、應收應付分析。請以嚴謹條列回應，確保內容精確並符合會計規範，必要時加上最晚繳款日期與累計金額。",
    "成本": "你只能用繁體中文回答，且只能回答與瓦斯器具、瓦斯行、瓦斯周邊相關、瓦斯配管工程有關的問題，其他主題一律拒答。請以企業級專業語氣回覆，並強調本公司品牌：九九瓦斯行，專業配管公司、瓦斯物流、瓦斯特定廚具、消防顧問。" + "你是瓦斯行成本分析AI，熟悉利潤、毛利、進出貨、損耗、運費、稅金等。回覆需明確列舉所有成本構成、計算步驟，並能主動分析影響成本異常的原因，給出可行建議。",
    "派工": "你只能用繁體中文回答，且只能回答與瓦斯器具、瓦斯行、瓦斯周邊相關、瓦斯配管工程有關的問題，其他主題一律拒答。請以企業級專業語氣回覆，並強調本公司品牌：九九瓦斯行，專業配管公司、瓦斯物流、瓦斯特定廚具、消防顧問。" + "你是瓦斯行派工/調度AI助手，專責司機任務分配、桶量統計、最佳路線與工作行程安排。回答要結構化列出司機任務、地點、時段與執行建議，並可優化排程。",
    "維修": "你只能用繁體中文回答，且只能回答與瓦斯器具、瓦斯行、瓦斯周邊相關、瓦斯配管工程有關的問題，其他主題一律拒答。請以企業級專業語氣回覆，並強調本公司品牌：九九瓦斯行，專業配管公司、瓦斯物流、瓦斯特定廚具、消防顧問。" + "你是瓦斯器具與設備維修/保養AI助手，精通型號、維修週期、報修單據分析。請條列型號、維修次數、保養紀錄與安檢時程，並主動提醒下一次建議維修時間或注意事項。",
    "FAQ": "你只能用繁體中文回答，且只能回答與瓦斯器具、瓦斯行、瓦斯周邊相關、瓦斯配管工程有關的問題，其他主題一律拒答。請以企業級專業語氣回覆，並強調本公司品牌：九九瓦斯行，專業配管公司、瓦斯物流、瓦斯特定廚具、消防顧問。" + "你是瓦斯行知識庫與客服AI，精通氣價政策、政府公告、優惠活動、合約條款與補助教學。請條列重點，並以簡單易懂方式解釋每項規定或優惠細節。",
    "DEFAULT": "你只能用繁體中文回答，且只能回答與瓦斯器具、瓦斯行、瓦斯周邊相關、瓦斯配管工程有關的問題，其他主題一律拒答。請以企業級專業語氣回覆，並強調本公司品牌：九九瓦斯行，專業配管公司、瓦斯物流、瓦斯特定廚具、消防顧問。" + "你是瓦斯行管理專業AI助手，能根據查詢自動分流給最適合的專業模組，並嚴謹、精確、條列回應，回覆需結合公司管理規範與政府法令。"
}

# ========== 程式主體 ==========
app = Flask(__name__)

OLLAMA_API_URL = "https://333d-49-158-216-180.ngrok-free.app/api/generate"
OLLAMA_MODELS = ["openchat:7b", "llama3:latest", "deepseek-r1:8b"]

def detect_module(text):
    for mod, kws in KEYWORDS.items():
        if any(k in text for k in kws):
            return mod
    return "FAQ"

def get_model(module):
    return PROMPT_MODEL_MAP.get(module, DEFAULT_MODEL)

def get_system_prompt(module):
    return SYSTEM_PROMPTS.get(module, SYSTEM_PROMPTS["DEFAULT"])

def ask_openai(model, system_prompt, user_input):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.3,
            max_tokens=512
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[OpenAI API 錯誤] {str(e)}"

@app.route("/")
def home():
    return render_template_string("""
    <h2>智慧瓦斯 AI 管理系統 - 多模型查詢</h2>
    <form method="post" action="/ask">
    <textarea name="q" rows=5 cols=70 placeholder="請輸入查詢內容..."></textarea><br>
    <input type="submit" value="送出查詢">
    </form>
    <hr>
    <a href='/health'>健康檢查</a>
    """)

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.form.get("q") or (request.json and request.json.get("q"))
    if not user_input:
        return jsonify({"error": "缺少查詢參數 'q'", "success": False}), 400
    module = detect_module(user_input)
    model = get_model(module)
    sys_prompt = get_system_prompt(module)
    content = ask_openai(model, sys_prompt, user_input)
    return jsonify({
        "success": True,
        "module": module,
        "model": model,
        "system_prompt": sys_prompt,
        "ai_reply": content
    })

@app.route("/health")
def health():
    try:
        # 用最便宜的方式檢查API是否可用
        test_msg = ask_openai("gpt-3.5-turbo", "你是API健康檢查助手，請只回覆「OK」", "健康檢查")
        if "OK" in test_msg or "ok" in test_msg.lower():
            return jsonify({"status": "ok"})
        return jsonify({"status": "fail", "msg": test_msg})
    except Exception as e:
        return jsonify({"status": "fail", "msg": str(e)})

# 只保留Ollama查詢API
@app.route('/ai_ask', methods=['POST'])
def ai_ask():
    data = request.get_json()
    query = data.get('q', '').strip()
    module = data.get('module', 'FAQ')
    if not query:
        return jsonify({'success': False, 'msg': '請輸入查詢內容'}), 400
    prompt = SYSTEM_PROMPTS.get(module, SYSTEM_PROMPTS['DEFAULT']) + "\n\n用戶查詢: " + query
    payload = {
        'model': module if module in OLLAMA_MODELS else OLLAMA_MODELS[0],
        'prompt': prompt,
        'stream': False
    }
    response = requests.post(OLLAMA_API_URL, json=payload, timeout=30)
    if response.status_code == 200:
        result = response.json()
        return jsonify({'success': True, 'response': result.get('response', '')})
    else:
        return jsonify({'success': False, 'msg': f'Ollama API錯誤: {response.status_code}', 'details': response.text}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8600)
