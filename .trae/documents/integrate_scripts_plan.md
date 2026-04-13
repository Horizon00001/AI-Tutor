# 根目录脚本整合到 Services 层计划

## 目标

将根目录下的独立脚本（pdf\_extractor.py、fix\_with\_deepseek.py、generate\_ppt.py、add\_anim.py）完全整合到 services 层，使根目录不再保留这些脚本文件。

## 现状分析

### 根目录现有脚本

1. **pdf\_extractor.py** - MinerU PDF提取工具
2. **fix\_with\_deepseek.py** - DeepSeek JSON修复工具
3. **generate\_ppt.py** - PPT生成工具
4. **add\_anim.py** - PPT动画添加工具
5. **run\_pipeline.py** - 完整流程脚本

### 当前 Services 层实现

* mineru\_service.py - 已存在，但调用外部 pdf\_extractor.py

* deepseek\_service.py - 已存在，但逻辑与 fix\_with\_deepseek.py 重复

* ppt\_service.py - 已存在，但调用外部 generate\_ppt.py 和 add\_anim.py

## 整合方案

### 阶段1: 整合 MinerU 提取功能

1. 将 pdf\_extractor.py 的核心逻辑完全移入 mineru\_service.py
2. 删除根目录 pdf\_extractor.py
3. 确保所有功能（上传、轮询、下载、解压）都在服务内完成

### 阶段2: 整合 DeepSeek 修复功能

1. 将 fix\_with\_deepseek.py 的核心逻辑完全移入 deepseek\_service.py
2. 删除根目录 fix\_with\_deepseek.py
3. 统一 Question 数据模型定义

### 阶段3: 整合 PPT 生成功能

1. 将 generate\_ppt.py 的核心逻辑完全移入 ppt\_service.py
2. 将 add\_anim.py 的核心逻辑整合到 ppt\_service.py
3. 删除根目录 generate\_ppt.py 和 add\_anim.py
4. 确保 LaTeX 处理、幻灯片创建等功能内聚

### 阶段4: 整合完整管道功能

1. 将 run\_pipeline.py 的核心逻辑整合到 pipeline.py 路由
2. 删除根目录 run\_pipeline.py
3. 确保管道调用使用内部服务而非外部脚本

### 阶段5: 验证与清理

1. 测试所有 API 端点确保功能正常
2. 验证文件依赖关系
3. 清理冗余代码

## 文件变更清单

### 新增/修改文件

* services/mineru\_service.py - 扩展功能

* services/deepseek\_service.py - 扩展功能

* services/ppt\_service.py - 扩展功能

* services/ppt\_generator.py - 新增（PPT生成核心类）

* api/routes/pipeline.py - 修改调用方式

### 备份并删除文件

* pdf\_extractor.py

* fix\_with\_deepseek.py

* generate\_ppt.py

* add\_anim.py

* run\_pipeline.py

## 依赖处理

* 保留 prompt.txt（DeepSeek提示词）

* 保留 .env（环境变量）

* 确保所有导入路径正确

## 风险与注意事项

1. 确保 PPT 生成的复杂逻辑（LaTeX转换、幻灯片布局）正确迁移
2. 保持动画添加功能完整
3. 确保文件路径处理在整合后仍然正确
4. 保留原有的错误处理和日志输出

