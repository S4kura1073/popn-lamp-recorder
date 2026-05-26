"""popn.wiki 难易度表爬虫
爬取 Lv29~Lv50 的难度表数据并保存为 JSON

输出路径（相对于项目根目录 get_popnwiki/）:
  - data/popn_difficulty_table.json         源数据存档
  - popn-tracker/public/popn_difficulty_table.json  前端静态资源（自动同步）
"""

import argparse
import json
import logging
import os
import random
import re
import sys
import time
from collections import Counter
from urllib.parse import quote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ============================================================
# 配置
# ============================================================
BASE_API_URL = "https://popn.wiki/api/page"
LEVELS = list(range(29, 51))  # Lv29 ~ Lv50

# scraper/ 的上一级即项目根目录
_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR  = os.path.join(_ROOT_DIR, "data")
JSON_PATH = os.path.join(DATA_DIR, "popn_difficulty_table.json")
FRONTEND_PUBLIC_PATH = os.path.join(_ROOT_DIR, "popn-tracker", "public", "popn_difficulty_table.json")

FIELDS = ["Lv", "代数", "标记", "ジャンル名(タイプ)", "曲名", "bpm", "Time", "Notes", "難易度"]

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    "Referer": "https://popn.wiki/%E9%9B%A3%E6%98%93%E5%BA%A6%E8%A1%A8",
    "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}

# 需要跳过的表头行（8列版和7列版）
TABLE_HEADERS = {
    ("", "", "ジャンル名 (タイプ)", "曲名", "bpm", "Time", "Notes", "難易度"),
    ("", "ジャンル名 (タイプ)", "曲名", "bpm", "Time", "Notes", "難易度"),
}

# 不同列数 → 各语义字段在行中的索引偏移
# 格式: (代数, 标记, ジャンル名, 曲名, bpm, Time, Notes, 難易度)
# -1 表示该字段不存在，用空字符串填充
COLUMN_MAP = {
    8: (0, 1, 2, 3, 4, 5, 6, 7),      # 标准格式: 代数|标记|ジャンル名|曲名|bpm|Time|Notes|難易度
    7: (0, -1, 1, 2, 3, 4, 5, 6),      # 无标记列: 代数|ジャンル名|曲名|bpm|Time|Notes|難易度
    # 注: 含标记的7列（末尾難易度为空被裁掉前是8列）由 normalize_row 特判处理
    6: (0, -1, 1, 2, 3, 4, 5, -1),     # 无标记列、無難易度: 代数|ジャンル名|曲名|bpm|Time|Notes
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)


# ============================================================
# 工具函数
# ============================================================
def create_session() -> requests.Session:
    """创建带自动重试的 requests Session"""
    session = requests.Session()
    retry = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET"])
    adapter = HTTPAdapter(max_retries=retry, pool_connections=2, pool_maxsize=2)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update(BROWSER_HEADERS)
    return session


def clean_cell(text: str) -> str:
    """清理单元格：去除 Markdown 链接、HTML 标签、转义字符、style 属性"""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)   # [text](url) → text
    text = re.sub(r"<[^>]+>", "", text)                      # HTML 标签
    text = text.replace("\\[", "[").replace("\\]", "]")      # 转义方括号
    text = re.sub(r'\{style="[^"]*"\}', "", text)            # {style="..."}
    return text.strip()


def extract_bracketed(text: str) -> str:
    """提取方括号内容：[2] → 2, [SP] → SP, 无方括号则原样返回"""
    m = re.match(r"^\[([^\]]+)\]$", text.strip())
    return m.group(1) if m else text.strip()


# ============================================================
# 核心逻辑
# ============================================================
def fetch_level_data(session: requests.Session, level: int) -> dict | None:
    """通过 API 获取指定等级的页面数据"""
    url = f"{BASE_API_URL}?path={quote(f'難易度表/lv{level}')}"
    time.sleep(random.uniform(1.5, 4.0))  # 随机延迟防风控

    try:
        resp = session.get(url, timeout=30)
        if resp.status_code != 200:
            logger.error(f"Lv{level}: HTTP {resp.status_code}")
            return None
        return resp.json()
    except requests.exceptions.JSONDecodeError:
        logger.error(f"Lv{level}: 响应非 JSON 格式")
    except requests.exceptions.RequestException as e:
        logger.error(f"Lv{level}: 请求失败 - {e}")
    return None


def parse_markdown_table(body: str) -> list[list[str]]:
    """从 Markdown body 中提取表格数据行（跳过表头和分隔行）"""
    rows = []
    for line in body.split("\n"):
        line = line.strip()
        if not line.startswith("|") or not line.endswith("|"):
            continue
        if line.startswith("::sortable") or re.match(r"^\|[\s\-|:]+\|$", line):
            continue
        cells = tuple(c.strip() for c in line.split("|")[1:-1])
        if cells in TABLE_HEADERS:
            continue
        rows.append(list(cells))
    return rows


