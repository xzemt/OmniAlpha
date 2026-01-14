# OmniAlpha 重构计划与变更日志

本文档用于记录将 **OmniAlpha** 从 Streamlit 单体应用重构为 **FastAPI (后端) + React (前端)** 分离架构的全过程。

## 1. 重构目标 (Objectives)

*   **解耦**: 将数据处理/策略计算逻辑与界面展示逻辑完全分离。
*   **性能**: 提升大数据量下的响应速度，消除 Streamlit 每次交互重跑脚本的性能瓶颈。
*   **体验**: 使用现代 Web 技术 (React + Tailwind) 构建更专业、交互更流畅的量化工作台。
*   **扩展**: 为未来引入更复杂的交互（如拖拽式策略构建、实时行情推送）打下基础。

## 2. 技术栈 (Tech Stack)

| 模块 | 原有技术 | **新技术** | 说明 |
| :--- | :--- | :--- | :--- |
| **后端** | Python / Streamlit | **Python / FastAPI** | 高性能异步 Web 框架，自动生成 OpenAPI 文档 |
| **前端** | Streamlit UI | **React (Vite + TS)** | 工业级前端框架，使用 TypeScript 保证类型安全 |
| **样式** | Streamlit Native | **Tailwind CSS** | 原子化 CSS 框架，快速构建现代 UI |
| **组件库** | Streamlit Widgets | **shadcn/ui** (推荐) | 基于 Radix UI 的高质量组件库 |
| **图表** | Altair | **Recharts / Lightweight Charts** | 更适合金融数据的交互式图表库 |

---

## 3. 实施路线图 (Roadmap)

### 第一阶段：项目结构重组与后端基础 (Infrastructure & Backend)
- [ ] **1.1 目录结构调整**: 建立 `backend/` 和 `frontend/` 目录，清理根目录。
- [ ] **1.2 FastAPI 初始化**: 配置 `main.py`，设置 CORS，配置 Uvicorn 服务器。
- [ ] **1.3 核心接口迁移 - 基础**: 
    - [ ] 移植大盘数据获取 (`/api/market/index`)
    - [ ] 移植策略列表获取 (`/api/strategies`)
- [ ] **1.4 核心接口迁移 - 扫描**: 
    - [ ] 实现股票扫描接口 (`/api/scan`)，处理长时间运行的任务。
- [ ] **1.5 核心接口迁移 - 个股**: 
    - [ ] 实现个股 K 线与指标数据接口 (`/api/stock/{code}`)。

### 第二阶段：前端工程搭建 (Frontend Setup)
- [ ] **2.1 Vite 项目初始化**: 创建 React + TypeScript 项目。
- [ ] **2.2 样式配置**: 安装并配置 Tailwind CSS。
- [ ] **2.3 基础布局开发**: 开发侧边栏、顶部导航、主内容区域的 Layout 骨架。
- [ ] **2.4 API 客户端封装**: 封装 `axios` 或 `fetch` 请求，统一管理后端接口调用。

### 第三阶段：功能模块实现 (Feature Implementation)
- [ ] **3.1 策略配置面板**: 复刻 Streamlit 的侧边栏，实现日期选择与策略多选功能。
- [ ] **3.2 扫描任务流**: 前端触发扫描 -> 显示进度 -> 展示结果表格。
- [ ] **3.3 结果可视化**: 
    - [ ] 使用 Recharts 实现 PE/PB 分布图。
    - [ ] 实现交互式数据表格 (排序、筛选)。
- [ ] **3.4 个股详情页**: 
    - [ ] 集成 K 线图组件。
    - [ ] 展示个股详细指标对比。

### 第四阶段：收尾与部署 (Finalization)
- [ ] **4.1 清理**: 移除 `web_ui.py` 及相关 Streamlit 依赖。
- [ ] **4.2 文档**: 更新 README.md，补充启动指南。
- [ ] **4.3 测试**: 完整流程测试。

---

## 4. 变更日志 (Change Log)

*记录每次重大的代码变更与进度更新*

| 日期 | 类别 | 修改内容 | 状态 |
| :--- | :--- | :--- | :--- |
| 2026-01-14 | **Plan** | 创建重构计划文档 `REFACTOR_LOG.md` | ✅ 完成 |
| 2026-01-14 | **Init** | (待执行) 创建后端目录结构与 FastAPI 基础配置 | ⏳ 待开始 |
