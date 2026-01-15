"""
后端 API 集成测试

用于测试所有主要API端点的功能和健壮性
"""

import pytest
import json
from datetime import datetime, timedelta
from httpx import AsyncClient
import asyncio


@pytest.fixture
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
class TestHealthCheck:
    """健康检查测试"""

    async def test_health_endpoint(self, client: AsyncClient):
        """测试健康检查端点"""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data

    async def test_root_endpoint(self, client: AsyncClient):
        """测试根端点"""
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data


@pytest.mark.asyncio
class TestMarketAPI:
    """市场数据API测试"""

    async def test_get_market_index_default(self, client: AsyncClient):
        """测试获取默认市场指数"""
        response = await client.get("/api/market/index")
        
        assert response.status_code == 200
        data = response.json()
        assert "code" in data
        assert data["code"] == "sh.000001"
        assert "data" in data

    async def test_get_market_index_custom_days(self, client: AsyncClient):
        """测试获取市场指数 (自定义天数)"""
        response = await client.get("/api/market/index?days=30&code=sz.000001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "sz.000001"

    async def test_get_market_index_invalid_days(self, client: AsyncClient):
        """测试无效的回溯天数"""
        # 0天应该被拒绝
        response = await client.get("/api/market/index?days=0")
        
        assert response.status_code == 400

    async def test_get_hs300_list(self, client: AsyncClient):
        """测试获取沪深300列表"""
        today = datetime.today().strftime("%Y-%m-%d")
        response = await client.get(f"/api/market/hs300-list?date={today}")
        
        assert response.status_code == 200
        data = response.json()
        assert "date" in data
        assert "stocks" in data
        assert "total" in data

    async def test_get_market_status(self, client: AsyncClient):
        """测试获取市场状态"""
        response = await client.get("/api/market/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "date" in data
        assert "is_trading_day" in data
        assert "timestamp" in data


@pytest.mark.asyncio
class TestScanAPI:
    """扫描API测试"""

    async def test_scan_test_pool(self, client: AsyncClient):
        """测试扫描测试股票池"""
        today = datetime.today().strftime("%Y-%m-%d")
        request_data = {
            "date": today,
            "strategies": ["ma"],
            "pool_type": "test",
        }
        
        response = await client.post("/api/scan/", json=request_data)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/x-ndjson"
        
        # 解析NDJSON流
        lines = response.text.strip().split("\n")
        assert len(lines) > 0
        
        # 验证第一行是元数据
        first = json.loads(lines[0])
        assert first["type"] == "meta"
        assert "total" in first

    async def test_scan_with_multiple_strategies(self, client: AsyncClient):
        """测试多策略扫描"""
        today = datetime.today().strftime("%Y-%m-%d")
        request_data = {
            "date": today,
            "strategies": ["ma", "vol"],
            "pool_type": "test",
        }
        
        response = await client.post("/api/scan/", json=request_data)
        
        assert response.status_code == 200

    async def test_scan_invalid_strategies(self, client: AsyncClient):
        """测试无效策略列表"""
        today = datetime.today().strftime("%Y-%m-%d")
        request_data = {
            "date": today,
            "strategies": [],  # 空列表应该被拒绝
            "pool_type": "test",
        }
        
        response = await client.post("/api/scan/", json=request_data)
        
        assert response.status_code == 422  # Validation error

    async def test_scan_invalid_date_format(self, client: AsyncClient):
        """测试无效的日期格式"""
        request_data = {
            "date": "2024-13-01",  # 无效月份
            "strategies": ["ma"],
            "pool_type": "test",
        }
        
        response = await client.post("/api/scan/", json=request_data)
        
        assert response.status_code == 422

    async def test_scan_custom_pool(self, client: AsyncClient):
        """测试自定义股票池扫描"""
        today = datetime.today().strftime("%Y-%m-%d")
        request_data = {
            "date": today,
            "strategies": ["ma"],
            "pool_type": "custom",
            "custom_pool": ["sh.600519", "sh.600000"],
        }
        
        response = await client.post("/api/scan/", json=request_data)
        
        assert response.status_code == 200

    async def test_scan_status(self, client: AsyncClient):
        """测试扫描服务状态"""
        response = await client.get("/api/scan/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


@pytest.mark.asyncio
class TestErrorHandling:
    """错误处理测试"""

    async def test_404_not_found(self, client: AsyncClient):
        """测试404错误"""
        response = await client.get("/api/nonexistent")
        
        assert response.status_code == 404

    async def test_invalid_method(self, client: AsyncClient):
        """测试无效的HTTP方法"""
        response = await client.post("/api/market/index")
        
        assert response.status_code == 405

    async def test_invalid_json(self, client: AsyncClient):
        """测试无效的JSON"""
        response = await client.post(
            "/api/scan/",
            content="not json",
            headers={"Content-Type": "application/json"},
        )
        
        assert response.status_code == 422


@pytest.mark.asyncio
class TestPerformance:
    """性能测试"""

    async def test_concurrent_requests(self, client: AsyncClient):
        """测试并发请求处理"""
        tasks = []
        for i in range(5):
            task = client.get("/health")
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        for response in responses:
            assert response.status_code == 200

    async def test_large_scan_response(self, client: AsyncClient):
        """测试大规模扫描响应"""
        today = datetime.today().strftime("%Y-%m-%d")
        request_data = {
            "date": today,
            "strategies": ["ma"],
            "pool_type": "test",
        }
        
        response = await client.post(
            "/api/scan/",
            json=request_data,
            timeout=60.0,  # 增加超时
        )
        
        assert response.status_code == 200
        
        # 验证流式响应的完整性
        lines = response.text.strip().split("\n")
        last = json.loads(lines[-1])
        assert last["type"] == "done"
