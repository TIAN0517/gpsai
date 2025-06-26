import os
import json
import time
import logging
import requests
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, session, render_template_string, redirect, url_for
from config import *


# ========== HTML 模板定義 ==========

# 主頁模板
MAIN_PAGE_HTML = """
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>智慧瓦斯 AI 管理系統 - Jy技術團隊</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Orbitron', 'Noto Sans TC', '微軟正黑體', sans-serif;
            background: linear-gradient(135deg, #161a2a 0%, #2676ff 100%);
            color: #fff;
            min-height: 100vh;
            overflow-x: hidden;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
            position: relative;
        }
        .logo {
            font-size: 3.5rem;
            font-weight: 900;
            color: #2676ff;
            text-shadow: 0 0 30px #2676ff;
            animation: flicker 3s infinite;
            margin-bottom: 10px;
        }
        .subtitle {
            font-size: 1.5rem;
            color: #ff9a3c;
            text-shadow: 0 0 15px #ff9a3c;
        }
        .developer {
            font-size: 0.9rem;
            color: #888;
            margin-top: 5px;
        }
        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(30, 34, 58, 0.8);
            border: 1px solid #2676ff;
            border-radius: 15px;
            padding: 15px 25px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }
        .status-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #00ff88;
            animation: pulse 2s infinite;
        }
        .query-card {
            background: rgba(30, 34, 58, 0.9);
            border: 2px solid #2676ff;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 0 40px rgba(38, 118, 255, 0.3);
            backdrop-filter: blur(15px);
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 25px;
        }
        label {
            display: block;
            margin-bottom: 12px;
            font-weight: bold;
            color: #ff9a3c;
            font-size: 1.1rem;
        }
        textarea {
            width: 100%;
            padding: 18px;
            border: 2px solid #2676ff;
            border-radius: 15px;
            background: rgba(22, 26, 42, 0.9);
            color: #fff;
            font-size: 16px;
            font-family: inherit;
            resize: vertical;
            outline: none;
            transition: all 0.3s ease;
            min-height: 120px;
        }
        textarea:focus {
            border-color: #ff9a3c;
            box-shadow: 0 0 25px rgba(255, 154, 60, 0.4);
            transform: scale(1.02);
        }
        .btn {
            background: linear-gradient(45deg, #2676ff, #ff9a3c);
            color: #fff;
            border: none;
            padding: 18px 40px;
            border-radius: 50px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 0 25px rgba(38, 118, 255, 0.4);
            position: relative;
            overflow: hidden;
        }
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 35px rgba(38, 118, 255, 0.6);
        }
        .btn:active {
            transform: translateY(-1px);
        }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .modules {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .module-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            transition: all 0.4s ease;
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }
        .module-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        .module-card:hover::before {
            left: 100%;
        }
        .module-card:hover {
            transform: translateY(-8px) scale(1.05);
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        }
        .module-card h3 {
            font-size: 1.3rem;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        .module-card p {
            font-size: 0.9rem;
            opacity: 0.9;
            line-height: 1.4;
        }
        .result {
            margin-top: 25px;
            padding: 25px;
            background: rgba(30, 34, 58, 0.95);
            border-radius: 20px;
            border-left: 5px solid #ff9a3c;
            white-space: pre-wrap;
            line-height: 1.7;
            box-shadow: 0 0 30px rgba(255, 154, 60, 0.2);
            animation: slideIn 0.5s ease;
        }
        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #2676ff;
        }
        .result-meta {
            display: flex;
            gap: 20px;
            font-size: 0.9rem;
            color: #ff9a3c;
        }
        .loading {
            text-align: center;
            color: #ff9a3c;
            font-size: 18px;
            margin: 25px 0;
            animation: pulse 1.5s infinite;
        }
        .loading::after {
            content: '';
            animation: dots 1.5s infinite;
        }
        .links {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 40px;
            flex-wrap: wrap;
        }
        .links a {
            color: #ff9a3c;
            text-decoration: none;
            padding: 12px 25px;
            border: 2px solid #ff9a3c;
            border-radius: 30px;
            transition: all 0.3s ease;
            font-weight: bold;
            position: relative;
            overflow: hidden;
        }
        .links a:hover {
            background: #ff9a3c;
            color: #161a2a;
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(255, 154, 60, 0.4);
        }
        .error {
            background: rgba(255, 59, 48, 0.1);
            border-left-color: #ff3b30;
            color: #ff6b6b;
        }
        @keyframes flicker {
            0%, 100% { opacity: 1; text-shadow: 0 0 30px #2676ff; }
            50% { opacity: 0.8; text-shadow: 0 0 20px #2676ff; }
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        @keyframes dots {
            0%, 20% { content: ''; }
            40% { content: '.'; }
            60% { content: '..'; }
            80%, 100% { content: '...'; }
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @media (max-width: 768px) {
            .container { padding: 15px; }
            .logo { font-size: 2.5rem; }
            .subtitle { font-size: 1.2rem; }
            .status-bar { flex-direction: column; gap: 10px; }
            .modules { grid-template-columns: 1fr; }
            .result-meta { flex-direction: column; gap: 5px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">智慧瓦斯 AI</div>
            <div class="subtitle">Jy技術團隊 - 專業管理助手</div>
            <div class="developer">開發者：Jy技術團隊 | 版本：3.0.0</div>
        </div>
        
        <div class="status-bar">
            <div class="status-item">
                <div class="status-indicator"></div>
                <span>系統狀態：正常運行</span>
            </div>
            <div class="status-item">
                <span>🤖 AI模型：董娘的助手</span>
            </div>
            <div class="status-item">
                <span>📊 今日查詢：<span id="todayQueries">0</span></span>
            </div>
            <div class="status-item">
                <span>⏰ 最後更新：<span id="lastUpdate">--</span></span>
            </div>
        </div>
        
        <div class="query-card">
            <form id="queryForm">
                <div class="form-group">
                    <label for="query">🚀 請輸入您的查詢：</label>
                    <textarea id="query" name="query" rows="4" placeholder="例如：請查詢本月帳單明細、今日派工安排、設備維修進度、成本分析報告等..." required></textarea>
                </div>
                <button type="submit" class="btn" id="submitBtn">
                    <span id="btnText">🚀 智能查詢</span>
                </button>
            </form>
            
            <div id="loading" class="loading" style="display: none;">
                🤖 AI 正在思考中，請稍候
            </div>
            
            <div id="result" class="result" style="display: none;"></div>
        </div>
        
        <div class="modules">
            <div class="module-card" onclick="fillQuery('請查詢本月帳單明細')">
                <h3>💰 帳務管理</h3>
                <p>帳款查詢、催收、月結對帳</p>
            </div>
            <div class="module-card" onclick="fillQuery('請分析本月成本狀況')">
                <h3>📊 成本分析</h3>
                <p>利潤分析、成本計算、損耗統計</p>
            </div>
            <div class="module-card" onclick="fillQuery('請安排今日派工任務')">
                <h3>🚚 派工調度</h3>
                <p>司機任務、路線規劃、行程安排</p>
            </div>
            <div class="module-card" onclick="fillQuery('請查詢設備維修進度')">
                <h3>🔧 維修保養</h3>
                <p>設備維修、安檢報告、保養提醒</p>
            </div>
            <div class="module-card" onclick="fillQuery('請解答瓦斯價格政策')">
                <h3>❓ FAQ 客服</h3>
                <p>常見問題、政策說明、客服支援</p>
            </div>
            <div class="module-card" onclick="fillQuery('請查詢合約到期狀況')">
                <h3>📋 合約管理</h3>
                <p>合約查詢、到期提醒、條款說明</p>
            </div>
            <div class="module-card" onclick="fillQuery('請介紹最新促銷活動')">
                <h3>🎉 活動推廣</h3>
                <p>促銷活動、抽獎比賽、節能推廣</p>
            </div>
            <div class="module-card" onclick="fillQuery('請說明會員優惠方案')">
                <h3>🎁 優惠方案</h3>
                <p>折扣政策、會員制度、積分回饋</p>
            </div>
            <div class="module-card" onclick="fillQuery('請查詢設備監控狀態')">
                <h3>⚙️ 設備管理</h3>
                <p>設備監控、安全檢測、管線維護</p>
            </div>
            <div class="module-card" onclick="fillQuery('請安排員工排班表')">
                <h3>👥 員工管理</h3>
                <p>排班考勤、薪資計算、培訓安排</p>
            </div>
        </div>
        
        <div class="links">
            <a href="/health">🩺 健康檢查</a>
            <a href="/api_doc">📚 API 文檔</a>
            <a href="/quota">📊 配額查詢</a>
            <a href="/login">🔐 管理登入</a>
        </div>
    </div>

    <script>
        // 點擊模組卡片自動填入查詢內容
        function fillQuery(queryText) {
            document.getElementById('query').value = queryText;
            document.getElementById('query').focus();
        }

        // 更新狀態欄
        function updateStatus() {
            fetch('/health')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('todayQueries').textContent = data.stats?.total_requests || 0;
                    document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
                })
                .catch(error => console.error('狀態更新失敗:', error));
        }

        // 定期更新狀態
        setInterval(updateStatus, 30000); // 每30秒更新一次
        updateStatus(); // 立即更新一次

        document.getElementById('queryForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const query = document.getElementById('query').value;
            const loading = document.getElementById('loading');
            const result = document.getElementById('result');
            const submitBtn = document.getElementById('submitBtn');
            const btnText = document.getElementById('btnText');
            
            if (!query.trim()) {
                alert('請輸入查詢內容');
                return;
            }
            
            // 顯示載入中
            loading.style.display = 'block';
            result.style.display = 'none';
            submitBtn.disabled = true;
            btnText.textContent = '處理中...';
            
            try {
                const response = await fetch('/ai_ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ query: query })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    result.innerHTML = `
                        <div class="result-header">
                            <h3>🤖 AI 回應結果</h3>
                            <div class="result-meta">
                                <span>🎯 模組: ${data.module}</span>
                                <span>🤖 模型: ${data.ai_model}</span>
                                <span>⏱️ 時間: ${data.response_time}秒</span>
                            </div>
                        </div>
                        <div style="margin-top: 15px;">
                            ${data.response.replace(/\\n/g, '<br>')}
                        </div>
                    `;
                    result.className = 'result';
                } else {
                    result.innerHTML = `
                        <div class="result-header">
                            <h3>❌ 查詢失敗</h3>
                        </div>
                        <div style="margin-top: 15px;">
                            ${data.error || '請求失敗'}
                        </div>
                    `;
                    result.className = 'result error';
                }
                
                result.style.display = 'block';
            } catch (error) {
                result.innerHTML = `
                    <div class="result-header">
                        <h3>❌ 網路錯誤</h3>
                    </div>
                    <div style="margin-top: 15px;">
                        ${error.message}
                    </div>
                `;
                result.className = 'result error';
                result.style.display = 'block';
            } finally {
                loading.style.display = 'none';
                submitBtn.disabled = false;
                btnText.textContent = '🚀 智能查詢';
            }
        });
    </script>
</body>
</html>
"""

