# 前端架构设计方案

## 一、项目概述

为"试卷讲解Demo"设计一个现代化、可扩展的前端应用，支持试卷处理、PPT生成、相似题生成等核心功能，并为后续功能扩展预留空间。

---

## 二、技术栈选择

### 推荐方案：Vue 3 + TypeScript + Vite

| 技术 | 选择理由 |
|------|----------|
| **Vue 3** | 组合式API、更好的TypeScript支持、性能优秀 |
| **TypeScript** | 类型安全、IDE智能提示、与后端Pydantic模型对应 |
| **Vite** | 极速开发体验、HMR、现代化构建 |
| **Pinia** | Vue官方推荐状态管理、组合式API风格 |
| **Vue Router** | 官方路由、支持路由守卫 |
| **Element Plus** | 成熟的UI组件库、丰富的企业级组件 |
| **Axios** | HTTP客户端、拦截器、请求取消 |
| **TailwindCSS** | 原子化CSS、快速开发、高度可定制 |

### 备选方案：React + TypeScript + Vite

如果团队更熟悉React生态，可选择：
- React 18 + TypeScript
- Zustand/Jotai (状态管理)
- React Router v6
- Ant Design / shadcn/ui

---

## 三、项目目录结构

```
frontend/
├── public/                     # 静态资源
│   └── favicon.ico
├── src/
│   ├── api/                    # API层 - 与后端交互
│   │   ├── index.ts            # Axios实例配置
│   │   ├── types.ts            # API响应类型定义
│   │   ├── auth.ts             # 认证相关API
│   │   ├── exams.ts            # 试卷管理API
│   │   ├── tasks.ts            # 任务管理API
│   │   ├── pipeline.ts         # 管道API
│   │   ├── questions.ts        # 相似题API
│   │   └── files.ts            # 文件上传API
│   │
│   ├── assets/                 # 静态资源（会被构建处理）
│   │   ├── images/
│   │   └── styles/
│   │       └── global.css
│   │
│   ├── components/             # 通用组件
│   │   ├── common/             # 基础UI组件
│   │   │   ├── AppHeader.vue
│   │   │   ├── AppSidebar.vue
│   │   │   ├── AppFooter.vue
│   │   │   ├── LoadingSpinner.vue
│   │   │   ├── EmptyState.vue
│   │   │   └── ErrorBoundary.vue
│   │   │
│   │   ├── business/           # 业务组件
│   │   │   ├── FileUploader.vue        # 文件上传组件
│   │   │   ├── TaskProgress.vue        # 任务进度组件
│   │   │   ├── QuestionCard.vue        # 题目卡片组件
│   │   │   ├── PipelineStatus.vue      # 管道状态组件
│   │   │   └── SimilarQuestionList.vue # 相似题列表组件
│   │   │
│   │   └── layout/             # 布局组件
│   │       ├── MainLayout.vue
│   │       ├── AuthLayout.vue
│   │       └── BlankLayout.vue
│   │
│   ├── composables/            # 组合式函数（Hooks）
│   │   ├── useAuth.ts          # 认证逻辑
│   │   ├── useTask.ts          # 任务管理
│   │   ├── usePolling.ts       # 轮询逻辑
│   │   ├── useNotification.ts  # 通知提示
│   │   └── useFileUpload.ts    # 文件上传
│   │
│   ├── router/                 # 路由配置
│   │   ├── index.ts
│   │   └── guards.ts           # 路由守卫
│   │
│   ├── stores/                 # Pinia状态管理
│   │   ├── index.ts
│   │   ├── auth.ts             # 用户认证状态
│   │   ├── exam.ts             # 试卷状态
│   │   ├── task.ts             # 任务状态
│   │   └── ui.ts               # UI状态（侧边栏、主题等）
│   │
│   ├── types/                  # TypeScript类型定义
│   │   ├── api.ts              # API响应类型
│   │   ├── exam.ts             # 试卷相关类型
│   │   ├── task.ts             # 任务相关类型
│   │   └── user.ts             # 用户相关类型
│   │
│   ├── utils/                  # 工具函数
│   │   ├── request.ts          # 请求封装
│   │   ├── storage.ts          # 本地存储
│   │   ├── format.ts           # 格式化工具
│   │   └── constants.ts        # 常量定义
│   │
│   ├── views/                  # 页面视图
│   │   ├── auth/               # 认证相关页面
│   │   │   ├── LoginView.vue
│   │   │   └── RegisterView.vue
│   │   │
│   │   ├── dashboard/          # 仪表盘
│   │   │   └── DashboardView.vue
│   │   │
│   │   ├── exam/               # 试卷管理
│   │   │   ├── ExamListView.vue
│   │   │   ├── ExamDetailView.vue
│   │   │   └── ExamCreateView.vue
│   │   │
│   │   ├── pipeline/           # 管道处理
│   │   │   ├── PipelineView.vue
│   │   │   └── PipelineResultView.vue
│   │   │
│   │   ├── task/               # 任务管理
│   │   │   └── TaskListView.vue
│   │   │
│   │   ├── question/           # 相似题
│   │   │   └── SimilarQuestionView.vue
│   │   │
│   │   └── error/              # 错误页面
│   │       └── NotFoundView.vue
│   │
│   ├── App.vue                 # 根组件
│   └── main.ts                 # 入口文件
│
├── .env                        # 环境变量
├── .env.development            # 开发环境变量
├── .env.production             # 生产环境变量
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

---

## 四、核心页面设计

### 4.1 页面路由规划

| 路由 | 页面 | 说明 |
|------|------|------|
| `/login` | 登录页 | 用户登录 |
| `/register` | 注册页 | 用户注册 |
| `/dashboard` | 仪表盘 | 概览、快捷操作 |
| `/exams` | 试卷列表 | 查看所有试卷 |
| `/exams/create` | 创建试卷 | 上传PDF处理 |
| `/exams/:id` | 试卷详情 | 查看题目、生成PPT |
| `/exams/:id/questions` | 题目管理 | 编辑题目内容 |
| `/pipeline` | 管道处理 | 一键处理流程 |
| `/tasks` | 任务列表 | 查看所有任务状态 |
| `/questions/similar` | 相似题生成 | 生成相似题目 |

### 4.2 核心页面功能

#### 仪表盘 (Dashboard)
- 统计概览（试卷数量、任务状态）
- 最近处理的试卷
- 快捷操作入口
- 系统状态

#### 试卷创建页 (ExamCreate)
- 文件上传（拖拽/点击）
- 处理选项配置
- 实时进度显示
- 结果预览

#### 试卷详情页 (ExamDetail)
- 试卷基本信息
- 题目列表展示
- 单题操作（编辑、生成相似题）
- PPT生成/下载
- 导出功能

#### 管道处理页 (Pipeline)
- 完整流程可视化
- 各阶段状态展示
- 错误处理与重试
- 结果下载

---

## 五、状态管理设计

### 5.1 Auth Store（认证状态）

```typescript
// stores/auth.ts
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
}

