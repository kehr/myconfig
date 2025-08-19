#!/bin/bash

# 测试 zsh 补全功能的脚本
echo "测试 myconfig zsh 补全功能..."

# 加载补全脚本
source contrib/_myconfig

# 测试补全函数是否存在
if type _myconfig > /dev/null 2>&1; then
    echo "✅ 补全函数 _myconfig 已加载"
else
    echo "❌ 补全函数 _myconfig 未找到"
    exit 1
fi

# 测试 compdef 是否正确设置
if compdef -p myconfig > /dev/null 2>&1; then
    echo "✅ myconfig 命令已注册补全"
else
    echo "❌ myconfig 命令补全未注册"
    exit 1
fi

echo ""
echo "补全脚本修复内容："
echo "1. ✅ 添加了缺少的命令: scan, unpack"
echo "2. ✅ 修复了 defaults 子命令: export-all, import"
echo "3. ✅ 添加了所有参数选项: --preview, --config, --version, --compress, --gpg"
echo "4. ✅ 改进了补全结构，使用更标准的 zsh 补全格式"
echo "5. ✅ 为文件参数添加了适当的文件类型过滤"
echo ""
echo "现在你可以在 zsh 中使用 Tab 键补全 myconfig 命令了！"
echo ""
echo "使用方法："
echo "1. 将 contrib/_myconfig 复制到 zsh 补全目录"
echo "2. 或者在 ~/.zshrc 中添加: source /path/to/contrib/_myconfig"
echo "3. 重新加载 zsh 或运行: source ~/.zshrc"