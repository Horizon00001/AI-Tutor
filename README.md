# AI-Tutor (AI 教学辅助系统)

这是一个基于 FastAPI 开发的 AI 教学辅助系统后端，旨在通过集成 DeepSeek 和 MinerU 等 AI 能力，为教师提供试卷处理、课件生成、相似题推荐及 AI 互动等功能。

## 主要功能

- **试卷处理 (OCR & 结构化)**: 集成 MinerU 提取试卷内容，并利用 DeepSeek 进行题目识别与解析。
- **相似题推荐**: 基于题目内容搜索并生成相似类型的练习题，助力个性化学习。
- **课件生成 (PPT)**: 自动根据题目内容或教学材料生成结构化的 PPT 演示文稿。
- **AI 互动问答**: 提供多轮对话能力，支持 AI 助教场景，解答教学过程中的问题。
- **收藏与题库管理**: 支持题目的收藏、分类管理及错题集导出。
- **试卷管理**: 完整的试卷库管理功能，支持 PDF 上传、处理及结果预览。

## 技术栈

- **后端框架**: FastAPI (Python 3.9+)
- **AI 模型**: DeepSeek (深度求索)
- **OCR 引擎**: MinerU (云端提取)
- **数据库**: SQLite (轻量级本地存储)
- **文档处理**: python-pptx (PPT 生成)

## 快速开始

### 1. 环境准备

确保您的系统中已安装 Python 3.9 或更高版本。

### 2. 克隆项目

```bash
git clone https://github.com/your-username/AI-Tutor.git
cd AI-Tutor
```

### 3. 安装依赖

建议使用虚拟环境：

```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r backend/requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 并重命名为 `.env`，填入您的 API 密钥：

```bash
cp .env.example .env
```

**配置项说明：**

- `API_KEY`: 您的 DeepSeek API 密钥。
- `token`: 您的 MinerU API 访问令牌。

### 5. 运行后端服务

```bash
cd backend
python app.py
```

服务启动后，您可以通过以下地址访问：

- **主页**: `http://localhost:8080`
- **交互式 API 文档 (Swagger)**: `http://localhost:8080/docs`

## 项目结构

```text
AI-Tutor/
├── backend/            # 后端核心代码
│   ├── api/            # 路由与控制器 (FastAPI Routes)
│   ├── services/       # 业务逻辑层 (DeepSeek, MinerU, PPT 等)
│   ├── utils/          # 工具类与配置
│   ├── data/           # SQLite 数据库文件 (已忽略)
│   ├── uploads/        # 上传文件存储 (已忽略)
│   ├── output/         # 生成结果存储 (已忽略)
│   ├── test/           # 测试用例与脚本
│   └── app.py          # 服务入口文件
├── .env.example        # 环境变量示例
├── .gitignore          # Git 忽略文件配置
└── README.md           # 项目说明文档
```

## 注意事项

- **API 限制**: 使用过程中请注意 DeepSeek 和 MinerU 的调用额度。
- **文件清理**: `backend/temp` 和 `backend/output` 目录下的临时文件会定期自动清理（如已实现）。

## 贡献指南

欢迎提交 Issue 或 Pull Request 来完善本项目。

## 许可证

[MIT License](LICENSE) (建议根据需要添加)