// Actions
- login(username, password)
- register(userData)
- logout()
- fetchCurrentUser()
- checkAuth()
```

### 5.2 Exam Store（试卷状态）

```typescript
// stores/exam.ts
interface ExamState {
  exams: Exam[];
  currentExam: Exam | null;
  questions: Question[];
  loading: boolean;
  pagination: Pagination;
}

// Actions
- fetchExams(page, limit)
- fetchExam(id)
- createExam(data)
- deleteExam(id)
- fetchQuestions(examId)
- updateQuestion(questionId, data)
```

### 5.3 Task Store（任务状态）

```typescript
// stores/task.ts
interface TaskState {
  tasks: Task[];
  currentTask: Task | null;
  pollingTasks: string[];  // 正在轮询的任务ID
}

// Actions
- fetchTasks(filters)
- fetchTask(id)
- startPolling(taskId)
- stopPolling(taskId)
- deleteTask(id)
```

---

## 六、API层设计

### 6.1 Axios实例配置

```typescript
// api/index.ts
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器 - 添加Token
api.interceptors.request.use(config => {
  const token = useAuthStore().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器 - 错误处理
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Token过期，跳转登录
      router.push('/login');
    }
    return Promise.reject(error);
  }
);
```

### 6.2 API模块示例

```typescript
// api/pipeline.ts
export const pipelineApi = {
  // 完整管道处理
  fullPipeline: async (file: File, options: PipelineOptions) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('use_animation', String(options.useAnimation));
    formData.append('title', options.title || '试卷评讲');
    
    return api.post<PipelineFullResponse>('/pipeline/full', formData);
  },
  
  // 获取管道状态
  getPipelineStatus: (pipelineId: string) => 
    api.get<PipelineStatusResponse>(`/pipeline/${pipelineId}`),
};
```

---

## 七、组件设计规范

### 7.1 组件命名规范

- **页面组件**: `XxxView.vue` (如 `LoginView.vue`)
- **业务组件**: 功能描述 (如 `QuestionCard.vue`)
- **基础组件**: `App`前缀 (如 `AppHeader.vue`)

### 7.2 组件Props定义

```typescript
// 使用TypeScript定义Props
interface Props {
  examId: string;
  showActions?: boolean;
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  showActions: true,
  loading: false
});
```

### 7.3 事件命名

```typescript
// 使用kebab-case
const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void;
  (e: 'submit', data: FormData): void;
  (e: 'cancel'): void;
}>();
```

---

## 八、扩展性设计

### 8.1 为后续功能预留的空间

| 预留模块 | 说明 |
|----------|------|
| **用户中心** | `/profile` 路由、个人信息管理 |
| **题库管理** | `/question-bank` 独立题库系统 |
| **班级管理** | `/classes` 班级、学生管理 |
| **作业系统** | `/homework` 布置作业、批改 |
| **数据统计** | `/analytics` 学习数据分析 |
| **AI助手** | `/assistant` AI对话助手 |
| **设置中心** | `/settings` 系统配置 |

### 8.2 模块化扩展机制

```typescript
// router/index.ts - 支持动态路由注册
const routes: RouteRecordRaw[] = [
  // 基础路由
  ...authRoutes,
  ...examRoutes,
  ...taskRoutes,
  
  // 预留扩展路由
  // ...questionBankRoutes,
  // ...classRoutes,
  // ...homeworkRoutes,
];
```

### 8.3 插件化组件设计

```typescript
// components/business/index.ts
// 业务组件统一导出，支持按需加载
export { default as FileUploader } from './FileUploader.vue';
export { default as TaskProgress } from './TaskProgress.vue';
export { default as QuestionCard } from './QuestionCard.vue';

