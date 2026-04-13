# 试卷讲解Demo - 前端设计计划

## 一、项目定位与核心价值

### 1.1 项目目标
为教师提供一个**试卷智能讲解平台**，核心功能是将PDF试卷自动转化为可讲解的PPT课件，并支持相似题生成、题目收藏等教学辅助功能。

### 1.2 核心用户场景
1. **上传试卷** → 自动识别题目、生成讲解PPT
2. **查看试卷** → 浏览题目、编辑讲解内容
3. **生成相似题** → 针对薄弱知识点生成练习题
4. **收藏管理** → 建立个人题库、整理教学资源

### 1.3 设计理念
- **简洁高效**：教师时间宝贵，界面要直观易用
- **渐进式披露**：核心功能突出，高级功能按需展示
- **视觉清晰**：数学公式、题目内容要清晰可读
- **移动友好**：支持平板端查看（但核心操作在PC）

---

## 二、技术栈与架构

### 2.1 技术选型

**主推方案：Vue 3 + TypeScript + Vite**

| 技术 | 选择理由 |
|------|----------|
| **Vue 3 (Composition API)** | 逻辑复用性强，与后端API对应 |
| **TypeScript** | 类型安全，与后端Pydantic模型对应 |
| **Vite** | 开发体验好，热更新快 |
| **Element Plus** | 企业级UI，组件丰富 |
| **Pinia** | 状态管理，轻量易用 |
| **TailwindCSS** | 快速定制样式 |

**备选方案：React + TypeScript**
- 如果团队更熟悉React生态

### 2.2 项目结构

```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── api/                    # API层
│   │   ├── index.ts           # Axios实例
│   │   ├── types.ts           # API类型
│   │   ├── auth.ts            # 认证
│   │   ├── pipeline.ts        # 管道处理
│   │   ├── exams.ts           # 试卷管理
│   │   ├── questions.ts       # 相似题
│   │   └── collections.ts    # 收藏
│   │
│   ├── components/            # 组件
│   │   ├── common/            # 通用组件
│   │   │   ├── AppHeader.vue
│   │   │   ├── AppSidebar.vue
│   │   │   ├── Loading.vue
│   │   │   └── Empty.vue
│   │   │
│   │   ├── exam/              # 试卷相关
│   │   │   ├── QuestionCard.vue
│   │   │   ├── QuestionList.vue
│   │   │   ├── ExamUpload.vue
│   │   │   └── PipelineProgress.vue
│   │   │
│   │   └── collection/        # 收藏相关
│   │       ├── FolderTree.vue
│   │       ├── CollectionCard.vue
│   │       └── TagEditor.vue
│   │
│   ├── composables/           # 组合式函数
│   │   ├── useTask.ts         # 任务轮询
│   │   ├── useUpload.ts       # 文件上传
│   │   └── useNotification.ts # 消息提示
│   │
│   ├── stores/                # 状态管理
│   │   ├── auth.ts
│   │   ├── exam.ts
│   │   └── collection.ts
│   │
│   ├── views/                 # 页面
│   │   ├── HomeView.vue       # 首页/仪表盘
│   │   ├── ExamListView.vue   # 试卷列表
│   │   ├── ExamDetailView.vue # 试卷详情
│   │   ├── ExamCreateView.vue # 创建试卷
│   │   ├── CollectionView.vue # 收藏管理
│   │   └── LoginView.vue      # 登录
│   │
│   ├── router/
│   │   └── index.ts
│   │
│   ├── App.vue
│   └── main.ts
│
├── .env
├── package.json
└── vite.config.ts
```

---

## 三、页面设计

### 3.1 页面架构

```
/                           → 首页仪表盘
/login                      → 登录页
/exams                      → 试卷列表
/exams/create               → 创建试卷（上传PDF）
/exams/:id                  → 试卷详情
/exams/:id/questions/:qid    → 题目详情/编辑
/collections                → 收藏管理
/collections/:folderId      → 文件夹内收藏
/settings                   → 设置（预留）
```

### 3.2 首页设计（Dashboard）

**设计思路**：教师登录后首先看到的是工作台，快速开始核心任务。

