# ideaSystemXS 数据库结构设计

## 概述

ideaSystemXS使用两种数据库来存储和管理数据：
1. **SQLite关系型数据库**：存储结构化数据，如想法内容、标签、用户设置等
2. **ChromaDB向量数据库**：存储文本嵌入向量，用于相似度搜索和AI分析

## SQLite数据库结构

### 表设计

#### 1. Ideas表（想法表）
```sql
CREATE TABLE Ideas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,                -- 想法内容
    title TEXT,                           -- 想法标题（可自动生成或用户指定）
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 更新时间
    is_archived BOOLEAN NOT NULL DEFAULT 0,  -- 是否归档
    is_favorite BOOLEAN NOT NULL DEFAULT 0,  -- 是否收藏
    ai_processed BOOLEAN NOT NULL DEFAULT 0, -- 是否已被AI处理
    summary TEXT,                         -- AI生成的摘要
    importance INTEGER DEFAULT 3,         -- 重要性评分（1-5）
    reminder_date TIMESTAMP               -- 提醒日期（如果有）
);
```

#### 2. Tags表（标签表）
```sql
CREATE TABLE Tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,            -- 标签名称
    color TEXT DEFAULT '#808080',         -- 标签颜色（十六进制）
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP  -- 创建时间
);
```

#### 3. IdeaTags表（想法-标签关联表）
```sql
CREATE TABLE IdeaTags (
    idea_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (idea_id, tag_id),
    FOREIGN KEY (idea_id) REFERENCES Ideas(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES Tags(id) ON DELETE CASCADE
);
```

#### 4. Relations表（想法关联表）
```sql
CREATE TABLE Relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_idea_id INTEGER NOT NULL,      -- 源想法ID
    target_idea_id INTEGER NOT NULL,      -- 目标想法ID
    relation_type TEXT NOT NULL,          -- 关联类型（如"相似"、"延续"、"对立"等）
    confidence REAL NOT NULL,             -- 关联置信度（0-1）
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    FOREIGN KEY (source_idea_id) REFERENCES Ideas(id) ON DELETE CASCADE,
    FOREIGN KEY (target_idea_id) REFERENCES Ideas(id) ON DELETE CASCADE
);
```

#### 5. Keywords表（关键词表）
```sql
CREATE TABLE Keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idea_id INTEGER NOT NULL,             -- 关联的想法ID
    keyword TEXT NOT NULL,                -- 关键词
    weight REAL NOT NULL,                 -- 权重（0-1）
    FOREIGN KEY (idea_id) REFERENCES Ideas(id) ON DELETE CASCADE
);
```

#### 6. Settings表（设置表）
```sql
CREATE TABLE Settings (
    key TEXT PRIMARY KEY,                 -- 设置键
    value TEXT,                           -- 设置值
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP  -- 更新时间
);
```

#### 7. AITasks表（AI任务表）
```sql
CREATE TABLE AITasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idea_id INTEGER,                      -- 关联的想法ID（如果有）
    task_type TEXT NOT NULL,              -- 任务类型（如"分析"、"摘要"、"关联"等）
    status TEXT NOT NULL,                 -- 任务状态（"待处理"、"处理中"、"已完成"、"失败"）
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    processed_at TIMESTAMP,               -- 处理时间
    result TEXT,                          -- 处理结果
    error TEXT,                           -- 错误信息（如果有）
    FOREIGN KEY (idea_id) REFERENCES Ideas(id) ON DELETE CASCADE
);
```

#### 8. Reminders表（提醒表）
```sql
CREATE TABLE Reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idea_id INTEGER NOT NULL,             -- 关联的想法ID
    reminder_time TIMESTAMP NOT NULL,     -- 提醒时间
    is_completed BOOLEAN NOT NULL DEFAULT 0,  -- 是否已完成
    note TEXT,                            -- 提醒备注
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    FOREIGN KEY (idea_id) REFERENCES Ideas(id) ON DELETE CASCADE
);
```

### 索引设计