// 后续新增组件只需在此添加导出
```

---

## 九、开发规范

### 9.1 Git提交规范

```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 重构
perf: 性能优化
test: 测试相关
chore: 构建/工具相关
```

### 9.2 代码风格

- 使用ESLint + Prettier
- 遵循Vue官方风格指南
- TypeScript严格模式

### 9.3 环境变量

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8080/api/v1
VITE_APP_TITLE=试卷讲解系统（开发）

# .env.production
VITE_API_BASE_URL=/api/v1
VITE_APP_TITLE=试卷讲解系统
```

---

## 十、实施步骤

### 阶段一：基础搭建（1-2天）
1. 初始化Vue 3 + TypeScript + Vite项目
2. 配置TailwindCSS、Element Plus
3. 搭建项目目录结构
4. 配置ESLint、Prettier

### 阶段二：核心功能（3-5天）
1. 实现API层和Axios配置
2. 实现认证模块（登录、注册、路由守卫）
3. 实现状态管理（Pinia stores）
4. 实现核心页面布局

### 阶段三：业务页面（3-5天）
1. 仪表盘页面
2. 试卷列表、详情页
3. 管道处理页面
4. 任务管理页面

### 阶段四：完善优化（2-3天）
1. 错误处理与提示
2. 加载状态优化
3. 响应式适配
4. 性能优化

---

## 十一、技术亮点

1. **TypeScript全栈类型安全** - 前后端类型对应
2. **组合式API** - 逻辑复用、代码组织清晰
3. **Pinia状态管理** - 轻量、TypeScript友好
4. **模块化设计** - 易于扩展新功能
5. **轮询机制** - 任务状态实时更新
6. **文件上传** - 拖拽、进度显示
7. **错误边界** - 优雅的错误处理

---

## 十二、依赖清单

```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "axios": "^1.6.0",
    "element-plus": "^2.4.0",
    "@element-plus/icons-vue": "^2.3.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "typescript": "^5.3.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "eslint": "^8.55.0",
    "prettier": "^3.1.0",
    "@vitejs/plugin-vue": "^4.5.0"
  }
}
```
