#!/usr/bin/env python3
"""
AI内容生成器 — 自动生成汽服门店推广内容
批量生成：抖音文案、百家号文章、知乎问答、小红书图文

使用方法：
    python3 content_generator.py --shop-name "XX汽服" --city "深圳" --output-dir ./output
"""

import argparse
import os
import json
from datetime import datetime

try:
    from openai import OpenAI
except ImportError:
    print("请先安装 OpenAI 库: pip install openai")
    print("国内推荐使用兼容 OpenAI API 的国内模型服务（如 DeepSeek、百度千帆等）")
    exit(1)


class ContentGenerator:
    """汽服门店内容生成器"""

    def __init__(self, shop_name, city, services=None, api_key=None, base_url=None, model=None):
        self.shop_name = shop_name
        self.city = city
        self.services = services or ["洗车", "保养", "维修", "美容"]
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = model or os.getenv("CONTENT_MODEL", "gpt-4o-mini")
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def generate_douyin_script(self, topic, target_count=5):
        """批量生成抖音短视频脚本"""
        prompt = f"""你是一家汽车服务门店的营销策划专家。
门店名称：{self.shop_name}
所在城市：{self.city}
服务项目：{', '.join(self.services)}

请生成 {target_count} 条抖音短视频脚本，主题围绕「{topic}」。
每条脚本包括：
- 标题（含城市名+门店名）
- 文案（50-80字，口语化）
- 画面建议
- 热门话题标签

要求：真实、接地气、有实用价值，不要夸大宣传。"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=2000
        )

        return response.choices[0].message.content

    def generate_baijiahao_article(self, topic):
        """生成百家号文章"""
        prompt = f"""你是一家汽车服务门店的店长，写一篇百家号文章。
门店名称：{self.shop_name}
所在城市：{self.city}
服务项目：{', '.join(self.services)}
文章主题：{topic}

要求：
- 标题含城市关键词
- 800-1200字
- 结构：痛点引入 → 知识点科普 → 门店服务介绍 → 总结建议
- 自然植入门店名称和地址，不要硬广
- 通俗易懂，车主视角"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=3000
        )

        return response.choices[0].message.content

    def generate_zhihu_answer(self, question):
        """生成知乎回答"""
        prompt = f"""你是一个有多年经验的车主/汽车从业者，在知乎上回答问题。
门店背景：{self.shop_name}（{self.city}）的综合汽车服务门店
服务项目：{', '.join(self.services)}

问题：{question}

要求：
- 以真实车主/从业者口吻回答
- 包含专业知识和个人经验
- 自然提及门店服务，不要硬广
- 200-500字"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=1500
        )

        return response.choices[0].message.content

    def generate_xiaohongshu_post(self, topic):
        """生成小红书图文笔记"""
        prompt = f"""你是一家汽车服务门店的运营，写一篇小红书图文笔记。
门店名称：{self.shop_name}
所在城市：{self.city}
服务项目：{', '.join(self.services)}
主题：{topic}

