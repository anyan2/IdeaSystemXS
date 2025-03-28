# ideaSystemXS 系统架构设计

## 整体架构

ideaSystemXS采用模块化设计，各模块之间通过明确的接口进行通信，确保高度解耦和鲁棒性。系统分为以下几个主要模块：

### 1. 核心模块 (Core)
- **应用管理器 (AppManager)**: 负责应用程序的生命周期管理，协调各模块之间的通信
- **配置管理器 (ConfigManager)**: 管理应用程序配置，包括用户设置、API密钥等
- **事件系统 (EventSystem)**: 实现基于发布-订阅模式的事件系统，用于模块间通信

### 2. 数据层 (Data Layer)
- **数据库管理器 (DatabaseManager)**: 管理SQLite数据库连接和操作
- **向量数据库管理器 (VectorDBManager)**: 管理向量数据库的连接和操作
- **数据模型 (DataModels)**: 定义系统中使用的数据模型和结构
- **数据访问对象 (DAO)**: 提供对数据库的抽象访问接口

### 3. 业务逻辑层 (Business Logic)
- **想法管理器 (IdeaManager)**: 处理想法的创建、更新、删除和查询
- **标签管理器 (TagManager)**: 管理标签的创建、更新和关联
- **搜索引擎 (SearchEngine)**: 提供基于关键词和向量的搜索功能
- **定时任务管理器 (ScheduleManager)**: 管理定时提醒和任务

### 4. AI服务层 (AI Services)
- **AI管理器 (AIManager)**: 管理AI服务的连接和操作
- **嵌入生成器 (EmbeddingGenerator)**: 生成文本的向量嵌入
- **想法分析器 (IdeaAnalyzer)**: 分析想法内容，提取关键信息
- **关联引擎 (RelationEngine)**: 发现想法之间的关联
- **摘要生成器 (SummaryGenerator)**: 生成想法的摘要和总结

### 5. UI层 (UI Layer)
- **窗口管理器 (WindowManager)**: 管理应用程序的窗口和对话框
- **主窗口 (MainWindow)**: 应用程序的主窗口
- **输入窗口 (InputWindow)**: 用于快速输入想法的窗口
- **设置窗口 (SettingsWindow)**: 用于配置应用程序的窗口
- **UI组件 (UIComponents)**: 可重用的UI组件
- **主题管理器 (ThemeManager)**: 管理应用程序的主题和样式

### 6. 系统集成层 (System Integration)
- **快捷键管理器 (HotkeyManager)**: 管理全局快捷键
- **系统托盘 (SystemTray)**: 管理系统托盘图标和菜单
- **通知管理器 (NotificationManager)**: 管理系统通知

## 模块交互流程

1. **应用启动流程**:
   - AppManager初始化各模块
   - ConfigManager加载配置
   - DatabaseManager和VectorDBManager初始化数据库连接
   - HotkeyManager注册全局快捷键
   - WindowManager创建主窗口
   - SystemTray创建系统托盘图标

2. **想法记录流程**:
   - 用户按下全局快捷键(Ctrl+Alt+I)
   - HotkeyManager捕获快捷键并通知AppManager
   - AppManager指示WindowManager显示InputWindow
   - 用户输入想法并保存
   - InputWindow将想法传递给IdeaManager
   - IdeaManager将想法存储到数据库
   - 如果AI服务可用，AIManager分析想法并生成嵌入向量
   - VectorDBManager将嵌入向量存储到向量数据库

3. **想法管理流程**:
   - 用户打开主窗口
   - MainWindow从IdeaManager获取想法列表
   - 用户可以按时间或关键词排序
   - 用户可以编辑、删除或标记想法
   - 更改通过IdeaManager更新到数据库

4. **AI分析流程**:
   - AIManager定期检查新想法
   - EmbeddingGenerator为想法生成嵌入向量
   - IdeaAnalyzer分析想法内容，提取关键信息
   - RelationEngine发现想法之间的关联
   - SummaryGenerator生成摘要和总结
   - 结果通过IdeaManager更新到数据库

5. **离线工作流程**:
   - ConfigManager检测到AI服务不可用
   - AIManager进入离线模式
   - 系统继续正常运行基本功能
   - 新想法被标记为"待分析"
   - 当AI服务恢复可用时，AIManager处理积压的想法

## 数据流图

```
[用户] <-> [HotkeyManager] <-> [AppManager] <-> [WindowManager] <-> [UI层]
                                    ^
                                    |
                                    v
[AI服务] <-> [AIManager] <-> [业务逻辑层] <-> [数据层] <-> [数据库]
```

## 技术实现考虑

1. **模块解耦**:
   - 使用依赖注入模式
   - 定义清晰的接口
   - 使用事件系统进行松耦合通信

2. **鲁棒性**:
   - 实现全面的错误处理
   - 使用事务确保数据一致性
   - 实现自动恢复机制

3. **性能优化**:
   - 使用连接池管理数据库连接
   - 实现缓存机制减少数据库访问
   - 异步处理耗时操作

4. **UI设计**:
   - 实现毛玻璃效果和苹果风格
   - 使用QSS和自定义绘制实现现代UI
   - 实现流畅的动画和过渡效果
