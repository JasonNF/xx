#!/usr/bin/env python3
"""修复中文命令：将 CommandHandler("中文") 改为 MessageHandler(filters.Regex(r"^\.中文"))"""
import re
import os

HANDLERS_DIR = "/opt/xiuxian-bot/src/bot/handlers"

# 匹配中文CommandHandler的正则
pattern = r'CommandHandler\s*\(\s*"([^"]*[\u4e00-\u9fff][^"]*)"\s*,\s*(\w+)\s*\)'

def fix_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # 替换 CommandHandler 为 MessageHandler
    def replace_handler(match):
        cmd = match.group(1)
        func = match.group(2)
        return f'MessageHandler(filters.Regex(r"^\\.{cmd}"), {func})'

    new_content = re.sub(pattern, replace_handler, content)

    # 添加 MessageHandler 和 filters 导入
    if new_content != original:
        # 检查并修复导入
        if "from telegram.ext import" in new_content:
            import_line = re.search(r'from telegram\.ext import ([^\n]+)', new_content)
            if import_line:
                imports = import_line.group(1)
                new_imports = []
                if "MessageHandler" not in imports:
                    new_imports.append("MessageHandler")
                if "filters" not in imports:
                    new_imports.append("filters")
                if new_imports:
                    new_content = new_content.replace(
                        f"from telegram.ext import {imports}",
                        f"from telegram.ext import {', '.join(new_imports)}, {imports}"
                    )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False

count = 0
for filename in os.listdir(HANDLERS_DIR):
    if filename.endswith(".py"):
        filepath = os.path.join(HANDLERS_DIR, filename)
        if fix_file(filepath):
            print(f"Fixed: {filename}")
            count += 1

print(f"\nTotal fixed: {count} files")