# 登入頁面模板
LOGIN_PAGE_HTML = """
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>管理登入 - 智慧瓦斯 AI 管理系統</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Orbitron', 'Noto Sans TC', sans-serif;
            background: linear-gradient(135deg, #161a2a 0%, #2676ff 100%);
            color: #fff;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            background: rgba(30, 34, 58, 0.9);
            border: 2px solid #2676ff;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 0 40px rgba(38, 118, 255, 0.3);
            backdrop-filter: blur(15px);
            width: 100%;
            max-width: 400px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo {
            font-size: 2rem;
            font-weight: 900;
            color: #2676ff;
            text-shadow: 0 0 20px #2676ff;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #ff9a3c;
            font-size: 1rem;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #ff9a3c;
            font-weight: bold;
        }
        input {
            width: 100%;
            padding: 15px;
            border: 2px solid #2676ff;
            border-radius: 10px;
            background: rgba(22, 26, 42, 0.9);
            color: #fff;
            font-size: 16px;
            outline: none;
            transition: all 0.3s;
        }
        input:focus {
            border-color: #ff9a3c;
            box-shadow: 0 0 15px rgba(255, 154, 60, 0.3);
        }
        .btn {
            width: 100%;
            background: linear-gradient(45deg, #2676ff, #ff9a3c);
            color: #fff;
            border: none;
            padding: 15px;
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(38, 118, 255, 0.4);
        }
        .back-link {
            text-align: center;
            margin-top: 20px;
        }
        .back-link a {
            color: #ff9a3c;
            text-decoration: none;
        }
        .error {
            background: rgba(255, 59, 48, 0.1);
            border: 1px solid #ff3b30;
            color: #ff6b6b;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 15px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="header">
            <div class="logo">管理登入</div>
            <div class="subtitle">智慧瓦斯 AI 管理系統</div>
        </div>
        
        <div id="error" class="error"></div>
        
        <form id="loginForm">
            <div class="form-group">
                <label for="username">用戶名</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">密碼</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn">登入</button>
        </form>
        
        <div class="back-link">
            <a href="/">← 返回首頁</a>
        </div>
    </div>

    <script>
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const error = document.getElementById('error');
            
            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    window.location.href = '/';
                } else {
                    error.textContent = data.message || '登入失敗';
                    error.style.display = 'block';
                }
            } catch (error) {
                error.textContent = '網路錯誤，請稍後再試';
                error.style.display = 'block';
            }
        });
    </script>
</body>
</html>
"""