```sql
-- Ideas表索引
CREATE INDEX idx_ideas_created_at ON Ideas(created_at);
CREATE INDEX idx_ideas_updated_at ON Ideas(updated_at);
CREATE INDEX idx_ideas_is_archived ON Ideas(is_archived);
CREATE INDEX idx_ideas_is_favorite ON Ideas(is_favorite);
CREATE INDEX idx_ideas_ai_processed ON Ideas(ai_processed);
CREATE INDEX idx_ideas_reminder_date ON Ideas(reminder_date);

-- Keywords表索引
CREATE INDEX idx_keywords_idea_id ON Keywords(idea_id);
CREATE INDEX idx_keywords_keyword ON Keywords(keyword);

-- Relations表索引
CREATE INDEX idx_relations_source_idea_id ON Relations(source_idea_id);
CREATE INDEX idx_relations_target_idea_id ON Relations(target_idea_id);

-- Reminders表索引
CREATE INDEX idx_reminders_idea_id ON Reminders(idea_id);
CREATE INDEX idx_reminders_reminder_time ON Reminders(reminder_time);
CREATE INDEX idx_reminders_is_completed ON Reminders(is_completed);
```

### 触发器设计

```sql
-- 更新Ideas表的updated_at字段
CREATE TRIGGER update_ideas_timestamp 
AFTER UPDATE ON Ideas
FOR EACH ROW
BEGIN
    UPDATE Ideas SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

-- 更新Settings表的updated_at字段
CREATE TRIGGER update_settings_timestamp 
AFTER UPDATE ON Settings
FOR EACH ROW
BEGIN
    UPDATE Settings SET updated_at = CURRENT_TIMESTAMP WHERE key = OLD.key;
END;
```

## ChromaDB向量数据库结构

ChromaDB是一个轻量级的向量数据库，用于存储和检索文本嵌入向量。在ideaSystemXS中，我们将使用ChromaDB来存储想法的向量表示，以支持相似度搜索和AI分析。

### 集合设计

#### 1. ideas_embeddings（想法嵌入集合）

这个集合存储所有想法的嵌入向量，用于相似度搜索和关联分析。

**元数据结构**:
```python
{
    "idea_id": int,           # 对应SQLite中Ideas表的id
    "created_at": str,        # 创建时间
    "updated_at": str,        # 更新时间
    "title": str,             # 想法标题
    "tags": List[str],        # 标签列表
    "is_archived": bool,      # 是否归档
    "is_favorite": bool       # 是否收藏
}
```

#### 2. keywords_embeddings（关键词嵌入集合）

这个集合存储从想法中提取的关键词的嵌入向量，用于主题聚类和内容推荐。

**元数据结构**:
```python
{
    "keyword": str,           # 关键词
    "idea_ids": List[int],    # 包含该关键词的想法ID列表
    "weight": float,          # 权重
    "created_at": str         # 创建时间
}
```

## 数据库接口设计

### SQLite数据库接口

我们将使用SQLAlchemy ORM来简化SQLite数据库操作，定义以下主要接口：

1. **IdeaRepository**：管理想法的CRUD操作
2. **TagRepository**：管理标签的CRUD操作
3. **RelationRepository**：管理想法关联的CRUD操作
4. **KeywordRepository**：管理关键词的CRUD操作
5. **SettingsRepository**：管理应用设置的CRUD操作
6. **AITaskRepository**：管理AI任务的CRUD操作
7. **ReminderRepository**：管理提醒的CRUD操作

### ChromaDB向量数据库接口

我们将使用ChromaDB的Python客户端来操作向量数据库，定义以下主要接口：

1. **VectorDBClient**：管理ChromaDB客户端连接
2. **IdeaEmbeddingRepository**：管理想法嵌入向量的CRUD操作
3. **KeywordEmbeddingRepository**：管理关键词嵌入向量的CRUD操作
4. **SimilaritySearchService**：提供相似度搜索功能

## 数据库初始化和迁移

1. **初始化脚本**：创建数据库表结构、索引和触发器
2. **迁移脚本**：处理数据库架构变更
3. **数据备份脚本**：定期备份数据库

## 数据库文件位置

由于PyInstaller打包的限制，数据库文件不能包含在exe中，我们将采用以下策略：

1. **开发环境**：数据库文件存储在项目目录下的`data`文件夹中
2. **生产环境**：数据库文件存储在用户数据目录中（如`%APPDATA%\ideaSystemXS\data`）
3. **程序启动时**：检测环境并自动选择正确的数据库路径

## 数据安全考虑

1. **数据加密**：敏感数据（如API密钥）使用加密存储
2. **事务管理**：使用事务确保数据一致性
3. **错误恢复**：实现数据库错误恢复机制
4. **备份策略**：定期自动备份数据库
