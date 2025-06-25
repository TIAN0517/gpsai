#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧瓦斯 AI 管理系統 - FastAPI Web 服務器
提供 RESTful API 接口
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import uvicorn
import json
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 導入我們的 AI 系統
from gas_ai_system import GasAISystem, PromptRouter

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 FastAPI 應用
app = FastAPI(
    title="智慧瓦斯 AI 管理系統",
    description="專為瓦斯行設計的 AI 輔助決策系統",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境中應該限制具體域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 安全認證
security = HTTPBearer()

# 初始化 AI 系統
ai_system = GasAISystem()

# Pydantic 模型
class QueryRequest(BaseModel):
    """查詢請求模型"""
    query: str = Field(..., description="用戶查詢內容", example="幫我查王小明現在欠多少錢？")
    context: Optional[Dict[str, Any]] = Field(None, description="額外上下文資訊")

class QueryResponse(BaseModel):
    """查詢回應模型"""
    success: bool = Field(..., description="查詢是否成功")
    data: Dict[str, Any] = Field(..., description="查詢結果")
    timestamp: str = Field(..., description="回應時間戳")
    processing_time: Optional[float] = Field(None, description="處理時間（秒）")

class SystemStatus(BaseModel):
    """系統狀態模型"""
    status: str = Field(..., description="系統狀態")
    modules: List[str] = Field(..., description="可用模組列表")
    cache_size: int = Field(..., description="快取大小")
    uptime: str = Field(..., description="運行時間")
    timestamp: str = Field(..., description="狀態檢查時間")

class BatchQueryRequest(BaseModel):
    """批量查詢請求模型"""
    queries: List[str] = Field(..., description="查詢列表", min_items=1, max_items=10)
    priority: Optional[str] = Field("normal", description="處理優先級")

class BatchQueryResponse(BaseModel):
    """批量查詢回應模型"""
    results: List[Dict[str, Any]] = Field(..., description="查詢結果列表")
    total_queries: int = Field(..., description="總查詢數")
    successful_queries: int = Field(..., description="成功查詢數")
    processing_time: float = Field(..., description="總處理時間")

# 認證依賴
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """驗證 API Token"""
    token = credentials.credentials
    # 這裡應該實現實際的 token 驗證邏輯
    # 目前使用簡單的環境變數檢查
    expected_token = os.getenv("API_TOKEN", "demo_token")
    if token != expected_token:
        raise HTTPException(status_code=401, detail="無效的 API Token")
    return token

# API 路由

@app.get("/", tags=["根路徑"])
async def root():
    """根路徑 - 系統資訊"""
    return {
        "message": "智慧瓦斯 AI 管理系統",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", tags=["健康檢查"])
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "modules": list(ai_system.router.modules.keys())
    }

@app.get("/status", response_model=SystemStatus, tags=["系統狀態"])
async def get_system_status():
    """獲取系統狀態"""
    status = ai_system.get_system_status()
    return SystemStatus(**status)

@app.post("/query", response_model=QueryResponse, tags=["AI 查詢"])
async def process_query(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token)
):
    """處理單一 AI 查詢"""
    start_time = datetime.now()
    
    try:
        # 處理查詢
        result = ai_system.process_query(request.query)
        
        # 計算處理時間
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # 背景任務：記錄查詢日誌
        background_tasks.add_task(log_query, request.query, result, processing_time)
        
        return QueryResponse(
            success=True,
            data=result,
            timestamp=datetime.now().isoformat(),
            processing_time=processing_time
        )
    
    except Exception as e:
        logger.error(f"處理查詢時發生錯誤: {e}")
        raise HTTPException(status_code=500, detail=f"處理查詢失敗: {str(e)}")

