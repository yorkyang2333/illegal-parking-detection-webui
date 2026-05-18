# 基于多模态大模型的校园返校时段车辆违停感知与优化研究 Web UI

## 项目简介

这是一个基于 Vue 3 + Flask 的前后端分离应用，用于车辆违停感知分析。通过集成 SAM 3（Segment Anything Model 3）进行车辆分割追踪与违停判定，结合阿里云 DashScope（Qwen-VL）进行车牌识别，最终由 Qwen 生成详细的违停报告。

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
- **SAM 3** - Meta 视频分割追踪模型（车辆检测与违停判定）
- **DashScope** - 阿里云 AI 模型 API（Qwen-VL 车牌识别 + Qwen 报告生成）
- **OpenCV** - 视频帧提取与图像裁剪
- **Flask-CORS** - 跨域支持

## 分析流水线

```
上传视频 → SAM 3 车辆追踪+违停判定 → QVQ 车牌识别 → Qwen 报告生成
```

1. **上传视频**：上传监控视频文件到后端
2. **车辆追踪**：SAM 3 对视频进行分割追踪，检测所有车辆并判定违停（静止超过5秒）
3. **车牌识别**：基于 SAM 3 的追踪结果，提取违停车辆最佳帧并裁剪，发送给 Qwen-VL 进行车牌 OCR
4. **报告生成**：Qwen 综合追踪数据和车牌识别结果，生成完整违停报告

## 快速开始

### 方法一：一键启动（推荐）

```bash
./run.sh
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
- Python 3.10–3.13
- DashScope API Key
- （可选）CUDA 12.6+ GPU 用于 SAM 3 本地推理

#### 2. 配置后端

```bash
cd backend

# 创建 .env 文件
cat > .env << EOF
DASHSCOPE_API_KEY=your_dashscope_key
GEMINI_API_KEY=your_gemini_key
SAM3_SERVICE_URL=http://localhost:8100
SAM3_LOCAL=false
EOF

# 创建虚拟环境并安装依赖
python3 -m venv venv
source venv/bin/activate
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

#### 4.（可选）部署 SAM 3 服务

SAM 3 需要 CUDA GPU。在 GPU 服务器上：

```bash
# 安装 SAM 3
conda create -n sam3 python=3.12
conda activate sam3
pip install torch==2.10.0 torchvision --index-url https://download.pytorch.org/whl/cu128
git clone https://github.com/facebookresearch/sam3.git
cd sam3 && pip install -e .

# 启动 SAM 3 服务
cd backend/sam3_service
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8100
```

如果 SAM 3 服务不可用，系统会自动使用 Mock 模式生成模拟数据，流水线仍可完整运行。

## 获取 API Key

### DashScope（必需）
1. 访问 [阿里云灵积官网](https://dashscope.aliyun.com)
2. 注册并登录账号
3. 创建 API Key
4. 将 Key 添加到 `backend/.env` 文件的 `DASHSCOPE_API_KEY`

### Gemini（可选，仅聊天模式使用）
1. 访问 [Google AI Studio](https://aistudio.google.com)
2. 创建 API Key
3. 将 Key 添加到 `backend/.env` 文件的 `GEMINI_API_KEY`

## 使用流程

1. **上传视频**：在分析页面上传监控视频
2. **自动分析**：系统自动执行 SAM 3 追踪 → 车牌识别 → 报告生成
3. **查看报告**：实时流式显示分析结果，包含违停车辆信息、车牌号和处罚建议

## 项目结构

```
WebUI/
├── backend/                # Flask 后端
│   ├── app.py             # 主应用（API 路由）
│   ├── video_utils.py     # 视频帧提取与裁剪工具
│   ├── sam3_service/      # SAM 3 推理模块
│   │   ├── predictor.py   # SAM 3 封装（含 Mock 模式）
│   │   ├── app.py         # 独立 FastAPI 服务（GPU 部署用）
│   │   └── requirements.txt
│   ├── routes/auth.py     # 认证路由
│   ├── models.py          # 数据库模型
│   ├── database.py        # 数据库初始化
│   ├── requirements.txt   # Python 依赖
│   ├── uploads/           # 上传文件存储
│   └── .env               # 环境变量（需自行创建）
│
├── frontend/              # Vue 3 前端
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── stores/        # Pinia 状态管理
│   │   ├── composables/   # Composition API 工具
│   │   ├── components/    # Vue 组件
│   │   └── assets/        # 样式和资源
│   ├── vite.config.ts     # Vite 配置
│   └── package.json       # Node 依赖
│
├── run.sh                 # 一键启动脚本
└── README.md              # 本文件
```

## 核心功能

- ✅ **SAM 3 车辆追踪** - 基于视频分割模型的车辆检测与轨迹追踪
- ✅ **自动违停判定** - 车辆静止超过5秒自动标记为违停
- ✅ **车牌 OCR** - 基于 Qwen-VL 的真实帧裁剪车牌识别
- ✅ **SSE 流式响应** - 实时显示分析进度和结果
- ✅ **Markdown 渲染** - 格式化输出报告
- ✅ **Mock 模式** - 无 GPU 环境下可用模拟数据完整测试流水线
- ✅ **类型安全** - 完整的 TypeScript 支持
- ✅ **前后端分离** - 独立开发部署

## 开发指南

### 前端开发

```bash
cd frontend
npm run dev       # 开发服务器（热重载）
npm run build     # 生产构建（含类型检查）
```

### 后端开发

```bash
cd backend
source venv/bin/activate
python app.py     # Flask 调试模式，端口 5001
```

### SAM 3 开发

开发环境（macOS/无 GPU）下，SAM 3 自动使用 Mock 模式，无需额外配置。Mock 模式会生成模拟的车辆追踪数据（第一辆车始终为违停车辆），方便调试完整流水线。

生产环境需在 GPU 服务器上部署 `backend/sam3_service/app.py`，并在 `.env` 中配置 `SAM3_SERVICE_URL`。

## 常见问题

### 1. SAM 3 服务不可用
系统会自动回退到 Mock 模式，流水线仍可正常运行。如需真实推理，请确保 GPU 服务器上的 SAM 3 服务已启动。

### 2. 车牌识别失败
确保 `DASHSCOPE_API_KEY` 已配置且有 Qwen-VL 模型的调用权限。

### 3. 端口被占用
- 前端：修改 `frontend/vite.config.ts` 中的 `server.port`
- 后端：修改 `backend/app.py` 中的 `app.run(port=...)`

### 4. 依赖安装失败
- 前端：删除 `frontend/node_modules` 和 `package-lock.json`，重新 `npm install`
- 后端：使用虚拟环境 `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`

## 许可证

本项目仅供学习研究使用。

## 贡献

欢迎提交 Issue 和 Pull Request！