```
┌─────────────────────────────────────────────────────────┐
│  [Logo] 试卷讲解系统                    [用户] [设置]    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │   📄 上传试卷    │  │   📋 试卷列表    │              │
│  │   快速开始       │  │   继续工作       │              │
│  └─────────────────┘  └─────────────────┘              │
│                                                         │
│  最近处理                                               │
│  ┌─────────────────────────────────────────────────┐   │
│  │ [试卷1] C++期末考试  |  已完成  |  2024-01-15   │   │
│  │ [试卷2] 计网习题集    |  处理中  |  2024-01-14   │   │
│  │ [试卷3] 高数模拟题    |  已完成  |  2024-01-13   │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  快捷操作                                               │
│  • [生成相似题]  • [查看收藏]  • [题库管理]            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**功能要点**：
- **上传按钮**：拖拽上传PDF，显示处理进度
- **试卷列表**：显示最近处理的试卷，支持快速访问
- **快捷操作**：生成相似题、查看收藏等

### 3.3 创建试卷页（ExamCreate）

**设计思路**：简洁的上传流程，实时展示处理状态。

```
┌─────────────────────────────────────────────────────────┐
│  ← 返回   创建试卷                                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │                                                  │   │
│  │        📁 拖拽PDF文件到这里                      │   │
│  │        或点击选择文件                           │   │
│  │                                                  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  处理选项                                               │
│  [✓] 生成动画效果                                      │
│  标题：[试卷评讲________________]                      │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  处理进度                                       │   │
│  │  ████████████████████░░░░░░░░░░  70%          │   │
│  │                                                 │   │
│  │  ✓ 文件上传完成                                 │   │
│  │  ✓ 题目识别中...                               │   │
│  │  ○ 内容修复中                                  │   │
│  │  ○ 生成PPT                                     │   │
│  │                                                 │   │
│  │  [查看结果]  [返回列表]                        │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**功能要点**：
- **拖拽上传**：支持拖拽和点击上传
- **进度可视化**：每个阶段的状态清晰展示
- **错误处理**：失败时提供重试选项
- **结果预览**：完成后可预览生成的PPT

### 3.4 试卷详情页（ExamDetail）

**设计思路**：题目列表 + 快速操作，强调查看和编辑。

```
┌─────────────────────────────────────────────────────────┐
│  ← 返回   C++期末考试（A卷）            [编辑] [导出]   │
├──────────┬──────────────────────────────────────────────┤
│          │                                              │
│  题目导航 │  题目 1                                     │
│          │  ─────────────────────────────────────────  │
│  • 1     │  下面有关构造函数的描述中，错误的是（    ）  │
│  • 2     │                                              │
│  • 3     │  A. 构造函数有返回值                        │
│  • 4     │  B. 构造函数可以重载                        │
│  • 5     │  C. 构造函数可以缺省参数                    │
│  ...     │  D. 构造函数可以由用户显式调用              │
│          │                                              │
│  ──────  │  答案：D                                    │
│  统计    │                                              │
│  总题数 5 │  讲解：                                    │
│  已讲解 2 │  本题考查构造函数的特点...                  │
│  未讲解 3 │                                              │
│          │  ─────────────────────────────────────────  │
│  ──────  │  [生成相似题]  [收藏]  [编辑]               │
│          │                                              │
│  [生成全部│                                              │
│  相似题]  │                                              │
│          │                                              │
└──────────┴──────────────────────────────────────────────┘
```

**功能要点**：
- **题目导航**：侧边栏快速跳转
- **题目卡片**：显示题目内容、答案、讲解
- **操作按钮**：生成相似题、收藏题目
- **统计信息**：显示已讲解/未讲解数量

### 3.5 收藏管理页（CollectionView）

**设计思路**：树形文件夹 + 收藏列表，类似文件管理器。

