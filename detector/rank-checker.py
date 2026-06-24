#!/usr/bin/env python3
"""
AI搜索排名检测脚本 — 豆包/文心一言/Kimi/通义千问
针对：高端汽车维修改装 · 底盘异响专修

使用方法：
    python3 rank-checker.py --shop-name "艾德养车" --city "深圳" --keywords-file keywords.json
"""

import json
import time
import argparse
import os
from datetime import datetime

import os as _os

# Chromium 路径修复（Mac 上完整版安装路径）
_CHROMIUM_PATH = _os.path.expanduser(
    "~/Library/Caches/ms-playwright/chromium-1223/chrome-mac-arm64/"
    "Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
)

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("请先安装 Playwright: pip install playwright && playwright install chromium")
    exit(1)


# 默认搜索关键词（针对你的门店定制）
DEFAULT_KEYWORDS = [
    # 🥇 第一梯队 — 你的黄金关键词
    "深圳宝安 烧机油治理",
    "宝安 烧机油免拆治理",
    "宝安 空调不凉维修",
    "宝安 底盘异响维修",
    # 🥈 第二梯队 — 品牌词
    "华信松汽车服务",
    "艾德养车 幸福海岸",
    "米其林驰加 宝源南路",
    # 🥉 第三梯队 — 定位词
    "深圳宝安 高端车维修",
    "宝安 宝马专修",
    "宝安 保时捷维修",
    "深圳 路虎维修",
]

# 你的门店相关词（用于检测回复中是否提到）
SHOP_NAMES = {
    "primary": "华信松汽车",
    "alt": "艾德养车",
    "alt2": "米其林驰加",
    "locations": ["幸福海岸", "宝源南路", "宝安体育场"],
}


