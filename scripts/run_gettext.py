import asyncio
import configparser
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Set

import polib

# 注意：此脚本的异步翻译功能依赖于一个支持 asyncio 的 googletrans 库，
from googletrans import Translator
from googletrans.models import Translated

ROOT_PATH = Path(__file__).parent.parent.resolve()

# --- 配置区 ---
config = configparser.ConfigParser()
config_path = ROOT_PATH / "scripts" / "script_config.ini"

if not config_path.exists():
    raise FileNotFoundError(f"配置文件未找到: {config_path}")
config.read(config_path, encoding="utf-8")

support_languages = [lan.strip() for lan in config.get("i18n", "support_languages").split(",")]
# 过滤掉 'en'，因为它是源语言，不需要翻译
support_languages = [lang for lang in support_languages if lang and lang != "en"]

if not support_languages:
    print("警告: 未配置除 'en' 之外的支持语言。自动翻译将不会执行。")

auto_translate = config.getboolean("i18n", "auto_translate", fallback=False)

SERVICES_DIR = ROOT_PATH / "src" / "hexo_helper" / "service"
LOCALE_DIR = ROOT_PATH / "locale"
EN_DIR = LOCALE_DIR / "en" / "LC_MESSAGES"
# 使用一个临时的 .pot 目录，避免混淆
POT_OUTPUT_DIR = LOCALE_DIR / ".pot_temp"


# --- 核心功能函数 ---


def fix_pot_header(pot_path: Path):
    """
    【关键修复】读取 .pot 文件，强制将其头部的 charset 修改为 UTF-8。
    这是解决 'gbk' 编码错误的根本方法。
    """
    print(f"  🔧 正在修正 POT 文件头: {pot_path.name}")
    try:
        # 先尝试用 utf-8 读取，这是最常见的情况
        content = pot_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # 如果失败，说明文件可能被存为系统默认编码（如 gbk/cp936）
        print("  - 检测到非 UTF-8 编码，尝试以 cp936 回退读取...")
        content = pot_path.read_text(encoding="cp936", errors="replace")

    # 使用正则表达式替换 charset，无论它之前是什么
    new_content, count = re.subn(
        r'("Content-Type: text/plain; charset=)(.*?)(\\n")', r"\1UTF-8\3", content, flags=re.IGNORECASE
    )

    if count > 0:
        pot_path.write_text(new_content, encoding="utf-8")
        print(f"  ✔ 已将 {pot_path.name} 的 charset 更新为 UTF-8。")
    else:
        print(f"  ℹ {pot_path.name} 未找到 charset 声明或无需修改。")


async def batch_translate_texts(texts: Set[str], target_langs: List[str]) -> Dict[str, Dict[str, str]]:
    """
    并发地将一组文本翻译成多种目标语言。
    """
    if not texts:
        return {}
    print(f"\n--- 准备将 {len(texts)} 条独特文本翻译成 {target_langs} 语言 ---")
    tasks = []
    # googletrans-py 推荐为每个请求创建新的 Translator 实例
    translator = Translator()
    for text in texts:
        for lang in target_langs:
            # 每个翻译都是一个独立的异步任务
            tasks.append(translator.translate(text, src="en", dest=lang))

    print(f"已创建 {len(tasks)} 个并发翻译任务, 开始执行...")
    results = await asyncio.gather(*tasks, return_exceptions=True)
    print("✔ 所有翻译任务执行完毕。")

    # 将结果整理成方便查询的嵌套字典
    translations_map = {text: {} for text in texts}
    task_index = 0
    for text in texts:
        for lang in target_langs:
            result = results[task_index]
            if isinstance(result, Translated) and result.text:
                translations_map[text][lang] = result.text
                print(f"当前语言: {lang}")
                print("------- 翻译结果 ---------")
                print(result.text)
                print("------------------------")
            else:
                error_msg = repr(result) if isinstance(result, Exception) else f"返回类型无效: {type(result)}"
                print(f"  ❌ 翻译 '{text[:30]}...' 到 '{lang}' 失败: {error_msg}")
            task_index += 1
    return translations_map


def discover_domains_and_sources(root_dir: Path) -> Dict[str, List[str]]:
    """自动发现模块（域）及其对应的源文件。"""
    domains = {}
    if not root_dir.is_dir():
        return domains
    # 发现所有子目录作为域
    for sub_path in root_dir.iterdir():
        if sub_path.is_dir() and (sub_path / "__init__.py").exists():
            domain_name = sub_path.name
            source_files = [str(p) for p in sub_path.rglob("*.py")]
            if source_files:
                domains[domain_name] = source_files
    # 发现根目录下的文件作为默认域 "_"
    root_py_files = [str(p) for p in root_dir.glob("*.py") if p.is_file()]
    if root_py_files:
        domains["_"] = root_py_files
    return domains