要求：
- 标题要吸睛，带 emoji
- 正文简短实用（100-200字）
- 带城市标签和行业标签
- 配图建议（拍什么角度）
- 风格：真实分享，不要太官方"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=1000
        )

        return response.choices[0].message.content

    def generate_all(self, topics=None, output_dir="./output"):
        """一次性生成全平台内容包"""
        if topics is None:
            topics = {
                "douyin": ["夏季车辆保养", "洗车避坑指南", "轮胎安全检查"],
                "baijiahao": ["夏季用车5个必知保养技巧", "怎么判断该换轮胎了"],
                "zhihu": ["大家保养车一般都去哪？", "洗车店里几十和几百的洗车有什么区别？"],
                "xiaohongshu": ["终于找到靠谱洗车店了", "车辆保养日记"]
            }

        os.makedirs(output_dir, exist_ok=True)
        output = {}
        
        # 抖音脚本
        output["douyin"] = []
        for t in topics["douyin"]:
            print(f"  生成抖音脚本: {t}")
            content = self.generate_douyin_script(t, target_count=3)
            output["douyin"].append({"topic": t, "content": content})

        # 百家号文章
        output["baijiahao"] = []
        for t in topics["baijiahao"]:
            print(f"  生成百家号文章: {t}")
            content = self.generate_baijiahao_article(t)
            output["baijiahao"].append({"topic": t, "content": content})

        # 知乎回答
        output["zhihu"] = []
        for q in topics["zhihu"]:
            print(f"  生成知乎回答: {q}")
            content = self.generate_zhihu_answer(q)
            output["zhihu"].append({"question": q, "content": content})

        # 小红书
        output["xiaohongshu"] = []
        for t in topics["xiaohongshu"]:
            print(f"  生成小红书笔记: {t}")
            content = self.generate_xiaohongshu_post(t)
            output["xiaohongshu"].append({"topic": t, "content": content})

        # 保存到文件
        today = datetime.now().strftime('%Y%m%d')
        filepath = os.path.join(output_dir, f'content-pack-{today}.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        # 也输出可读的 Markdown 版本
        md_path = os.path.join(output_dir, f'content-pack-{today}.md')
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# 内容发布包 — {self.shop_name} ({self.city})\n")
            f.write(f"生成时间: {datetime.now().isoformat()}\n\n")
            
            f.write("## 抖音脚本\n\n")
            for item in output["douyin"]:
                f.write(f"### 主题：{item['topic']}\n\n{item['content']}\n\n---\n\n")
            
            f.write("## 百家号文章\n\n")
            for item in output["baijiahao"]:
                f.write(f"### {item['topic']}\n\n{item['content']}\n\n---\n\n")
            
            f.write("## 知乎回答\n\n")
            for item in output["zhihu"]:
                f.write(f"### 问题：{item['question']}\n\n{item['content']}\n\n---\n\n")
            
            f.write("## 小红书笔记\n\n")
            for item in output["xiaohongshu"]:
                f.write(f"### {item['topic']}\n\n{item['content']}\n\n---\n\n")

        print(f"\n✅ 内容包已生成：{filepath}")
        print(f"   Markdown 版本：{md_path}")
        return output


def main():
    parser = argparse.ArgumentParser(description='汽服门店AI内容生成器')
    parser.add_argument('--shop-name', required=True, help='门店名称')
    parser.add_argument('--city', required=True, help='所在城市')
    parser.add_argument('--services', nargs='+', default=["洗车", "保养", "维修", "美容"], help='服务项目')
    parser.add_argument('--output-dir', default='./output', help='输出目录')
    parser.add_argument('--api-key', help='OpenAI API Key（也可通过 OPENAI_API_KEY 环境变量设置）')
    parser.add_argument('--base-url', help='API 地址（国内可用 DeepSeek/千帆等兼容接口）')
    parser.add_argument('--model', default='gpt-4o-mini', help='模型名称')
    
    args = parser.parse_args()
    
    # 检查 API Key
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未设置 API Key！")
        print("   方式1: 传参 --api-key 'your-key'")
        print("   方式2: 设置环境变量 export OPENAI_API_KEY='your-key'")
        print("   国内推荐: 使用 DeepSeek API (兼容 OpenAI 格式，更便宜)")
        exit(1)
    
    print(f"\n📝 内容生成器 — {args.shop_name} ({args.city})")
    print(f"   服务项目: {', '.join(args.services)}")
    print(f"   模型: {args.model}")
    print(f"   API: {args.base_url or 'OpenAI 官方'}")
    print()
    
    generator = ContentGenerator(
        shop_name=args.shop_name,
        city=args.city,
        services=args.services,
        api_key=api_key,
        base_url=args.base_url,
        model=args.model
    )
    
    generator.generate_all(output_dir=args.output_dir)
    
    print(f"\n📋 接下来手动发布到各平台：")
    print(f"   抖音 → 打开抖音拍摄/上传，按脚本录制")
    print(f"   百家号 → 复制文章到百家号后台发布")
    print(f"   知乎 → 在相关问题下粘贴回答")
    print(f"   小红书 → 按笔记内容拍摄/发布")


if __name__ == '__main__':
    main()