```
┌─────────────────────────────────────────────────────────┐
│  收藏管理                            [新建文件夹] [+新建收藏] │
├──────────────┬──────────────────────────────────────────┤
│              │                                          │
│  文件夹      │  全部收藏 (12)          [搜索____] [标签筛选] │
│              │                                          │
│  📁 全部     │  ┌────────────────────────────────────┐  │
│  📁 C++相关  │  │ C++构造函数题  [选择题] [重要]    │  │
│    📁 基础   │  │ 来源：21年期末考试 | 收藏于 1-15   │  │
│    📁 进阶   │  │ 讲解要点：构造函数不能有返回值...  │  │
│  📁 计网     │  │ [查看] [编辑] [生成相似题]         │  │
│  📁 数学     │  └────────────────────────────────────┘  │
│              │                                          │
│  标签        │  ┌────────────────────────────────────┐  │
│  🏷️ 重要     │  │ 计网数据链路层题  [填空题]         │  │
│  🏷️ 易错     │  │ 来源：计网习题集 | 收藏于 1-14     │  │
│  🏷️ 经典     │  └────────────────────────────────────┘  │
│              │                                          │
└──────────────┴──────────────────────────────────────────┘
```

**功能要点**：
- **文件夹树**：支持多级文件夹
- **收藏列表**：卡片式展示，支持拖拽移动
- **标签系统**：多标签管理
- **批量操作**：选中多个进行移动/删除

---

## 四、核心功能详解

### 4.1 试卷上传与处理流程

**流程图**：

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  上传   │ ──→ │ MinerU  │ ──→ │ DeepSeek│ ──→ │   PPT   │
│  PDF    │     │  提取   │     │   修复   │     │  生成   │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
    │               │               │               │
    ↓               ↓               ↓               ↓
  文件验证      题目识别        内容修正        讲解PPT
```

**前端实现**：
1. **上传组件**：拖拽 + 点击，支持PDF格式验证
2. **进度展示**：实时轮询任务状态，显示每个阶段
3. **错误处理**：失败阶段高亮显示重试按钮
4. **结果展示**：完成后跳转到试卷详情或直接下载PPT

### 4.2 题目管理与编辑

**功能点**：
- **题目展示**：支持LaTeX公式渲染
- **答案显示**：可折叠/展开
- **讲解编辑**：富文本编辑器
- **单题操作**：生成相似题、收藏、标记

**组件设计**：
```vue
<!-- QuestionCard.vue -->
<template>
  <div class="question-card">
    <div class="question-header">
      <span class="question-number">题目 {{ index + 1 }}</span>
      <el-tag v-if="question.type">{{ question.type }}</el-tag>
    </div>
    
    <div class="question-content" v-html="renderLatex(question.content)"></div>
    
    <div class="answer-section">
      <el-collapse>
        <el-collapse-item title="答案">
          <div v-html="renderLatex(question.answer)"></div>
        </el-collapse-item>
        <el-collapse-item title="讲解">
          <div>{{ question.analysis || '暂无讲解' }}</div>
        </el-collapse-item>
      </el-collapse>
    </div>
    
    <div class="actions">
      <el-button @click="generateSimilar">生成相似题</el-button>
      <el-button @click="collect">收藏</el-button>
      <el-button @click="edit">编辑</el-button>
    </div>
  </div>
</template>
```

### 4.3 相似题生成

**交互设计**：
- **单题生成**：点击按钮，设置生成数量和难度
- **批量生成**：选择多题，一次性生成
- **进度展示**：任务列表，显示每个题目的生成状态
- **结果展示**：相似题列表，可下载或直接加入题库

**弹窗设计**：
```
┌─────────────────────────────────────┐
│  生成相似题                         │
├─────────────────────────────────────┤
│  原题：构造函数相关                  │
│                                     │
│  生成数量：[3 ▼]                    │
│  难度调整：○ 简单 ○ 适中 ● 困难    │
│                                     │
│  ☐ 保留知识点                      │
│                                     │
│  [取消]            [开始生成]       │
└─────────────────────────────────────┘
```

### 4.4 收藏管理

**功能点**：
- **文件夹管理**：创建、删除、重命名、移动
- **收藏操作**：收藏、取消收藏、移动到文件夹
- **标签管理**：添加、删除、筛选标签
- **备注功能**：添加教学备注、常见错误等

---

## 五、状态管理设计

### 5.1 Exam Store

```typescript
interface ExamState {
  exams: Exam[];
  currentExam: Exam | null;
  questions: Question[];
  loading: boolean;
  processingStatus: ProcessingStatus | null;
}

