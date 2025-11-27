#!/usr/bin/env python3
"""修复中文命令：处理所有中文 CommandHandler"""
import re
import os

HANDLERS_DIR = "/opt/xiuxian-bot/src/bot/handlers"

# 匹配包含中文的CommandHandler（单个字符串或列表）
# 模式1: CommandHandler("中文", func)
pattern1 = r'CommandHandler\s*\(\s*"([^"]*[\u4e00-\u9fff][^"]*)"\s*,\s*(\w+)\s*\)'
# 模式2: CommandHandler(["cmd1", "中文"], func)
pattern2 = r'CommandHandler\s*\(\s*\[([^\]]*[\u4e00-\u9fff][^\]]*)\]\s*,\s*(\w+)\s*\)'

def fix_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # 替换单字符串格式
    def replace_single(match):
        cmd = match.group(1)
        func = match.group(2)
        return f'MessageHandler(filters.Regex(r"^\\.{cmd}"), {func})'

    new_content = re.sub(pattern1, replace_single, content)

    # 替换列表格式 - 为每个中文命令创建单独的handler
    def replace_list(match):
        cmds_str = match.group(1)
        func = match.group(2)
        # 解析命令列表
        cmds = re.findall(r'"([^"]+)"', cmds_str)
        handlers = []
        for cmd in cmds:
            if re.search(r'[\u4e00-\u9fff]', cmd):
                # 中文命令用 MessageHandler
                handlers.append(f'MessageHandler(filters.Regex(r"^\\.{cmd}"), {func})')
            else:
                # 英文命令保持 CommandHandler
                handlers.append(f'CommandHandler("{cmd}", {func})')
        return handlers[0] if len(handlers) == 1 else '\n    '.join([f'application.add_handler({h})' for h in handlers])

    # 这个比较复杂，手动处理
    list_matches = list(re.finditer(pattern2, new_content))
    for match in reversed(list_matches):
        cmds_str = match.group(1)
        func = match.group(2)
        cmds = re.findall(r'"([^"]+)"', cmds_str)

        # 分离中英文命令
        cn_cmds = [c for c in cmds if re.search(r'[\u4e00-\u9fff]', c)]
        en_cmds = [c for c in cmds if not re.search(r'[\u4e00-\u9fff]', c)]

        replacement_parts = []
        if en_cmds:
            if len(en_cmds) == 1:
                replacement_parts.append(f'CommandHandler("{en_cmds[0]}", {func})')
            else:
                replacement_parts.append(f'CommandHandler({en_cmds}, {func})')
        for cn_cmd in cn_cmds:
            replacement_parts.append(f'MessageHandler(filters.Regex(r"^\\.{cn_cmd}"), {func})')

        # 只保留第一个，其他的需要手动处理
        if replacement_parts:
            new_content = new_content[:match.start()] + replacement_parts[0] + new_content[match.end():]

    # 添加 MessageHandler 和 filters 导入
    if new_content != original:
        if "from telegram.ext import" in new_content:
            import_match = re.search(r'from telegram\.ext import ([^\n]+)', new_content)
            if import_match:
                imports = import_match.group(1)
                additions = []
                if "MessageHandler" not in imports:
                    additions.append("MessageHandler")
                if "filters" not in imports:
                    additions.append("filters")
                if additions:
                    new_content = new_content.replace(
                        f"from telegram.ext import {imports}",
                        f"from telegram.ext import {', '.join(additions)}, {imports}"
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
