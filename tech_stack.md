# ideaSystemXS 技术栈与依赖

## 核心技术
- **编程语言**: Python 3.10+
- **GUI框架**: PyQt6（用于创建现代化UI界面）
- **数据库**: 
  - SQLite3（内置于Python，用于关系型数据存储）
  - Chroma DB（轻量级向量数据库，用于AI分析）
- **打包工具**: PyInstaller（用于生成Windows可执行文件）

## 主要依赖库

### GUI相关
- **PyQt6**: 主要GUI框架
- **PyQt6-QScintilla**: 用于代码编辑器组件（如果需要）
- **qt-material**: 提供Material设计风格的Qt主题
- **blurwindow**: 用于实现毛玻璃效果
- **qtawesome**: 提供图标支持

### 数据库相关
- **sqlite3**: Python内置，用于关系型数据库操作
- **chromadb**: 轻量级向量数据库，用于存储和检索向量嵌入
- **sqlalchemy**: SQL工具包和ORM，简化数据库操作

### AI相关
- **openai**: OpenAI API客户端，用于AI功能
- **sentence-transformers**: 用于生成文本嵌入向量
- **numpy**: 用于数值计算
- **scikit-learn**: 用于机器学习算法（如聚类）
- **schedule**: 用于定时任务管理

### 系统功能相关
- **keyboard**: 用于全局快捷键支持
- **pywin32**: Windows API接口，用于系统集成
- **apscheduler**: 高级Python调度器，用于定时任务
- **python-dotenv**: 用于环境变量管理，存储API密钥等敏感信息

### 工具库
- **tqdm**: 进度条显示
- **loguru**: 日志记录
- **pyyaml**: YAML配置文件支持
- **requests**: HTTP请求

## 开发工具
- **virtualenv**: 用于创建隔离的Python环境
- **black**: 代码格式化工具
- **isort**: 导入排序工具
- **pylint**: 代码静态分析工具

## 打包与分发
- **PyInstaller**: 将Python应用打包为独立可执行文件
- **pywin32**: 用于Windows特定功能
- **setuptools**: 用于构建和分发Python包

## 特殊考虑
- 所有依赖都应通过pip安装，避免使用需要额外安装步骤的库
- 向量数据库选择chromadb，因为它是纯Python实现，易于安装和集成
- 使用内置sqlite3模块，避免外部数据库依赖
- 确保所有库都与PyInstaller兼容，以便成功打包为exe