@app.post("/batch-query", response_model=BatchQueryResponse, tags=["批量查詢"])
async def process_batch_queries(
    request: BatchQueryRequest,
    token: str = Depends(verify_token)
):
    """處理批量 AI 查詢"""
    start_time = datetime.now()
    results = []
    successful_count = 0
    
    for query in request.queries:
        try:
            result = ai_system.process_query(query)
            results.append({
                "query": query,
                "success": True,
                "result": result
            })
            successful_count += 1
        except Exception as e:
            results.append({
                "query": query,
                "success": False,
                "error": str(e)
            })
    
    processing_time = (datetime.now() - start_time).total_seconds()
    
    return BatchQueryResponse(
        results=results,
        total_queries=len(request.queries),
        successful_queries=successful_count,
        processing_time=processing_time
    )

# 模組特定 API

@app.get("/api/accounting/customer/{customer_name}/balance", tags=["帳務管理"])
async def get_customer_balance(
    customer_name: str,
    token: str = Depends(verify_token)
):
    """查詢客戶欠款"""
    result = ai_system.router.modules['accounting'].check_customer_balance(customer_name)
    return {
        "customer_name": customer_name,
        "balance_info": result,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/accounting/overdue", tags=["帳務管理"])
async def get_overdue_customers(
    days: int = 30,
    token: str = Depends(verify_token)
):
    """獲取逾期客戶列表"""
    result = ai_system.router.modules['accounting'].get_overdue_customers(days)
    return {
        "overdue_days": days,
        "customers": result,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/cost/analysis", tags=["成本分析"])
async def analyze_costs(
    period: str,
    token: str = Depends(verify_token)
):
    """分析成本趨勢"""
    result = ai_system.router.modules['cost_analysis'].analyze_profit_trend(period)
    return {
        "period": period,
        "analysis": result,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/dispatch/optimize", tags=["派工管理"])
async def optimize_dispatch(
    date: str,
    token: str = Depends(verify_token)
):
    """優化派工安排"""
    result = ai_system.router.modules['dispatch'].optimize_dispatch(date)
    return {
        "date": date,
        "optimization": result,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/maintenance/schedule", tags=["維修管理"])
async def schedule_maintenance(
    location: str,
    token: str = Depends(verify_token)
):
    """安排維修任務"""
    result = ai_system.router.modules['maintenance'].schedule_maintenance(location)
    return {
        "location": location,
        "schedule": result,
        "timestamp": datetime.now().isoformat()
    }

# 快取管理 API

@app.get("/cache/stats", tags=["快取管理"])
async def get_cache_stats(token: str = Depends(verify_token)):
    """獲取快取統計資訊"""
    cache = ai_system.router.cache
    return {
        "cache_size": len(cache.cache),
        "ttl": cache.ttl,
        "timestamp": datetime.now().isoformat()
    }

@app.delete("/cache/clear", tags=["快取管理"])
async def clear_cache(token: str = Depends(verify_token)):
    """清除快取"""
    ai_system.router.cache.cache.clear()
    return {
        "message": "快取已清除",
        "timestamp": datetime.now().isoformat()
    }

# 工具函數

def log_query(query: str, result: Dict[str, Any], processing_time: float):
    """記錄查詢日誌（背景任務）"""
    log_entry = {
        "query": query,
        "result_type": result.get("type", "unknown"),
        "processing_time": processing_time,
        "timestamp": datetime.now().isoformat()
    }
    logger.info(f"查詢日誌: {json.dumps(log_entry, ensure_ascii=False)}")

# 錯誤處理

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局異常處理"""
    logger.error(f"未處理的異常: {exc}")
    return {
        "error": "系統內部錯誤",
        "message": str(exc),
        "timestamp": datetime.now().isoformat()
    }

# 啟動腳本

if __name__ == "__main__":
    # 檢查環境變數
    api_token = os.getenv("API_TOKEN", "demo_token")
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"=== 智慧瓦斯 AI 管理系統 ===")
    print(f"API Token: {api_token}")
    print(f"服務地址: http://{host}:{port}")
    print(f"API 文檔: http://{host}:{port}/docs")
    print("=" * 40)
    
    # 啟動服務器
    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    ) 