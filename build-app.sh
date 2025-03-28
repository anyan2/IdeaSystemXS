#!/bin/bash
# PyInstaller打包脚本 - Linux版本
# 此脚本用于将ideaSystemXS打包成Linux可执行程序

# 设置颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 显示欢迎信息
echo -e "${GREEN}====================================================${NC}"
echo -e "${GREEN}       ideaSystemXS 打包脚本 (Linux)               ${NC}"
echo -e "${GREEN}====================================================${NC}"
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${RED}错误: 未找到虚拟环境。请先运行 setup-env.sh 脚本。${NC}"
    exit 1
fi

# 激活虚拟环境
echo -e "${YELLOW}激活虚拟环境...${NC}"
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo -e "${RED}错误: 无法找到激活脚本${NC}"
    exit 1
fi

# 检查PyInstaller
echo -e "${YELLOW}检查PyInstaller...${NC}"
if ! pip show pyinstaller &>/dev/null; then
    echo -e "${YELLOW}安装PyInstaller...${NC}"
    pip install pyinstaller
    if [ $? -ne 0 ]; then
        echo -e "${RED}错误: 安装PyInstaller失败${NC}"
        exit 1
    fi
fi

# 创建输出目录
if [ ! -d "dist" ]; then
    mkdir dist
fi

# 清理旧的构建文件
echo -e "${YELLOW}清理旧的构建文件...${NC}"
rm -rf build
rm -rf dist/ideaSystemXS

# 运行PyInstaller
echo -e "${YELLOW}开始打包应用程序...${NC}"
pyinstaller --noconfirm --clean \
    --name="ideaSystemXS" \
    --add-data="src/ui/resources:src/ui/resources" \
    --hidden-import=PyQt6.QtCore \
    --hidden-import=PyQt6.QtGui \
    --hidden-import=PyQt6.QtWidgets \
    --hidden-import=sqlite3 \
    --hidden-import=chromadb \
    --hidden-import=numpy \
    --hidden-import=openai \
    --windowed \
    src/main.py

if [ $? -ne 0 ]; then
    echo -e "${RED}错误: PyInstaller打包失败${NC}"
    exit 1
fi

# 复制额外文件
echo -e "${YELLOW}复制额外文件...${NC}"
cp README.md dist/ideaSystemXS/
cp LICENSE dist/ideaSystemXS/
mkdir -p dist/ideaSystemXS/data
mkdir -p dist/ideaSystemXS/config

# 创建启动脚本
echo -e "${YELLOW}创建启动脚本...${NC}"
cat > dist/ideaSystemXS/start_ideaSystemXS.sh << 'EOF'
#!/bin/bash
# 启动ideaSystemXS
cd "$(dirname "$0")"
./ideaSystemXS
EOF
chmod +x dist/ideaSystemXS/start_ideaSystemXS.sh

# 创建ZIP压缩包
echo -e "${YELLOW}创建ZIP压缩包...${NC}"
cd dist
zip -r ideaSystemXS.zip ideaSystemXS
cd ..

echo ""
echo -e "${GREEN}====================================================${NC}"
echo -e "${GREEN}        打包完成!                                  ${NC}"
echo -e "${GREEN}====================================================${NC}"
echo ""
echo -e "可执行程序位于: ${YELLOW}dist/ideaSystemXS/ideaSystemXS${NC}"
echo -e "ZIP压缩包位于: ${YELLOW}dist/ideaSystemXS.zip${NC}"
echo ""
echo -e "请将ZIP压缩包发送给用户，用户解压后可直接运行。"
echo ""

# 退出虚拟环境
deactivate
