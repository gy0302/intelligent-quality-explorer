"""
智能测试探索架构 - 源代码包
将此目录标记为Python包，允许导入子模块
"""
from pathlib import Path
import sys

# 将项目根目录添加到Python路径，这样可以从任何位置导入
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

__version__ = "0.1.0"
__author__ = "智能测试团队"
__description__ = "基于AI的智能接口测试自动生成平台"

# 导出常用的模块，便于导入
__all__ = [
    "configs",
    "intelligent_testing",
]