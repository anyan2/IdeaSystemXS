# IdeaSystemXS
首先：先运行first_setup_env，这会设置虚拟环境和安装依赖。
# 现在的问题
问题是遇到了如下问题：
当把main.py作为包运行的时候（python -m src.main），显示无法找到main.py同级目录的core文件夹报错如下：
D:\ideaSystemXS>python -m src.main Traceback (most recent call last):   File "C:\Users\--\AppData\Local\Programs\Python\Python39\lib\runpy.py", line 197, in *run*module_as_main     return *run*code(code, main_globals, None,   File "C:\Users\--\AppData\Local\Programs\Python\Python39\lib\runpy.py", line 87, in *run*code     exec(code, run_globals)   File "D:\library\developIDEAS\autogen\ideaSystemXS\src\main.py", line 19, in      from core.app_manager import AppManager ModuleNotFoundError: No module named 'core'
这时候错误体现在无法找到core组件上。
当main.py当做py文件运行的时候，此时会正常import core内的文件，但是core内的文件调用他同级的文件的时候，因为from ..core.config_manager import ConfigManager这种先出自己目录，然后再进自己目录调用自己同级文件的方式出问题报错：
Traceback (most recent call last):
  File "D:\ideaSystemXS\src\main.py", line 19, in <module>
    from core.app_manager import AppManager
  File "D:\ideaSystemXS\src\core\app_manager.py", line 7, in <module>
    from ..core.config_manager import ConfigManager
ImportError: attempted relative import beyond top-level package
此时阻拦该文件访问上级目录。
## 如遇到莫名其妙的压缩包，是我怕改坏了文件做的备份，无视就行
# 这次貌似真的不缺文件了
