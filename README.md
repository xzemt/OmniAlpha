# OmniAlpha: 全场景智能量化研究与交易引擎

**OmniAlpha** 是一个专为 A 股市场设计的模块化量化交易平台。它不仅集成了实时行情获取、历史回测和模拟盘执行，更核心的突破在于其**双循环架构**：内置基于遗传算法与强化学习的 **AlphaGen 因子挖掘工厂**，并预留了 **LLM（大语言模型）** 接口，用于语义情感分析与策略自动化生成。

**新架构 (v2.0)**: 采用 **FastAPI (后端)** + **React (前端)** 的前后端分离架构，提供更专业、流畅的交互体验。

## 🌟 核心特性

*   **🖥️ 现代化工作台**: 基于 **React + Tailwind CSS** 打造的全新 Web 界面，支持 AI 智能选股、Alpha 因子分析、多策略扫描。
*   **🚀 高性能后端**: 基于 **FastAPI** 的异步 API 服务，支持流式响应（Streaming Response）处理耗时扫描任务。
*   **🛠️ 模块化架构**: 采用依赖倒置设计，Data Provider、Strategy、Engine 高度解耦，方便扩展。
*   **📈 多维度策略**: 内置均线趋势、放量突破、低估值、高换手等多种实战策略，支持自由组合。
*   **🤖 AI 赋能**: 集成 LLM 对话接口，支持自然语言选股 ("帮我找一下最近缩量下跌的股票")。

## 📚 策略库 (Strategy Library)

### 技术面策略 (Technical)
*   **`ma` (均线趋势)**: 捕捉上升通道个股 (Close > MA20 & MA5 > MA20)。
*   **`vol` (放量突破)**: 寻找资金异动 (涨幅 > 2% & 量比 > 1.5)。
*   **`turn` (高换手)**: 筛选市场活跃标的 (换手率 > 5% & 非ST)。

### 基本面策略 (Fundamental)
*   **`pe` (低估值)**: 寻找安全边际 (0 < PE-TTM < 30)。
*   **`growth` (双高增长)**: 挖掘高成长潜力 (净利润同比 > 20%)。
*   **`roe` (高ROE)**: 锁定优质资产 (ROE > 15%)。
*   **`debt` (低负债)**: 规避财务风险 (资产负债率 < 50%)。

---

## 📂 项目结构 (Project Structure)

*(Updated: 2026-01-14)*

```text
BlackOil-OmniAlpha/
├── backend/                # 🐍 **后端服务 (FastAPI)**
│   ├── app/
│   │   ├── api/            # API 路由定义 (market, stock, scan, ai, alpha)
│   │   ├── core/           # 核心配置与工具
│   │   └── main.py         # FastAPI 应用入口
│   ├── core/               # 复用的核心逻辑 (Engine, Strategies)
│   ├── data/               # 数据层 (Baostock Provider)
│   ├── strategies/         # 策略实现层 (Technical, Fundamental)
│   └── alpha/              # 因子挖掘层
├── frontend/               # ⚛️ **前端应用 (React + Vite)**
│   ├── src/
│   │   ├── api/            # API 客户端封装
│   │   ├── components/     # 公共组件 (Layout, Sidebar, Header)
│   │   ├── pages/          # 页面视图 (Home, Technical, Alpha, AI, StockDetail)
│   │   └── ...
│   └── ...
├── data/                   # 💾 **数据存储** (本地缓存的 CSV/Parquet)
├── logs/                   # 📝 **运行日志**
└── README.md               # 📄 项目文档
```

## 🚀 快速开始 (Quick Start)

为了顺利运行 OmniAlpha，请遵循以下详细步骤：

### 1. 环境准备 (Prerequisites)

在开始之前，请确保您的开发环境中已安装以下软件：

*   **Python**: 版本 3.8 或更高。推荐使用 `pyenv` 或 `conda` 进行 Python 版本管理。
*   **Node.js**: 版本 16 或更高。Node.js 环境包含了 `npm` (Node Package Manager)。您也可以使用 `yarn` 或 `pnpm` 作为替代包管理器。

### 2. 后端服务启动 (Backend Service)

后端服务使用 Python 和 FastAPI 构建。

1.  **打开第一个终端**：导航到项目的根目录（即包含 `backend/` 文件夹的目录）。
    ```bash
    # 示例：如果您当前在其他目录，请cd到项目根目录
    cd /Users/comedian/Code/BlackOil-OmniAlpha
    ```
2.  **创建并激活 Python 虚拟环境 (推荐)**：
    ```bash
    python -m venv venv_backend
    source venv_backend/bin/activate # macOS/Linux
    # 或 venv_backend\Scripts\activate # Windows
    ```
3.  **安装 Python 依赖**：
    ```bash
    pip install -r requirements.txt
    ```
4.  **启动 FastAPI 服务**：
    ```bash
    uvicorn backend.app.main:app --reload --port 8000
    ```
    *   `--reload` 参数会在代码文件发生变化时自动重启服务，方便开发。
    *   `--port 8000` 指定服务运行在 8000 端口。
    *   当您看到类似 `Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)` 的输出时，表示后端服务已成功启动。
    *   您可以通过访问 `http://localhost:8000/docs` 查看 API 文档 (Swagger UI)。

### 3. 前端应用启动 (Frontend Application)

前端应用使用 React、Vite 和 Tailwind CSS 构建。

1.  **打开第二个终端**：导航到 `frontend/` 目录。
    ```bash
    # 确保您在项目根目录，然后进入frontend
    cd frontend
    ```
2.  **安装 Node.js 依赖**：
    根据您的偏好，选择以下任一命令安装依赖：
    ```bash
    npm install
    # 或 pnpm install
    # 或 yarn install
    ```
3.  **启动前端开发服务器**：
    ```bash
    npm run dev
    ```
    *   当您看到类似 `ready in ... ms` 并且提示 `Local: http://localhost:5173/` 的输出时，表示前端开发服务器已成功启动。
    *   现在，打开您的浏览器，访问 `http://localhost:5173` 即可打开 OmniAlpha 工作台，并开始使用新的重构页面。

---

## 🏗️ 核心模块 (Core Modules)

### 1. Technical (技术选股)
复刻并增强了原有的筛选逻辑，支持在前端勾选多种策略组合，通过 WebSocket/Stream 实时接收扫描进度与结果。

### 2. Alpha (因子分析)
基于 `alpha/` 目录下的因子库（如 GTJA191），提供因子计算器与分布可视化功能，辅助量化因子挖掘。

### 3. AI (智能助手)
通过 `llm/` 接口对接大语言模型，提供对话式交互体验，支持语义选股与策略解释。

---

## 📅 项目规划 (Roadmap)

*   [x] **Phase 1**: 核心引擎重构与模块化。
*   [x] **Phase 2**: 建立 Data-Alpha-Backtest 分层架构。
*   [x] **Phase 3**: **架构重构**: 迁移至 FastAPI + React 前后端分离架构 (Completed 2026-01-14)。
*   [ ] **Phase 4**: 完善 `BacktestEngine`，实现真实的撮合逻辑与绩效统计。
*   [ ] **Phase 5**: 完善 AI 模块，实现 "Text-to-Strategy" 自动代码生成。

---

## 🤝 贡献与反馈

欢迎提交 Issue 或 Pull Request！