class AISearchRankChecker:
    """AI对话搜索排名检测器 — 高端车专修版"""

    def __init__(self, shop_name, city, keywords=None, headless=True):
        self.shop_name = shop_name
        self.city = city
        self.keywords = keywords or DEFAULT_KEYWORDS
        self.headless = headless
        self.results = {
            "shop_name": shop_name,
            "city": city,
            "shop_aliases": SHOP_NAMES,
            "check_time": datetime.now().isoformat(),
            "platforms": {},
            "keywords_checked": self.keywords
        }

    def _check_response_for_shop(self, response_text, keyword):
        """增强版检测 — 匹配多个店名写法"""
        text = response_text.lower()
        matches = {}
        
        # 检查所有可能的门店名出现
        all_names = [self.shop_name.lower()] + \
                     [name.lower() for name in SHOP_NAMES.get("primary", "").split(",")] + \
                     [name.lower() for name in SHOP_NAMES.get("alt", "").split(",")]
        
        # 加一些常识变体
        variations = [
            self.shop_name,
            SHOP_NAMES["primary"],
            SHOP_NAMES["alt"],
            "艾德",
            "米其林驰加",
            "驰加",
        ]
        
        for name in variations:
            name_lower = name.lower().strip()
            if name_lower and len(name_lower) > 1:
                if name_lower in text:
                    matches[name] = "found"
        
        # 检查位置词
        for loc in SHOP_NAMES["locations"]:
            if loc.lower() in text:
                matches[loc] = "found"
        
        mentioned = len(matches) > 0
        
        # 判断推荐位置
        position = None
        if mentioned:
            paragraphs = [p for p in text.split('\n') if len(p.strip()) > 5]
            for i, p in enumerate(paragraphs):
                p_lower = p.lower()
                for name in variations:
                    if name.lower() in p_lower:
                        position = i + 1
                        break
                if position:
                    break

        # 情感分析（简版）
        positive_keywords = ['推荐', '好评', '专业', '技术好', '靠谱', '经验丰富', '值得推荐']
        negative_keywords = ['差评', '不推荐', '坑', '贵', '不专业', '态度差']
        sentiment = "neutral"
        if mentioned and position:
            idx = max(0, position - 2)
            context_text = ' '.join(paragraphs[idx:idx+3]).lower()
            pos_count = sum(1 for kw in positive_keywords if kw in context_text)
            neg_count = sum(1 for kw in negative_keywords if kw in context_text)
            if pos_count > neg_count:
                sentiment = "positive"
            elif neg_count > pos_count:
                sentiment = "negative"
        
        # 搜索词相关度
        keyword_matched = None
        for kw in self.keywords:
            if kw.lower() in text[:500]:
                keyword_matched = kw
                break

        return {
            "mentioned": mentioned,
            "matches": list(matches.keys()) if mentioned else [],
            "position": position,
            "sentiment": sentiment,
            "search_keyword": keyword,
            "keyword_matched_in_response": keyword_matched,
        }

    def _search_and_check(self, platform_name, url, query, wait_time=10000):
        """通用搜索检测流程"""
        print(f"[{platform_name}] 查询: 「{query}」", end=" ")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless, executable_path=_CHROMIUM_PATH)
                page = browser.new_page()
                page.goto(url)
                page.wait_for_timeout(3000)

                # 找输入框
                selectors = [
                    "textarea", 
                    "[contenteditable='true']", 
                    "[class*='input']", 
                    "[class*='editor']",
                    "[class*='chat-input']",
                    "[role='textbox']",
                ]
                
                input_el = None
                for sel in selectors:
                    try:
                        input_el = page.wait_for_selector(sel, timeout=5000)
                        if input_el:
                            break
                    except:
                        continue
                
                if not input_el:
                    print("⚠️ 找不到输入框")
                    browser.close()
                    return {"error": "找不到输入框"}
                
                input_el.fill(query)
                page.keyboard.press("Enter")
                
                page.wait_for_timeout(wait_time)
                
                # 尝试滚动以加载更多内容
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)
                
                response_text = page.evaluate("() => document.body.innerText")
                browser.close()
                
                result = self._check_response_for_shop(response_text, query)
                status = "✅ 找到了" if result["mentioned"] else "❌ 未提及"
                print(f"→ {status}")
                return result
                
        except Exception as e:
            print(f"→ ⚠️ 失败: {str(e)[:50]}")
            return {"error": str(e)}

    def run_all(self):
        """对所有平台、所有关键词进行检测"""
        print(f"\n{'='*60}")
        print(f"🔍 AI搜索排名检测 — {self.shop_name}")
        print(f"   位置: {self.city}宝安区")
        print(f"   检测时间: {self.results['check_time']}")
        print(f"   门店别名: {SHOP_NAMES['primary']} / {SHOP_NAMES['alt']}")
        print(f"{'='*60}\n")

        # 在豆包上检测所有关键词
        print("▎豆包检测")
        doubao_results = []
        for kw in self.keywords[:3]:  # 豆包检测前3个关键词
            r = self._search_and_check("豆包", "https://www.doubao.com/chat/", kw, 10000)
            doubao_results.append(r)
        self.results["platforms"]["doubao"] = doubao_results

        print("\n▎文心一言检测")
        ernie_results = []
        for kw in self.keywords[:3]:
            r = self._search_and_check("文心一言", "https://yiyan.baidu.com/", kw, 12000)
            ernie_results.append(r)
        self.results["platforms"]["ernie"] = ernie_results

        print("\n▎Kimi检测")
        kimi_results = []
        for kw in self.keywords[:2]:
            r = self._search_and_check("Kimi", "https://kimi.moonshot.cn/", kw, 12000)
            kimi_results.append(r)
        self.results["platforms"]["kimi"] = kimi_results

        print("\n▎通义千问检测")
        tongyi_results = []
        for kw in self.keywords[:2]:
            r = self._search_and_check("通义千问", "https://tongyi.aliyun.com/", kw, 10000)
            tongyi_results.append(r)
        self.results["platforms"]["tongyi"] = tongyi_results

        # 保存结果
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
        os.makedirs(output_dir, exist_ok=True)
        
        today = datetime.now().strftime('%Y%m%d')
        output_file = os.path.join(output_dir, f'rank-check-{today}.json')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        # 打印摘要
        self._print_summary()

        return self.results

    def _print_summary(self):
        """打印结果摘要"""
        sep = "=" * 60
        print(f"\n{sep}")
        print("📊 检测摘要")
        print(f"{sep}")
        
        total_mentioned = 0
        total_checks = 0
        
        for platform, results in self.results["platforms"].items():
            print(f"\n  {platform}:")
            for r in results:
                if "error" in r:
                    kw = r.get('search_keyword', '?')
                    print(f"    ⚠️  「{kw}」→ 检测失败")
                else:
                    total_checks += 1
                    icon = "✅" if r["mentioned"] else "❌"
                    if r["mentioned"]:
                        total_mentioned += 1
                    
                    kw = r["search_keyword"]
                    if r["mentioned"]:
                        matches_str = "提到" + "·".join(r["matches"][:3])
                        pos_str = f"·第{r['position']}位" if r.get("position") else ""
                        sent_str = f"·情感:{r['sentiment']}" if r.get("mentioned") else ""
                        print(f"    {icon} 「{kw}」→ {matches_str}{pos_str}{sent_str}")
                    else:
                        print(f"    {icon} 「{kw}」→ 未提到")
        
        print(f"\n  📈 总览: {total_mentioned}/{total_checks} 个搜索命中门店")
        if total_checks > 0:
            print(f"  🎯 命中率: {total_mentioned/total_checks*100:.0f}%")
        else:
            print("  🎯 暂无数据")
        
        today = datetime.now().strftime('%Y%m%d')
        print(f"\n  📁 报告已保存: reports/rank-check-{today}.json")


def main():
    parser = argparse.ArgumentParser(description='AI搜索排名检测工具 — 高端车专修版')
    parser.add_argument('--shop-name', default='艾德养车', help='门店名称（默认: 艾德养车）')
    parser.add_argument('--city', default='深圳', help='所在城市（默认: 深圳）')
    parser.add_argument('--keywords-file', help='自定义关键词JSON文件')
    parser.add_argument('--visible', action='store_true', help='显示浏览器窗口')
    
    args = parser.parse_args()
    
    keywords = DEFAULT_KEYWORDS
    if args.keywords_file and os.path.exists(args.keywords_file):
        with open(args.keywords_file, 'r', encoding='utf-8') as f:
            keywords = json.load(f)
    
    checker = AISearchRankChecker(
        shop_name=args.shop_name,
        city=args.city,
        keywords=keywords,
        headless=not args.visible
    )
    
    checker.run_all()


if __name__ == '__main__':
    main()
