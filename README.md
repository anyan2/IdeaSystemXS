
# IdeaSystemXS  
首先：先运行 `first_setup_env`，这会设置虚拟环境和安装依赖。


# 现在的问题 ❗  
问题是遇到了如下问题：  

### 模块导入失败（包模式运行）  
当使用包模式运行时（`python -m src.main`），显示无法找到 `main.py` 同级目录的 `core` 文件夹，报错如下：  
```
D:\ideaSystemXS>python -m src.main  
Traceback (most recent call last):  
  File "C:\Users\--\AppData\Local\Programs\Python\Python39\lib\runpy.py", line 197, in _run_module_as_main  
    return _run_code(code, main_globals, None,  
  File "C:\Users\--\AppData\Local\Programs\Python\Python39\lib\runpy.py", line 87, in _run_code  
    exec(code, run_globals)  
  File "D:\library\developIDEAS\autogen\ideaSystemXS\src\main.py", line 19, in <module>  
    from core.app_manager import AppManager  
**ModuleNotFoundError**: No module named 'core'  
```  
🔍 **关键问题**：无法找到 `core组件`。  

### 相对导入越界（直接运行）  
当直接运行 `main.py` 时，`core` 内文件调用同级文件出现错误：  
```
Traceback (most recent call last):  
  File "D:\ideaSystemXS\src\main.py", line 19, in <module>  
    from core.app_manager import AppManager  
  File "D:\ideaSystemXS\src\core\app_manager.py", line 7, in <module>  
    from ..core.config_manager import ConfigManager  
**ImportError**: attempted relative import beyond top-level package  
```  
🔍 **关键问题**：文件访问上级目录被阻拦。  

## 注意事项  
如遇到 `.zip` 压缩包，是代码备份文件，请忽略。  
# 这次貌似真的不缺文件了  


# 2025-03-29 更新（已解决）  
> 🟢 **已修复**：  
> - 基础模块缺失  
> - 依赖安装错误  
> - 核心组件初始化问题  

## 新增问题：AI & 窗口管理组件异常  
**当前未解决问题**：  
虽然已补全 `ai_manager` 和 `window_manager`，但启动主窗口时仍存在问题：  
```python
Traceback (most recent call last):  
  File "D:\library\developIDEAS\autogen\ideaSystemXS\src\main.py", line 75, in main  
    app_manager.start()  
**AttributeError**: 'AppManager' object has no attribute 'start'  
```  
🔍 **关键问题**：`AppManager` 类缺少 `start()` 方法，且 `window_manager` 自定义启动逻辑存在 bug。  


### 组件版本回退指南  
因为项目依赖于旧版本组件，请执行以下命令回退依赖版本：  
```bash
# 卸载旧版本
pip uninstall numpy chromadb

# 安装指定版本
pip install numpy==1.26.4  
pip install chromadb==0.5.0  
```  