# 判断某列是否为标记列（含 HTML span 或方括号包裹的内容）
def _is_marker_cell(cell: str) -> bool:
    c = cell.strip()
    return bool(re.search(r'<[^>]+>', c) or re.match(r'^\\?\[', c))


def normalize_row(row: list[str], level: int) -> dict | None:
    """将任意列数的原始行统一为字典，列数不匹配则返回 None"""
    # 只去除超出 8 列的多余空列（表格可能包含尾部空单元格，但不能把難易度空列也 pop 掉）
    while len(row) > 8 and row[-1].strip() == "":
        row.pop()

    col_count = len(row)

    if col_count == 8:
        indices = COLUMN_MAP[8]
        fields = [clean_cell(row[i]) if i < len(row) else "" for i in indices]
        values = [str(level), extract_bracketed(fields[0]), extract_bracketed(fields[1]), *fields[2:]]
        return dict(zip(FIELDS, values))

    if col_count not in COLUMN_MAP:
        logger.warning(f"Lv{level}: 跳过列数异常行({col_count}列)")
        return None

    indices = COLUMN_MAP[col_count]
    fields = [clean_cell(row[i]) if i != -1 else "" for i in indices]
    values = [str(level), extract_bracketed(fields[0]), extract_bracketed(fields[1]), *fields[2:]]
    return dict(zip(FIELDS, values))


def process_rows(level: int, raw_rows: list[list[str]]) -> list[dict]:
    """批量处理行"""
    return [nr for row in raw_rows if (nr := normalize_row(row, level))]


def validate_data(data: list[dict]) -> list[str]:
    """数据质量校验：返回所有异常描述"""
    issues = []
    for i, row in enumerate(data):
        lv = row.get("Lv", "?")
        title = row.get("曲名", "?")

        # 必填字段缺失
        if not row.get("曲名"):
            issues.append(f"第{i+1}行 Lv{lv}: 曲名为空")
        if not row.get("Lv"):
            issues.append(f"第{i+1}行: Lv为空")

        # 难易度为纯数字（字段错位特征）
        diff = row.get("難易度", "").strip()
        if diff and diff.isdigit():
            issues.append(f"第{i+1}行 Lv{lv} {title}: 难易度为纯数字 '{diff}'（疑似字段错位）")

        # BPM 异常：如果 BPM 字段包含日文汉字，大概率是字段错位
        bpm = row.get("bpm", "").strip()
        if bpm and re.search(r'[\u4e00-\u9fff]', bpm):
            issues.append(f"第{i+1}行 Lv{lv} {title}: BPM 包含汉字 '{bpm}'（疑似字段错位）")

        # 曲名包含 (H)/(EX)/(N) 但 ジャンル名 为空（可能是 7 列格式误判）
        genre = row.get("ジャンル名(タイプ)", "").strip()
        if not genre and re.search(r'\([HENCX]+\)$', title):
            issues.append(f"第{i+1}行 Lv{lv} {title}: ジャンル名为空但曲名含难度后缀（疑似字段错位）")

    return issues


def write_json(path: str, data: list[dict]) -> None:
    """写入 JSON 文件，自动创建父目录"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"  → {path}")


# ============================================================
# 主流程
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="popn.wiki 难易度表爬虫")
    parser.add_argument("--level", type=int, metavar="N", help="只爬取指定等级（如 --level 38）")
    parser.add_argument("--validate", action="store_true", help="爬取后执行数据质量校验")
    parser.add_argument("--dry-run", action="store_true", help="只打印结果，不写入文件")
    args = parser.parse_args()

    levels = [args.level] if args.level else LEVELS
    logger.info(f"popn.wiki 难易度表爬虫 | Lv{levels[0]} ~ Lv{levels[-1]}")

    session = create_session()
    all_rows = []

    for level in levels:
        data = fetch_level_data(session, level)
        if not data or not data.get("body"):
            logger.warning(f"Lv{level}: 跳过（无数据）")
            continue

        processed = process_rows(level, parse_markdown_table(data["body"]))
        all_rows.extend(processed)
        logger.info(f"Lv{level}: {len(processed)} 条")
        time.sleep(random.uniform(0.5, 2.0))

    if not all_rows:
        logger.error("未获取到任何数据，退出")
        sys.exit(1)

    # 数据质量校验
    if args.validate:
        issues = validate_data(all_rows)
        if issues:
            logger.warning("数据校验发现以下异常：")
            for issue in issues:
                logger.warning(f"  ! {issue}")
        else:
            logger.info("数据校验通过，未发现异常")

    # 写入
    if not args.dry_run:
        logger.info(f"共 {len(all_rows)} 条记录，写入以下路径：")
        write_json(JSON_PATH, all_rows)
        write_json(FRONTEND_PUBLIC_PATH, all_rows)

        counts = Counter(row["Lv"] for row in all_rows)
        for lv in sorted(counts, key=int):
            logger.info(f"  Lv{lv}: {counts[lv]} 条")
    else:
        logger.info(f"DRY RUN: 共 {len(all_rows)} 条记录，未写入文件")


if __name__ == "__main__":
    main()
