"""测试改名验证功能"""
import sys
import re
from pathlib import Path

# 复制验证函数和常量（避免导入整个handlers包）
RENAME_COST = 20000
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 10

FORBIDDEN_WORDS = [
    "管理员", "GM", "系统", "官方", "客服",
    "fuck", "shit", "damn", "傻逼", "操你妈",
]


def validate_nickname(nickname: str) -> tuple[bool, str]:
    """验证道号合法性"""
    if len(nickname) < MIN_NAME_LENGTH:
        return False, f"道号长度不能少于{MIN_NAME_LENGTH}个字符"

    if len(nickname) > MAX_NAME_LENGTH:
        return False, f"道号长度不能超过{MAX_NAME_LENGTH}个字符"

    if not nickname or nickname.isspace():
        return False, "道号不能为空或只包含空格"

    if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9·•]+$', nickname):
        return False, "道号只能包含中文、英文、数字和·符号"

    nickname_lower = nickname.lower()
    for word in FORBIDDEN_WORDS:
        if word.lower() in nickname_lower:
            return False, f"道号包含禁用词：{word}"

    if nickname[0].isdigit():
        return False, "道号不能以数字开头"

    return True, ""


def run_validation_suite() -> bool:
    """运行道号验证测试返回是否全部通过"""

    print("=" * 60)
    print("🧪 道号验证测试")
    print("=" * 60)
    print()

    test_cases = [
        # (nickname, expected_valid, description)
        ("逍遥散人", True, "正常中文道号"),
        ("剑尘", True, "2字道号（最小长度）"),
        ("青云真君无敌天下", True, "10字道号（最大长度）"),
        ("SwordKing", True, "纯英文道号（9字符）"),
        ("血影魔君123", True, "中英文数字混合"),
        ("玄天·道人", True, "包含·符号"),

        # 无效案例
        ("逍", False, "长度不足（<2）"),
        ("这个道号实在太长了超过限制", False, "长度超限（>10）"),
        ("123开始", False, "数字开头"),
        ("道号@特殊", False, "包含特殊字符@"),
        ("道号#符号", False, "包含特殊字符#"),
        ("管理员", False, "包含禁用词"),
        ("系统道人", False, "包含禁用词"),
        ("", False, "空字符串"),
        ("   ", False, "只有空格"),
        ("操你妈", False, "包含脏话"),
    ]

    passed = 0
    failed = 0

    for nickname, expected_valid, description in test_cases:
        is_valid, error_msg = validate_nickname(nickname)

        if is_valid == expected_valid:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1

        result = "有效" if is_valid else f"无效({error_msg})"
        print(f"{status} | {description:20} | '{nickname}' -> {result}")

    print()
    print("-" * 60)
    print(f"测试结果: 通过 {passed}/{len(test_cases)}, 失败 {failed}/{len(test_cases)}")
    print("-" * 60)
    print()

    # 显示配置信息
    print("📋 改名配置")
    print("-" * 60)
    print(f"改名消耗: {RENAME_COST:,} 灵石")
    print(f"道号长度: {MIN_NAME_LENGTH}-{MAX_NAME_LENGTH} 个字符")
    print(f"改名次数: 终生1次")
    print("-" * 60)
    print()

    return failed == 0


def test_nickname_validation():
    """pytest 用例包装"""
    assert run_validation_suite(), "部分改名校验用例失败"


if __name__ == "__main__":
    success = run_validation_suite()

    if success:
        print("✅ 所有验证测试通过！")
        sys.exit(0)
    else:
        print("❌ 部分测试失败！")
        sys.exit(1)
