#!/bin/bash
# 虚拟环境设置脚本
# 此脚本用于创建Python虚拟环境并安装所需依赖

# 设置颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 显示欢迎信息
echo -e "${GREEN}====================================================${NC}"
echo -e "${GREEN}       ideaSystemXS 虚拟环境设置脚本              ${NC}"
echo -e "${GREEN}====================================================${NC}"
echo ""

# 检查Python版本
echo -e "${YELLOW}检查Python版本...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}找到 $PYTHON_VERSION${NC}"
else
    echo -e "${RED}错误: 未找到Python 3。请安装Python 3.8或更高版本。${NC}"
    exit 1
fi

# 检查pip
echo -e "${YELLOW}检查pip...${NC}"
if command -v pip3 &>/dev/null; then
    PIP_VERSION=$(pip3 --version)
    echo -e "${GREEN}找到 $PIP_VERSION${NC}"
else
    echo -e "${RED}错误: 未找到pip3。请安装pip。${NC}"
    exit 1
fi

# 检查venv模块
echo -e "${YELLOW}检查venv模块...${NC}"
if python3 -c "import venv" &>/dev/null; then
    echo -e "${GREEN}venv模块已安装${NC}"
else
    echo -e "${RED}错误: venv模块未安装。请安装Python venv模块。${NC}"
    echo -e "${YELLOW}在Ubuntu上，可以运行: sudo apt-get install python3-venv${NC}"
    echo -e "${YELLOW}在Windows上，venv应该已经包含在Python安装中${NC}"
    exit 1
fi

# 创建虚拟环境
VENV_DIR="venv"
echo -e "${YELLOW}创建虚拟环境 '$VENV_DIR'...${NC}"
if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}虚拟环境目录已存在。是否要删除并重新创建? (y/n)${NC}"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo -e "${YELLOW}删除现有虚拟环境...${NC}"
        rm -rf "$VENV_DIR"
    else
        echo -e "${GREEN}使用现有虚拟环境${NC}"
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo -e "${RED}错误: 创建虚拟环境失败${NC}"
        exit 1
    fi
    echo -e "${GREEN}虚拟环境创建成功${NC}"
fi

# 激活虚拟环境
echo -e "${YELLOW}激活虚拟环境...${NC}"
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
    source "$VENV_DIR/Scripts/activate"
else
    echo -e "${RED}错误: 无法找到激活脚本${NC}"
    exit 1
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}错误: 激活虚拟环境失败${NC}"
    exit 1
fi
echo -e "${GREEN}虚拟环境已激活${NC}"

# 升级pip
echo -e "${YELLOW}升级pip...${NC}"
pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo -e "${RED}警告: 升级pip失败，但将继续安装依赖${NC}"
fi

# 安装依赖
echo -e "${YELLOW}安装依赖...${NC}"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}错误: 安装依赖失败${NC}"
    exit 1
fi
echo -e "${GREEN}依赖安装成功${NC}"

# 完成
echo ""
echo -e "${GREEN}====================================================${NC}"
echo -e "${GREEN}       虚拟环境设置完成!                           ${NC}"
echo -e "${GREEN}====================================================${NC}"
echo ""
echo -e "要激活此虚拟环境，请运行:"
echo -e "${YELLOW}source $VENV_DIR/bin/activate${NC} (Linux/macOS)"
echo -e "或"
echo -e "${YELLOW}$VENV_DIR\\Scripts\\activate${NC} (Windows)"
echo ""
echo -e "要退出虚拟环境，请运行:"
echo -e "${YELLOW}deactivate${NC}"
echo ""