# API 文檔頁面模板
API_DOC_HTML = """
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API 文檔 - 智慧瓦斯 AI 管理系統</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Orbitron', 'Noto Sans TC', sans-serif;
            background: linear-gradient(135deg, #161a2a 0%, #2676ff 100%);
            color: #fff;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(30, 34, 58, 0.9);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 0 30px rgba(38, 118, 255, 0.3);
        }
        h1 {
            color: #ff9a3c;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5rem;
        }
        .api-section {
            margin-bottom: 30px;
            padding: 25px;
            background: rgba(22, 26, 42, 0.8);
            border-radius: 15px;
            border-left: 4px solid #2676ff;
        }
        .api-section h2 {
            color: #2676ff;
            margin-bottom: 15px;
            font-size: 1.5rem;
        }
        .method {
            display: inline-block;
            padding: 8px 20px;
            background: #ff9a3c;
            color: #161a2a;
            border-radius: 25px;
            font-weight: bold;
            margin-right: 15px;
            font-size: 0.9rem;
        }
        .endpoint {
            font-family: monospace;
            background: rgba(255, 154, 60, 0.2);
            padding: 12px;
            border-radius: 8px;
            margin: 15px 0;
            font-size: 1.1rem;
        }
        .example {
            background: rgba(38, 118, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            margin: 15px 0;
            font-family: monospace;
            white-space: pre-wrap;
            border: 1px solid #2676ff;
        }
        .back-link {
            text-align: center;
            margin-top: 40px;
        }
        .back-link a {
            color: #ff9a3c;
            text-decoration: none;
            padding: 15px 30px;
            border: 2px solid #ff9a3c;
            border-radius: 30px;
            transition: all 0.3s;
            font-weight: bold;
        }
        .back-link a:hover {
            background: #ff9a3c;
            color: #161a2a;
            transform: translateY(-2px);
        }
        .feature-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .feature-item {
            background: rgba(255, 154, 60, 0.1);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #ff9a3c;
        }
        .feature-item h4 {
            color: #ff9a3c;
            margin-bottom: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 API 文檔 - 智慧瓦斯 AI 管理系統</h1>
        
        <div class="api-section">
            <h2>🤖 AI 查詢 API</h2>
            <div><span class="method">POST</span> <span class="endpoint">/ai_ask</span></div>
            <p>使用 董娘的助手 進行智能查詢，自動分流到對應模組，支援多家 AI API 備援</p>
            
            <h3>請求格式:</h3>
            <div class="example">{
    "query": "請查詢本月帳單明細"
}</div>
            
            <h3>回應格式:</h3>
            <div class="example">{
    "success": true,
    "query": "請查詢本月帳單明細",
    "response": "根據您的查詢，以下是本月帳單明細...",
    "module": "帳務",
    "api_used": "Gemini",
    "api_display_name": "董娘的助手",
    "response_time": 2.34,
    "timestamp": "2024-01-01T12:00:00"
}</div>
        </div>
        
        <div class="api-section">
            <h2>🩺 健康檢查 API</h2>
            <div><span class="method">GET</span> <span class="endpoint">/health</span></div>
            <p>檢查系統健康狀態、AI 模型連接、API 統計資訊</p>
            
            <h3>回應格式:</h3>
            <div class="example">{
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00",
    "apis": {
        "Gemini": {
            "status": "healthy",
            "display_name": "Google 董娘的特助"
        }
    },
    "stats": {
        "total_requests": 150,
        "successful_requests": 145,
        "failed_requests": 5,
        "uptime": "1:00:00",
        "last_request": "2024-01-01T12:00:00"
    },
    "modules": ["帳務", "成本", "派工", "維修", "FAQ"]
}</div>
        </div>
        
        <div class="api-section">
            <h2>📊 配額查詢 API</h2>
            <div><span class="method">GET</span> <span class="endpoint">/quota</span></div>
            <p>查詢各 AI API 的使用配額和剩餘次數</p>
        </div>
        
        <div class="api-section">
            <h2>📋 查詢歷史 API</h2>
            <div><span class="method">GET</span> <span class="endpoint">/history</span></div>
            <p>獲取查詢歷史記錄，支援按用戶和模組過濾</p>
            <div><span class="method">DELETE</span> <span class="endpoint">/history</span></div>
            <p>刪除查詢歷史記錄</p>
        </div>
        
        <div class="api-section">
            <h2>📋 模組列表 API</h2>
            <div><span class="method">GET</span> <span class="endpoint">/modules</span></div>
            <p>獲取支援的模組列表和分類</p>
        </div>
        
        <div class="api-section">
            <h2>📢 公告 API</h2>
            <div><span class="method">GET</span> <span class="endpoint">/notice</span></div>
            <p>獲取系統公告資訊</p>
        </div>
        
        <div class="api-section">
            <h2>🔐 用戶管理 API</h2>
            <div><span class="method">POST</span> <span class="endpoint">/login</span></div>
            <p>用戶登入</p>
            <div><span class="method">GET</span> <span class="endpoint">/logout</span></div>
            <p>用戶登出</p>
        </div>
        
        <div class="api-section">
            <h2>🚀 系統特色功能</h2>
            <div class="feature-list">
                <div class="feature-item">
                    <h4>🤖 多 AI 備援</h4>
                    <p>支援 Gemini、OpenAI、DeepSeek 自動切換</p>
                </div>
                <div class="feature-item">
                    <h4>🎯 智能分流</h4>
                    <p>自動識別查詢內容並分流到對應模組</p>
                </div>
                <div class="feature-item">
                    <h4>📊 即時統計</h4>
                    <p>API 使用統計、成功率、響應時間監控</p>
                </div>
                <div class="feature-item">
                    <h4>🔐 權限管理</h4>
                    <p>多級用戶權限、登入驗證、歷史記錄</p>
                </div>
                <div class="feature-item">
                    <h4>🌐 響應式設計</h4>
                    <p>支援手機、平板、桌面多設備訪問</p>
                </div>
                <div class="feature-item">
                    <h4>📱 企業級 UI</h4>
                    <p>現代化界面、動畫效果、品牌主題</p>
                </div>
            </div>
        </div>
        
        <div class="back-link">
            <a href="/">🏠 返回首頁</a>
        </div>
    </div>
</body>
</html>
"""

