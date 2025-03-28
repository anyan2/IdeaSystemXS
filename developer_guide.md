"""
ideaSystemXS 知识库系统 - 开发者文档
"""

# ideaSystemXS 开发者文档

## 目录
1. 项目概述
2. 系统架构
3. 模块说明
4. 数据库设计
5. 开发环境设置
6. 构建指南
7. 扩展指南

## 1. 项目概述

ideaSystemXS 是一个基于 Python 和 PyQt6 开发的个人知识库系统，旨在提供快速记录、整理和分析想法的功能。系统采用模块化设计，支持AI辅助分析，并提供美观的用户界面。

### 核心功能
- 全局快捷键调用输入窗口
- 数据库存储想法
- 图形化管理界面
- AI智能处理
- 离线工作能力

### 技术栈
- **前端**：PyQt6
- **后端**：Python 3.8+
- **数据库**：SQLite (关系型数据库), ChromaDB (向量数据库)
- **AI集成**：OpenAI API

## 2. 系统架构

系统采用分层架构设计，确保各组件之间的高度解耦和可维护性。

### 架构层次
1. **核心层**：提供基础功能和服务
2. **数据层**：处理数据存储和检索
3. **业务逻辑层**：实现业务规则和流程
4. **AI服务层**：提供AI相关功能
5. **UI层**：提供用户界面
6. **系统集成层**：处理与操作系统的交互

### 模块间通信
- 采用事件驱动模式，通过事件系统进行模块间通信
- 使用依赖注入模式，减少模块间的直接依赖
- 采用单例模式管理全局资源

## 3. 模块说明

### 核心模块 (core)
- **app_manager.py**: 应用程序生命周期管理
- **config_manager.py**: 配置管理
- **event_system.py**: 事件系统

### 数据模块 (data)
- **database_manager.py**: SQLite数据库管理
- **vector_db_manager.py**: 向量数据库管理

### 业务逻辑模块 (business)
- **idea_manager.py**: 想法管理
- **tag_manager.py**: 标签管理
- **search_engine.py**: 搜索引擎
- **schedule_manager.py**: 定时任务管理

### AI服务模块 (ai)
- **ai_service.py**: AI服务接口
- **embedding_generator.py**: 向量嵌入生成
- **idea_analyzer.py**: 想法分析
- **ideas_summarizer.py**: 想法总结
- **reminder_system.py**: 提醒系统
- **ai_query_console.py**: AI查询控制台

### UI模块 (ui)
- **main_window.py**: 主窗口
- **input_window.py**: 输入窗口
- **settings_window.py**: 设置窗口
- **idea_management.py**: 想法管理界面
- **tag_management.py**: 标签管理界面
- **search_widget.py**: 搜索界面
- **theme_manager.py**: 主题管理
- **ui_utils.py**: UI工具函数
- **theme_animation.py**: 动画效果
- **ai_config.py**: AI配置界面

### 系统集成模块 (system_integration)
- **hotkey_manager.py**: 全局快捷键管理
- **system_tray.py**: 系统托盘
- **notification_manager.py**: 通知管理

### 工具模块 (utils)
- 各种通用工具函数

## 4. 数据库设计

### SQLite数据库
系统使用SQLite作为关系型数据库，存储结构化数据。

#### 主要表结构
- **ideas**: 存储想法基本信息
  - id: INTEGER PRIMARY KEY
  - title: TEXT
  - content: TEXT
  - created_at: TIMESTAMP
  - updated_at: TIMESTAMP
  - is_archived: BOOLEAN

- **tags**: 存储标签信息
  - id: INTEGER PRIMARY KEY
  - name: TEXT
  - created_at: TIMESTAMP

- **idea_tags**: 想法和标签的关联表
  - id: INTEGER PRIMARY KEY
  - idea_id: INTEGER (外键)
  - tag_id: INTEGER (外键)

- **reminders**: 存储提醒信息
  - id: INTEGER PRIMARY KEY
  - idea_id: INTEGER (外键)
  - remind_time: TIMESTAMP
  - remind_reason: TEXT
  - is_completed: BOOLEAN

- **ai_conversations**: 存储AI对话历史
  - id: INTEGER PRIMARY KEY
  - query: TEXT
  - response: TEXT
  - timestamp: TIMESTAMP

### 向量数据库 (ChromaDB)
系统使用ChromaDB作为向量数据库，存储文本嵌入向量，支持相似度搜索。

#### 主要集合
- **ideas_embeddings**: 存储想法的向量嵌入
  - id: 与SQLite中的idea.id对应
  - embedding: 向量嵌入
  - metadata: 包含想法的标题、创建时间等元数据

## 5. 开发环境设置

### 环境要求
- Python 3.8+
- pip 包管理器
- Git (可选，用于版本控制)

### 设置步骤

1. **克隆代码库**
   ```bash
   git clone https://github.com/yourusername/ideaSystemXS.git
   cd ideaSystemXS
   ```

2. **创建虚拟环境**
   ```bash
   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   
   # Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **初始化配置**
   ```bash
   # 复制示例配置文件
   cp config.example.json config.json
   # 编辑配置文件
   # 根据需要修改配置
   ```

5. **运行开发版本**
   ```bash
   python src/main.py
   ```

## 6. 构建指南

### Windows构建

1. **使用提供的构建脚本**
   ```bash
   # 设置环境
   setup-env.bat
   
   # 构建应用
   build-app.bat
   ```

2. **手动构建**
   ```bash
   # 安装PyInstaller
   pip install pyinstaller
   
   # 构建应用
   pyinstaller --name=ideaSystemXS --windowed --icon=resources/icon.ico --add-data="resources;resources" src/main.py
   ```

### Linux构建

1. **使用提供的构建脚本**
   ```bash
   # 设置环境
   ./setup-env.sh
   
   # 构建应用
   ./build-app.sh
   ```

2. **手动构建**
   ```bash
   # 安装PyInstaller
   pip install pyinstaller
   
   # 构建应用
   pyinstaller --name=ideaSystemXS --windowed --icon=resources/icon.png --add-data="resources:resources" src/main.py
   ```

## 7. 扩展指南

### 添加新功能

1. **确定功能所属模块**
   根据功能性质，确定应该扩展哪个模块。

2. **实现功能**
   在相应模块中添加新的类或方法。

3. **注册事件**
   如果新功能需要与其他模块交互，使用事件系统注册相应的事件。

4. **更新UI**
   如果新功能需要UI交互，在UI模块中添加相应的界面元素。

### 自定义AI服务

系统默认使用OpenAI API，但可以通过以下步骤自定义AI服务：

1. **修改ai_service.py**
   实现自定义的AI服务接口。

2. **更新embedding_generator.py**
   如果需要使用不同的嵌入模型，更新嵌入生成逻辑。

3. **配置服务**
   在配置文件中更新AI服务的相关配置。

### 添加新的数据存储方式

如果需要支持新的数据存储方式，可以按照以下步骤进行扩展：

1. **创建新的数据管理器**
   实现与新存储方式交互的管理器类。

2. **实现数据接口**
   确保新的数据管理器实现了与现有系统兼容的接口。

3. **更新配置**
   在配置系统中添加新存储方式的相关配置项。

4. **集成到现有系统**
   在app_manager.py中初始化新的数据管理器，并在相关模块中使用。

---

本文档提供了ideaSystemXS项目的技术概览和开发指南。如有任何问题或需要进一步的技术支持，请联系项目维护者。
