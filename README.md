# 基于多模态大模型的校园返校时段车辆违停感知与优化研究 Web UI

## 项目简介

这是一个基于 Vue 3 + Flask 的前后端分离应用，用于车辆违停感知分析。通过集成阿里云 DashScope API（Qwen 模型），结合 Gemini 和 QVQ-Max 的分析结果，生成详细的违停报告。

## 技术栈

### 前端
- **Vue 3** - 使用 Composition API
- **TypeScript** - 类型安全
- **Vite** - 快速构建工具
- **Element Plus** - UI 组件库
- **Pinia** - 状态管理
- **Marked** - Markdown 渲染
- **DOMPurify** - XSS 防护

### 后端
- **Flask 3.1.2** - Python Web 框架
- **DashScope** - 阿里云 AI 模型 API
- **Flask-CORS** - 跨域支持

## 快速开始

### 方法一：一键启动（推荐）

#### Unix/Mac/Linux
```bash
./scripts/start.sh
```

#### Windows
```bash
scripts\start.bat
```

启动脚本会自动：
1. 检查 Node.js 和 Python 环境
2. 安装所有依赖
3. 启动后端服务器（端口 5001）
4. 启动前端开发服务器（端口 3000）

访问 http://localhost:3000 使用应用

按 `Ctrl+C` 停止所有服务器

### 方法二：手动启动

#### 1. 环境要求
- Node.js 16+ 和 npm
- Python 3.8+
- DashScope API Key

#### 2. 配置后端

```bash
cd backend

# 创建 .env 文件
echo "DASHSCOPE_API_KEY=your_api_key_here" > .env

# 安装 Python 依赖
pip install -r requirements.txt

# 启动 Flask 服务器
python app.py
```

后端将运行在 http://localhost:5001

#### 3. 配置前端

```bash
cd frontend

# 安装 Node 依赖
npm install

# 启动开发服务器
npm run dev
```

前端将运行在 http://localhost:3000

## 获取 API Key

1. 访问 [阿里云灵积官网](https://dashscope.aliyun.com)
2. 注册并登录账号
3. 创建 API Key
4. 将 Key 添加到 `backend/.env` 文件

## 使用流程

1. **输入页面**：
   - 先使用 [Gemini](https://gemini.google.com) 分析违停情况
   - 使用 QVQ-Max 识别车牌号
   - 将两者结果粘贴到提示词中
   - 点击"运行"按钮

2. **输出页面**：
   - 自动跳转到输出页面
   - 实时流式显示 AI 生成的违停报告
   - 报告包含：车牌号、违停原因、处罚建议

## 项目结构

```
WebUI/
├── backend/              # Flask 后端
│   ├── app.py           # 主应用
│   ├── requirements.txt # Python 依赖
│   ├── .env            # 环境变量（需自行创建）
│   └── frame_cache/    # 缓存目录
│
├── frontend/            # Vue 3 前端
│   ├── public/         # 静态资源
│   ├── src/
│   │   ├── components/ # Vue 组件
│   │   ├── views/      # 页面组件
│   │   ├── stores/     # Pinia 状态管理
│   │   ├── composables/# Composition API 工具
│   │   └── assets/     # 样式和资源
│   ├── vite.config.ts  # Vite 配置
│   └── package.json    # Node 依赖
│
├── scripts/
│   ├── start.sh        # Unix/Mac 启动脚本
│   └── start.bat       # Windows 启动脚本
│
└── README.md           # 本文件
```

## 核心功能

- ✅ **SSE 流式响应** - 实时显示 AI 生成内容
- ✅ **Markdown 渲染** - 格式化输出报告
- ✅ **侧边栏导航** - 悬停展开式设计
- ✅ **状态管理** - Pinia 集中管理应用状态
- ✅ **类型安全** - 完整的 TypeScript 支持
- ✅ **前后端分离** - 独立开发部署
- ✅ **CORS 支持** - 跨域请求配置

## 开发指南

### 前端开发

```bash
cd frontend

# 启动开发服务器（热重载）
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

### 后端开发

```bash
cd backend

# 启动 Flask 服务器（调试模式）
python app.py
```

## 常见问题

### 1. 端口被占用
如果端口 3000 或 5001 被占用，可以修改：
- 前端：`frontend/vite.config.ts` 中的 `server.port`
- 后端：`backend/app.py` 中的 `app.run(port=...)`

### 2. CORS 错误
确保后端已安装 `Flask-CORS` 并正确配置允许的源地址。

### 3. API Key 未配置
检查 `backend/.env` 文件是否存在且包含有效的 `DASHSCOPE_API_KEY`。

### 4. 依赖安装失败
- 前端：尝试删除 `frontend/node_modules` 和 `frontend/package-lock.json`，重新运行 `npm install`
- 后端：尝试使用虚拟环境：`python -m venv venv && source venv/bin/activate`

## 许可证

本项目仅供学习研究使用。

## 贡献

欢迎提交 Issue 和 Pull Request！