# ========== 日誌配置 ==========
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# ========== Flask 主體 ==========
app = Flask(__name__)
app.secret_key = SESSION_SECRET

# ========== 全域變數 ==========
# API 使用統計
api_stats = {
    'total_requests': 0,
    'successful_requests': 0,
    'failed_requests': 0,
    'last_request_time': None,
    'api_errors': {},
    'quota_usage': {
        'hourly': 0,
        'daily': 0,
        'monthly': 0
    }
}

# 查詢歷史（實際應用中應使用資料庫）
query_history = []

# 快取系統
cache = {}
cache_timestamps = {}

# ========== 權限分級裝飾器 ==========
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                return jsonify({'error': '請先登入', 'msg': 'Please login first'}), 401
            if role and session['user']['role'] != role:
                return jsonify({'error': '權限不足', 'msg': 'Permission denied'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ========== API 分流與備援機制 ==========
def get_available_apis():
    """獲取可用的 API 列表，只允許三個ollama模型，且API URL為ngrok外部API"""
    apis = []
    ollama_models = ["openchat:7b", "llama3:latest", "deepseek-r1:8b"]
    for model in ollama_models:
        apis.append({
            'name': 'Ollama',
            'display_name': f'Ollama {model}',
            'url': 'https://333d-49-158-216-180.ngrok-free.app/api/generate',
            'model': model,
            'priority': 0,
            'status': 'unknown',
            'type': 'local'
        })
    return apis

def check_api_health(api):
    """檢查 API 健康狀態（僅Ollama）"""
    try:
        if api['name'] == 'Ollama':
            response = requests.post(
                api['url'],
                json={
                    'model': api['model'],
                    'prompt': 'test',
                    'stream': False
                },
                timeout=5
            )
            return response.status_code == 200
        else:
            return False
    except Exception as e:
        logger.error(f"API 健康檢查失敗 {api['name']}: {str(e)}")
        return False

def call_ai_api(api, query, module):
    """調用指定的 AI API（僅Ollama）"""
    try:
        if api['name'] == 'Ollama':
            return call_ollama_api(api, query, module)
        else:
            raise Exception("只允許Ollama API")
    except Exception as e:
        logger.error(f"API 調用失敗 {api['name']}: {str(e)}")
        raise

def call_ollama_api(api, query, module):
    """調用 Ollama API"""
    prompt = f"{SYSTEM_PROMPTS.get(module, SYSTEM_PROMPTS['DEFAULT'])}\n\n用戶查詢: {query}"
    response = requests.post(
        api['url'],
        json={
            'model': api['model'],
            'prompt': prompt,
            'stream': False
        },
        timeout=30
    )
    if response.status_code == 200:
        result = response.json()
        if 'response' in result:
            return result['response']
        else:
            raise Exception("Ollama API 回應格式錯誤")
    else:
        raise Exception(f"Ollama API 錯誤: {response.status_code} - {response.text}")

def decode_unicode_response(text):
    """自動解碼 Unicode 轉中文"""
    try:
        # 嘗試解碼常見的 Unicode 轉義序列
        if '\\u' in text:
            text = text.encode('utf-8').decode('unicode_escape')
        return text
    except Exception as e:
        logger.warning(f"Unicode 解碼失敗: {str(e)}")
        return text

# ========== 快取管理 ==========
def get_cache_key(query, module):
    """生成快取鍵"""
    return hashlib.md5(f"{query}:{module}".encode()).hexdigest()

def get_from_cache(query, module):
    """從快取獲取結果"""
    if not CACHE_ENABLED:
        return None
    
    cache_key = get_cache_key(query, module)
    if cache_key in cache:
        timestamp = cache_timestamps.get(cache_key, 0)
        if time.time() - timestamp < CACHE_TTL:
            return cache[cache_key]
        else:
            # 過期，清理
            del cache[cache_key]
            del cache_timestamps[cache_key]
    return None

def set_cache(query, module, result):
    """設置快取"""
    if not CACHE_ENABLED:
        return
    
    cache_key = get_cache_key(query, module)
    
    # 檢查快取大小限制
    if len(cache) >= CACHE_MAX_SIZE:
        # 清理最舊的項目
        oldest_key = min(cache_timestamps.keys(), key=lambda k: cache_timestamps[k])
        del cache[oldest_key]
        del cache_timestamps[oldest_key]
    
    cache[cache_key] = result
    cache_timestamps[cache_key] = time.time()

# ========== 配額管理 ==========
def check_quota():
    """檢查配額限制"""
    # 配額功能已停用，僅使用單一 Gemini API
    return True, None

def increment_quota():
    """增加配額使用量"""
    # 配額功能已停用，僅使用單一 Gemini API
    pass

# ========== 路由定義 ==========

@app.route('/')
def index():
    """主頁 - 智慧瓦斯AI管理系統"""
    return render_template_string(MAIN_PAGE_HTML)

@app.route('/login', methods=['GET', 'POST'])
def legacy_login():
    return jsonify({
        'success': False,
        'code': 405,
        'error': {
            'msg': '請改用 /api/login 進行登入',
            'details': '舊版HTML登入已停用',
            'suggestion': '請呼叫 /api/login 並用POST+JSON格式'
        },
        'data': None
    })

@app.route('/logout', methods=['GET', 'POST'])
def legacy_logout():
    return jsonify({
        'success': False,
        'code': 405,
        'error': {
            'msg': '請改用 /api/logout 進行登出',
            'details': '舊版HTML登出已停用',
            'suggestion': '請呼叫 /api/logout 並用POST'
        },
        'data': None
    })

@app.route('/health')
def health_check():
    """健康檢查 API - 企業級監控"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'ai_model': 'ollama-ngrok',
        'cache': {
            'size': len(cache),
            'enabled': CACHE_ENABLED
        }
    })

@app.route('/modules')
def get_modules():
    """獲取模組列表"""
    return jsonify({
        'modules': MODULES,
        'categories': MODULE_CATEGORIES
    })

@app.route('/notice')
def get_notice():
    """獲取公告資訊"""
    return jsonify({
        'notice': NOTICE,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/ai_ask', methods=['POST'])
def ai_ask():
    start_time = time.time()
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': '缺少查詢內容', 'msg': 'Missing query parameter'}), 400
        query = data['query'].strip()
        if not query:
            return jsonify({'error': '查詢內容不能為空', 'msg': 'Query cannot be empty'}), 400
        # 模組判斷
        module = 'FAQ'
        for mod, keywords in KEYWORDS.items():
            if any(keyword in query for keyword in keywords):
                module = mod
                break
        module_prompt = SYSTEM_PROMPTS.get(module, SYSTEM_PROMPTS['DEFAULT'])
        prompt = f"請用繁體中文詳細回答：{module_prompt}\n\n用戶查詢: {query}"
        # 呼叫 Ollama API
        ollama_url = "https://333d-49-158-216-180.ngrok-free.app/api/generate"
        payload = {
            "model": module if module in OLLAMA_MODELS else OLLAMA_MODELS[0],
            "prompt": prompt,
            "stream": False
        }
        headers = {'Content-Type': 'application/json'}
        resp = requests.post(ollama_url, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            result = resp.json()
            response_text = result.get('response', '')
        elif resp.status_code == 429:
            return jsonify({'error': 'Ollama API 流量已用盡，請聯絡管理員。'}), 429
        else:
            return jsonify({'error': f'AI服務錯誤({resp.status_code})', 'msg': resp.text}), 500
        response_time = time.time() - start_time
        user = session.get('user', {})
        is_admin = user.get('role') == 'admin'
        return jsonify({
            'success': True,
            'query': query,
            'response': response_text,
            'module': module,
            'ai_model': OLLAMA_MODEL_DISPLAY_NAMES.get(payload['model'], payload['model']),
            'response_time': round(response_time, 2),
            'timestamp': datetime.now().isoformat(),
        })
    except Exception as e:
        logger.error(f"AI 查詢失敗: {str(e)}")
        return jsonify({'error': '查詢處理失敗', 'msg': 'Query processing failed', 'details': str(e)}), 500

@app.route('/history', methods=['GET', 'DELETE'])
@login_required()
def query_history_api():
    """查詢歷史 API"""
    global query_history  # 僅在這裡宣告一次
    if request.method == 'GET':
        # 獲取查詢參數
        user = request.args.get('user')
        module = request.args.get('module')
        limit = int(request.args.get('limit', 50))
        
        # 過濾歷史記錄
        filtered_history = query_history
        if user:
            filtered_history = [h for h in filtered_history if h['user'] == user]
        if module:
            filtered_history = [h for h in filtered_history if h['module'] == module]
        
        # 限制返回數量
        filtered_history = filtered_history[-limit:]
        
        return jsonify({
            'history': filtered_history,
            'total': len(filtered_history),
            'timestamp': datetime.now().isoformat()
        })
    
    elif request.method == 'DELETE':
        # 刪除歷史記錄
        data = request.get_json()
        history_id = data.get('id') if data else None
        
        if history_id:
            # 刪除指定記錄
            query_history = [h for h in query_history if h['id'] != history_id]
        else:
            # 清空所有記錄
            query_history.clear()
        
        return jsonify({
            'success': True,
            'message': '歷史記錄已刪除',
            'remaining_count': len(query_history)
        })

@app.route('/quota')
def quota_check():
    """配額查詢 API"""
    try:
        return jsonify({
            'quota_enabled': False,
            'message': '配額功能已停用，僅使用單一 Gemini API',
            'ai_model': 'gemini-1.5-pro-002',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"配額查詢失敗: {str(e)}")
        return jsonify({
            'error': '配額查詢失敗',
            'details': str(e)
        }), 500

@app.route('/cache/status')
def cache_status():
    """快取狀態查詢 API"""
    try:
        return jsonify({
            'enabled': CACHE_ENABLED,
            'size': len(cache),
            'max_size': CACHE_MAX_SIZE,
            'ttl': CACHE_TTL,
            'usage_percentage': round(len(cache) / CACHE_MAX_SIZE * 100, 2) if CACHE_MAX_SIZE > 0 else 0
        })
    except Exception as e:
        logger.error(f"快取狀態查詢失敗: {str(e)}")
        return jsonify({
            'error': '快取狀態查詢失敗',
            'details': str(e)
        }), 500

@app.route('/cache/clear', methods=['POST'])
@login_required(role='admin')
def clear_cache():
    """清空快取 API（僅管理員）"""
    try:
        global cache, cache_timestamps
        cache.clear()
        cache_timestamps.clear()
        
        return jsonify({
            'success': True,
            'message': '快取已清空',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"清空快取失敗: {str(e)}")
        return jsonify({
            'error': '清空快取失敗',
            'details': str(e)
        }), 500

@app.route('/api_doc')
def api_documentation():
    """API 文檔頁面"""
    return render_template_string(API_DOC_HTML)

@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    data = request.get_json()
    query = data.get('query', '').strip()
    if not query:
        return jsonify({
            'success': False,
            'msg': '請輸入查詢內容',
            'ai_model': 'ollama'
        }), 400
    module_prompt = SYSTEM_PROMPTS.get('DEFAULT')
    prompt = f"請用繁體中文詳細回答：{module_prompt}\n\n用戶查詢: {query}"
    url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    resp = requests.post(url, headers=headers, json=data, timeout=30)
    if resp.status_code == 200:
        result = resp.json()
        try:
            answer = result['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            answer = str(result)
    elif resp.status_code == 429:
        return jsonify({'error': 'API 金鑰流量已用盡，請聯絡管理員更換金鑰。'}), 429
    else:
        return jsonify({'error': f'AI服務錯誤({resp.status_code})', 'msg': resp.text}), 500
    resp_json = {
        'success': True,
        'query': query,
        'response': answer,
        'ai_model': 'ollama'
    }
    if 'user' in session and session['user'].get('role') == 'admin':
        resp_json['api_key'] = GEMINI_API_KEY
    return jsonify(resp_json)

@app.route('/faq', methods=['POST'])
def ai_faq():
    data = request.get_json()
    query = data.get('query', '').strip()
    if not query:
        return jsonify({
            'success': False,
            'msg': '請輸入查詢內容',
            'ai_model': 'ollama'
        }), 400
    module_prompt = SYSTEM_PROMPTS.get('faq', SYSTEM_PROMPTS['DEFAULT'])
    prompt = f"請用繁體中文詳細回答：{module_prompt}\n\n用戶查詢: {query}"
    url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    resp = requests.post(url, headers=headers, json=data, timeout=30)
    if resp.status_code == 200:
        result = resp.json()
        try:
            answer = result['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            answer = str(result)
    elif resp.status_code == 429:
        return jsonify({'error': 'API 金鑰流量已用盡，請聯絡管理員更換金鑰。'}), 429
    else:
        return jsonify({'error': f'AI服務錯誤({resp.status_code})', 'msg': resp.text}), 500
    resp_json = {
        'success': True,
        'query': query,
        'response': answer,
        'ai_model': 'ollama'
    }
    if 'user' in session and session['user'].get('role') == 'admin':
        resp_json['api_key'] = GEMINI_API_KEY
    return jsonify(resp_json)

@app.route('/analyze', methods=['POST'])
def ai_analyze():
    data = request.get_json()
    query = data.get('query', '').strip()
    if not query:
        return jsonify({
            'success': False,
            'msg': '請輸入查詢內容',
            'ai_model': 'ollama'
        }), 400
    module_prompt = SYSTEM_PROMPTS.get('cost', SYSTEM_PROMPTS['DEFAULT'])
    prompt = f"請用繁體中文詳細回答：{module_prompt}\n\n用戶查詢: {query}"
    url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    resp = requests.post(url, headers=headers, json=data, timeout=30)
    if resp.status_code == 200:
        result = resp.json()
        try:
            answer = result['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            answer = str(result)
    elif resp.status_code == 429:
        return jsonify({'error': 'API 金鑰流量已用盡，請聯絡管理員更換金鑰。'}), 429
    else:
        return jsonify({'error': f'AI服務錯誤({resp.status_code})', 'msg': resp.text}), 500
    resp_json = {
        'success': True,
        'query': query,
        'response': answer,
        'ai_model': 'ollama'
    }
    if 'user' in session and session['user'].get('role') == 'admin':
        resp_json['api_key'] = GEMINI_API_KEY
    return jsonify(resp_json)

# 登入API
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if username != "lstjks" or password != "Ss520520":
        return jsonify({
            "success": False,
            "code": 401,
            "error": {
                "msg": "用戶名或密碼錯誤",
                "details": "請確認帳號密碼後再試",
                "suggestion": "如忘記密碼請聯繫管理員"
            },
            "data": None
        })
    session['user'] = {"username": username, "role": "admin"}
    session['last_active'] = datetime.now().isoformat()
    return jsonify({
        "success": True,
        "code": 0,
        "data": {"user": username, "session": dict(session)},
        "error": None
    })

@app.route("/api/login", methods=["GET"])
def api_login_get():
    return jsonify({
        "success": False,
        "code": 405,
        "error": {
            "msg": "僅支援POST方法，請用POST提交JSON格式帳號密碼",
            "details": "請勿用GET或直接瀏覽器網址列呼叫此API",
            "suggestion": "請用Postman、curl或前端AJAX/Fetch發送POST請求"
        },
        "data": None
    })

# 登出API
@app.route('/api/logout', methods=['POST'])
@login_required()
def api_logout():
    session.clear()
    return jsonify({'success': True, 'code': 0, 'data': {'msg': '已登出'}, 'error': None})

# ========== 健康檢查 API ==========
@app.route('/api/health', methods=['GET'])
def api_health():
    # 模型健康檢查（簡單測試每個模型名稱是否在可用清單）
    model_status = {name: '可用' for name in OLLAMA_MODELS}
    # 可擴充為實際 ping Ollama API
    cache_status = {
        'enabled': globals().get('CACHE_ENABLED', False),
        'size': len(globals().get('cache', {})),
        'max_size': globals().get('CACHE_MAX_SIZE', 0),
        'ttl': globals().get('CACHE_TTL', 0)
    }
    return jsonify({
        'system': '智慧瓦斯AI管理系統',
        'status': 'healthy',
        'models': {k: {'display': OLLAMA_MODEL_DISPLAY_NAMES.get(k, k), 'status': v} for k, v in model_status.items()},
        'cache': cache_status,
        'timestamp': datetime.now().isoformat()
    })

# ========== 配額查詢 API ==========
@app.route('/api/quota', methods=['GET'])
def api_quota():
    # 假設配額資訊來自 config 或全域變數
    quota_info = {
        'enabled': globals().get('QUOTA_ENABLED', False),
        'hourly': globals().get('QUOTA_HOURLY', 100),
        'daily': globals().get('QUOTA_DAILY', 1000),
        'monthly': globals().get('QUOTA_MONTHLY', 10000),
        'used_hourly': globals().get('quota_used_hourly', 0),
        'used_daily': globals().get('quota_used_daily', 0),
        'used_monthly': globals().get('quota_used_monthly', 0),
        'cooldown': globals().get('QUOTA_COOLDOWN', 60),
        'timestamp': datetime.now().isoformat()
    }
    quota_info['remaining_hourly'] = quota_info['hourly'] - quota_info['used_hourly']
    quota_info['remaining_daily'] = quota_info['daily'] - quota_info['used_daily']
    quota_info['remaining_monthly'] = quota_info['monthly'] - quota_info['used_monthly']
    return jsonify(quota_info)

# ========== 管理登入狀態查詢 API ==========
@app.route('/api/login_status', methods=['GET'])
def api_login_status():
    user = session.get('user')
    if user:
        return jsonify({
            'logged_in': True,
            'username': user.get('username'),
            'role': user.get('role'),
            'login_time': session.get('last_active'),
            'timestamp': datetime.now().isoformat()
        })
    else:
        return jsonify({
            'logged_in': False,
            'timestamp': datetime.now().isoformat()
        })

# ========== 主程式入口 ==========
if __name__ == '__main__':
    print("=" * 60)
    print("🚀 智慧瓦斯 AI 管理系統 - Jy技術團隊 - 專業瓦斯行管理AI助手")
    print("=" * 60)
    print(f"📡 服務地址: http://localhost:{PORT}")
    print(f"🎯 API 端點: /ai_ask (查詢), /health (健康檢查)")
    print(f"🤖 AI 模型: 董娘的特助")
    print("=" * 60)
    print("💡 使用方式:")
    print(f"   1. 瀏覽器開啟 http://localhost:{PORT}")
    print("   2. 輸入查詢內容即可自動分流到對應模組")
    print("   3. 支援帳務、成本、派工、維修、FAQ等查詢")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=PORT, debug=True) 