def run_pygettext(pygettext_path: Path, domain: str, sources: List[str], output_dir: Path):
    """为指定域执行 pygettext 命令。"""
    print(f"\n--- 正在处理域: [{domain}] ---")
    output_pot_file = output_dir / f"{domain}.pot"
    command = ["python", str(pygettext_path), "--no-location", "-d", domain, "-o", str(output_pot_file)] + sources
    print(f"  > 执行: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
        print(f"  ✔ 成功为域 [{domain}] 生成模板文件。")
        if result.stderr:
            print(f"  - 信息: {result.stderr.strip()}")
        # 【关键步骤】生成后立即修复文件头
        fix_pot_header(output_pot_file)
    except subprocess.CalledProcessError as e:
        print(f"  ❌ 为域 [{domain}] 执行失败！")
        print(f"  - 错误信息: {e.stderr.strip()}")


# --- 主函数 ---
async def main():
    """主函数，负责整个自动化流程"""
    pygettext_path_str = os.getenv("pygettext_path") or input("请输入 'pygettext.py' 的绝对路径:\n")
    pygettext_script_path = Path(pygettext_path_str.strip())
    if not pygettext_script_path.is_file():
        print(f"错误: 无法找到 'pygettext.py' 脚本: {pygettext_script_path}")
        return
    print("-" * 50)

    # 1. 自动发现所有域和源文件
    print(f"正在扫描 '{SERVICES_DIR}' 目录以发现模块...")
    domains_to_scan = discover_domains_and_sources(SERVICES_DIR)
    if not domains_to_scan:
        print(f"未在 '{SERVICES_DIR}' 下发现任何有效的模块。")
        return
    print("发现以下模块（域）需要处理:", list(domains_to_scan.keys()))

    # 2. 为每个域生成 .pot 模板并修正编码头
    POT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for domain, sources in domains_to_scan.items():
        run_pygettext(pygettext_script_path, domain, sources, POT_OUTPUT_DIR)

    print("\n" + "=" * 50)
    print(".pot 模板文件生成并修正完毕。")

    # 3. 初始化语言目录并分发 .po 文件
    print("\n--- 正在初始化语言目录并分发 .po 文件 ---")
    all_po_files = []
    # 将 'en' 和其他支持的语言合并，统一处理目录创建
    all_langs_to_process = ["en"] + support_languages
    pot_files = list(POT_OUTPUT_DIR.glob("*.pot"))

    if not pot_files:
        print("  - 警告: 临时目录中没有 .pot 文件可以分发。")
    else:
        for lang in all_langs_to_process:
            target_dir = LOCALE_DIR / lang / "LC_MESSAGES"
            target_dir.mkdir(parents=True, exist_ok=True)
            for pot_file_path in pot_files:
                po_file_name = pot_file_path.with_suffix(".po").name
                target_po_path = target_dir / po_file_name
                all_po_files.append(target_po_path)
                if not target_po_path.exists():
                    shutil.copy(pot_file_path, target_po_path)
                    print(f"  ✔ 已创建: {target_po_path.relative_to(ROOT_PATH)}")
                else:
                    # 使用 polib 合并，而不是简单跳过，以加入新的翻译条目
                    print(f"  ℹ 文件已存在，正在合并: {target_po_path.relative_to(ROOT_PATH)}")
                    po = polib.pofile(str(target_po_path), encoding="utf-8")
                    pot = polib.pofile(str(pot_file_path), encoding="utf-8")
                    po.merge(pot)
                    po.save()

    # 4. 填充 'en' 目录的翻译文件 (msgstr=msgid)
    print("\n--- 正在填充 'en' 目录的翻译文件 (msgstr=msgid) ---")
    if EN_DIR.is_dir():
        for po_path in EN_DIR.glob("*.po"):
            po = polib.pofile(str(po_path), encoding="utf-8")
            if any(entry.msgid and not entry.msgstr for entry in po):
                for entry in po:
                    if entry.msgid and not entry.msgstr:
                        entry.msgstr = entry.msgid
                po.save()
                print(f"  ✔ 已填充并保存: {po_path.relative_to(ROOT_PATH)}")
    else:
        print(f"  - 警告: 未找到 'en' 目录: {EN_DIR}")

    # 5. 自动翻译
    if auto_translate and support_languages:
        print("\n" + "=" * 50)
        print("自动翻译已启用。")
        untranslated_msgids = set()
        po_files_to_translate = [p for p in all_po_files if p.parent.parent.name != "en"]

        for po_path in po_files_to_translate:
            if po_path.exists():
                po = polib.pofile(str(po_path), encoding="utf-8")
                for entry in po.untranslated_entries():
                    if entry.msgid:
                        untranslated_msgids.add(entry.msgid)

        if not untranslated_msgids:
            print("✔ 未发现需要翻译的新文本。")
        else:
            translations_map = await batch_translate_texts(untranslated_msgids, support_languages)
            print("\n--- 正在将翻译结果写回 .po 文件 ---")
            for po_path in po_files_to_translate:
                lang = po_path.parent.parent.name
                po = polib.pofile(str(po_path), encoding="utf-8")
                is_updated = False
                for entry in po.untranslated_entries():
                    if entry.msgid in translations_map and lang in translations_map[entry.msgid]:
                        entry.msgstr = translations_map[entry.msgid][lang]
                        is_updated = True
                if is_updated:
                    po.save()
                    print(f"  ✔ 已更新并保存: {po_path.relative_to(ROOT_PATH)}")

    # 6. 清理临时目录
    if POT_OUTPUT_DIR.exists():
        try:
            shutil.rmtree(POT_OUTPUT_DIR)
            print(f"\n🗑️ 已删除临时目录: {POT_OUTPUT_DIR}")
        except Exception as e:
            print(f"\n⚠️ 删除临时目录失败: {e}")

    print("\n" + "=" * 50)
    print("🎉 国际化脚本执行完毕。")


if __name__ == "__main__":
    # 在Windows上，为 asyncio 设置正确的事件循环策略，以兼容 googletrans-py
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