interface ProcessingStatus {
  pipelineId: string;
  stages: {
    upload: StageStatus;
    mineru: StageStatus;
    deepseek: StageStatus;
    ppt: StageStatus;
  };
  currentStage: string;
  progress: number;
}
```

### 5.2 Collection Store

```typescript
interface CollectionState {
  folders: Folder[];
  collections: Collection[];
  currentFolder: Folder | null;
  tags: Tag[];
  selectedItems: string[];
}
```

---

## 六、API层设计

### 6.1 Axios配置

```typescript
// api/index.ts
import axios from 'axios';
import { ElMessage } from 'element-plus';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api/v1',
  timeout: 60000,
});

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录');
      router.push('/login');
    }
    return Promise.reject(error);
  }
);
```

### 6.2 Pipeline API

```typescript
// api/pipeline.ts
export const pipelineApi = {
  fullPipeline: async (file: File, options: PipelineOptions) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('use_animation', String(options.useAnimation));
    formData.append('title', options.title || '试卷评讲');
    
    return api.post('/pipeline/full', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  
  getStatus: (pipelineId: string) => 
    api.get(`/pipeline/${pipelineId}`),
};
```

---

## 七、组件清单

| 组件 | 说明 | 优先级 |
|------|------|--------|
| AppHeader | 顶部导航栏 | P0 |
| AppSidebar | 侧边栏（可折叠） | P0 |
| FileUploader | 文件上传组件 | P0 |
| PipelineProgress | 处理进度展示 | P0 |
| QuestionCard | 题目卡片 | P0 |
| QuestionList | 题目列表 | P0 |
| FolderTree | 文件夹树形结构 | P1 |
| CollectionCard | 收藏卡片 | P1 |
| SimilarQuestionList | 相似题列表 | P1 |
| TagEditor | 标签编辑器 | P2 |
| Loading | 加载状态 | P0 |
| Empty | 空状态 | P1 |

---

## 八、实施计划

### 阶段一：基础搭建（2天）

1. **项目初始化**
   - 创建Vue 3 + TypeScript + Vite项目
   - 安装依赖（Element Plus、TailwindCSS、Pinia）
   - 配置ESLint、Prettier

2. **项目结构**
   - 搭建目录结构
   - 配置路由
   - 配置Axios

3. **登录模块**
   - 登录页面
   - 认证状态管理

### 阶段二：核心功能（5天）

1. **首页仪表盘**（1天）
   - 快捷操作入口
   - 最近试卷列表
   - 统计信息

2. **试卷上传**（2天）
   - 文件上传组件
   - 管道处理进度
   - 错误处理

3. **试卷列表/详情**（2天）
   - 试卷列表展示
   - 题目卡片组件
   - 题目导航

### 阶段三：扩展功能（3天）

1. **相似题生成**（1天）
   - 生成弹窗
   - 结果展示

2. **收藏管理**（2天）
   - 文件夹管理
   - 收藏CRUD
   - 标签系统

### 阶段四：优化完善（2天）

1. **体验优化**
   - 加载状态优化
   - 错误提示优化
   - 响应式适配

2. **性能优化**
   - 懒加载路由
   - 组件按需加载

---

## 九、技术亮点

1. **TypeScript全栈类型对应**
   - 前端类型与后端Pydantic模型对应
   - API响应类型化

2. **实时任务状态**
   - 轮询机制展示处理进度
   - WebSocket预留（后续可升级）

3. **LaTeX公式渲染**
   - KaTeX或MathJax
   - 支持复杂数学公式

4. **文件上传体验**
   - 拖拽上传
   - 实时进度
   - 格式验证

5. **响应式设计**
   - 支持PC、平板
   - 侧边栏可折叠

---

## 十、依赖清单

```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "axios": "^1.6.0",
    "element-plus": "^2.4.0",
    "@element-plus/icons-vue": "^2.3.0",
    "katex": "^0.16.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "typescript": "^5.3.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "@vitejs/plugin-vue": "^4.5.0"
  }
}
```

---

## 十一、总结

这个前端设计的核心理念是**简洁高效、以用户为中心**：

1. **操作路径短**：从上传到生成PPT只需几步操作
2. **状态清晰**：每个阶段的状态都有明确展示
3. **容错性好**：失败有明确的提示和重试选项
4. **扩展性强**：预留了收藏管理、题库等扩展空间

设计遵循**渐进式披露**原则，首页展示核心功能，复杂功能按需展开，保证界面的简洁性。
