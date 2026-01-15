# OmniAlpha 启动指南 (Startup Guide)

## 概述

本文档详细说明如何快速启动 OmniAlpha 项目的各种配置。

---

## ⭐ 推荐方式: 一键启动 (最简单)

在项目根目录直接执行统一启动脚本：

```bash
python run.py
```

或显式指定启动所有服务：

```bash
python run.py --mode all
```

### 预期输出

```
============================================================
   OmniAlpha 项目启动器 (前后端一体化)
============================================================

🚀 启动后端服务 (FastAPI)...
   端口: http://localhost:8000
   文档: http://localhost:8000/docs
✓ 后端服务启动成功
🎨 启动前端服务 (React + Vite)...
   端口: http://localhost:5173
   📦 首次运行，正在安装依赖...
✓ 前端服务启动成功

============================================================
✓ 服务启动完成！
============================================================

📍 访问地址:
   • 前端工作台: http://localhost:5173
   • 后端 API: http://localhost:8000
   • API 文档: http://localhost:8000/docs

⌨️  按 Ctrl+C 停止所有服务
============================================================
```

---

## 🔧 其他启动模式

### 仅启动后端 API

```bash
python run.py --mode backend
```

后端 API 将在 `http://localhost:8000` 运行。

**主要端点:**
- `GET /` - 根端点
- `GET /health` - 健康检查
- `GET /docs` - Swagger UI 文档
- `GET /api/market/index` - 市场指数数据
- `GET /api/market/hs300-list` - 沪深300列表
- `POST /api/scan/` - 股票扫描 (流式)

### 仅启动前端应用

```bash
python run.py --mode frontend
```

前端应用将在 `http://localhost:5173` 运行 (Vite 开发服务器)。

**注意:** 前端需要后端 API 正常运行才能完全工作。建议同时启动后端。

### 启动 Streamlit 轻量级界面

```bash
python run.py --mode web
```

Streamlit 界面将在 `http://localhost:8501` 运行。

**用途:** 快速验证选股逻辑，无需前端开发环境。

---

## 🚀 手动启动 (如果遇到run.py问题)

如果 `run.py` 无法执行，您也可以手动在不同终端启动各个服务：

### 终端 1: 启动后端

```bash
cd /Users/hhd/Desktop/test/OmniAlpha
uvicorn backend.app.main:app --reload --port 8000
```

### 终端 2: 启动前端

```bash
cd /Users/hhd/Desktop/test/OmniAlpha/frontend
npm run dev
```

### 终端 3 (可选): 启动 Streamlit

```bash
cd /Users/hhd/Desktop/test/OmniAlpha
streamlit run web_ui.py
```

---

## 🧪 测试

启动后，您可以进行以下测试来验证安装：

### 1. 测试后端健康检查

```bash
curl http://localhost:8000/health
```

预期响应：
```json
{
  "status": "ok",
  "timestamp": "2026-01-16T10:30:00.123456"
}
```

### 2. 测试获取市场指数

```bash
curl "http://localhost:8000/api/market/index?code=sh.000001&days=30"
```

### 3. 测试前端可访问性

在浏览器打开：`http://localhost:5173`

您应该看到 OmniAlpha 的主界面。

### 4. 运行自动化测试

```bash
# 运行所有单元测试
pytest tests/unit/ -v

# 运行特定测试
pytest tests/unit/test_technical_strategies.py::TestMovingAverageStrategy -v

# 查看覆盖率报告
pytest --cov=. --cov-report=html
# 在 htmlcov/index.html 中查看
```

---

## 📋 故障排除 (Troubleshooting)

### 问题 1: `ModuleNotFoundError: No module named 'fastapi'`

**解决方案:** 确保安装了所有依赖

```bash
pip install -r requirements.txt
```

### 问题 2: `npm: command not found`

**解决方案:** 安装 Node.js 和 npm

- 访问 https://nodejs.org/
- 下载并安装 LTS 版本

### 问题 3: 前端显示空白页或 API 连接失败

**解决方案:** 
1. 确保后端 API 正在运行 (检查 `http://localhost:8000/health`)
2. 检查浏览器控制台 (F12) 是否有错误信息
3. 清除浏览器缓存并重新刷新

### 问题 4: 端口 8000 或 5173 已被占用

**解决方案:** 更改端口或停止占用该端口的进程

```bash
# 查看占用 8000 端口的进程 (macOS/Linux)
lsof -i :8000
# 查看占用 5173 端口的进程
lsof -i :5173
```

或在启动时指定其他端口：

```bash
# 后端使用不同端口
uvicorn backend.app.main:app --reload --port 8001

# 前端修改 vite.config.ts 中的端口设置
```

### 问题 5: Baostock 数据连接失败

**解决方案:** 
1. 检查网络连接
2. 确认 Baostock 服务可用
3. 检查数据提供者配置 (data/settings.json)

---

## 🔄 开发工作流

### 修改后端代码

1. 编辑 `backend/app/` 下的文件
2. 由于启用了 `--reload`，Uvicorn 会自动重新加载
3. 无需手动重启

### 修改前端代码

1. 编辑 `frontend/src/` 下的文件
2. Vite 会自动热更新 (HMR)
3. 浏览器会自动刷新

### 添加新依赖

**Python:**
```bash
pip install <package>
pip freeze > requirements.txt
```

**Node.js:**
```bash
cd frontend
npm install <package>
```

---

## 📊 监控运行状态

### 查看日志

启动时的日志会显示在终端。您可以看到：
- 请求日志 (method, url, status, time)
- 错误日志 (错误堆栈跟踪)
- 应用启动/关闭事件

### API 文档

启动后，访问 `http://localhost:8000/docs` 查看 Swagger UI 文档，可以：
- 查看所有可用的 API 端点
- 测试 API 请求
- 查看请求/响应示例

---

## ✅ 检查清单

启动完成后，确保以下项目都正常工作：

- [ ] 后端 API 启动在 `http://localhost:8000`
- [ ] 前端应用启动在 `http://localhost:5173`
- [ ] 可以访问 API 文档 `http://localhost:8000/docs`
- [ ] 前端页面可正常加载
- [ ] 网络请求可以成功 (查看浏览器开发者工具)
- [ ] 没有控制台错误信息

---

## 🎓 后续步骤

完成启动后，您可以：

1. **探索 UI** - 访问 `http://localhost:5173` 了解功能
2. **测试 API** - 使用 Swagger UI 测试各个端点
3. **查看日志** - 检查终端输出了解请求处理情况
4. **修改代码** - 编辑源代码并查看实时更新
5. **运行测试** - 执行 `pytest` 确保代码质量

---

## 📞 获得帮助

如遇到问题：

1. 查看本指南的 **故障排除** 部分
2. 检查项目的 `README.md`
3. 查看源代码中的注释和文档字符串
4. 提交 GitHub Issue (如果是 bug)

---

**最后更新: 2026年1月16日**
