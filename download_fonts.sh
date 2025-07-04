#!/bin/bash

# 字体下载脚本 - 为Docker环境准备中文字体

echo "📝 下载中文字体文件..."

FONT_DIR="./fonts"
mkdir -p "$FONT_DIR"

# 下载思源黑体（开源免费字体）
echo "📥 下载思源黑体 (Source Han Sans CN)..."
if [ ! -f "$FONT_DIR/SourceHanSansCN-Regular.ttf" ]; then
    curl -L "https://github.com/adobe-fonts/source-han-sans/releases/download/2.004R/SourceHanSansCN.zip" -o "$FONT_DIR/SourceHanSansCN.zip"
    cd "$FONT_DIR"
    unzip -q SourceHanSansCN.zip
    find . -name "SourceHanSansCN-Regular.otf" -exec cp {} SourceHanSansCN-Regular.ttf \;
    rm -rf SourceHanSansCN.zip SubsetOTF OTC
    cd ..
    echo "✅ 思源黑体下载完成"
else
    echo "✅ 思源黑体已存在"
fi

# 下载思源宋体（开源免费字体）
echo "📥 下载思源宋体 (Source Han Serif CN)..."
if [ ! -f "$FONT_DIR/SourceHanSerifCN-Regular.ttf" ]; then
    curl -L "https://github.com/adobe-fonts/source-han-serif/releases/download/2.001R/09_SourceHanSerifCN.zip" -o "$FONT_DIR/SourceHanSerifCN.zip"
    cd "$FONT_DIR"
    unzip -q SourceHanSerifCN.zip
    find . -name "SourceHanSerifCN-Regular.otf" -exec cp {} SourceHanSerifCN-Regular.ttf \;
    rm -rf SourceHanSerifCN.zip SourceHanSerifCN
    cd ..
    echo "✅ 思源宋体下载完成"
else
    echo "✅ 思源宋体已存在"
fi

# 下载 Noto Sans CJK SC（Google字体）
echo "📥 下载 Noto Sans CJK SC..."
if [ ! -f "$FONT_DIR/NotoSansCJKsc-Regular.ttf" ]; then
    curl -L "https://github.com/googlefonts/noto-cjk/releases/download/Sans2.004/03_NotoSansCJK-TTF.zip" -o "$FONT_DIR/NotoSansCJK.zip"
    cd "$FONT_DIR"
    unzip -q NotoSansCJK.zip
    find . -name "NotoSansCJKsc-Regular.ttf" -exec cp {} . \;
    rm -rf NotoSansCJK.zip NotoSansCJK-TTF
    cd ..
    echo "✅ Noto Sans CJK SC 下载完成"
else
    echo "✅ Noto Sans CJK SC 已存在"
fi

echo ""
echo "✅ 字体下载完成！"
echo "📁 字体文件位置: $FONT_DIR/"
ls -la "$FONT_DIR/"*.ttf 2>/dev/null || echo "⚠️ 未找到TTF字体文件"
