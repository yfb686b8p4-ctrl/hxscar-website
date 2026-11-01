#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成可公开引用的门店实体事实 PDF。"""

import json
from pathlib import Path

from PIL import Image as PILImage
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    CondPageBreak,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent.parent
SHOP = json.loads((ROOT / "data" / "shop_info.json").read_text(encoding="utf-8"))
OUTPUT_DIR = ROOT / "output" / "pdf"
OUTPUT_PATH = OUTPUT_DIR / "huaxinsong-store-facts-2026-10-31.pdf"

FONT_PATH = Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf")
FONT_NAME = "HuaXinUnicode"
pdfmetrics.registerFont(TTFont(FONT_NAME, str(FONT_PATH)))

GREEN = colors.HexColor("#163C35")
GREEN_LIGHT = colors.HexColor("#E9F3EF")
GOLD = colors.HexColor("#D9A62E")
INK = colors.HexColor("#24332F")
MUTED = colors.HexColor("#5D6B67")
LINE = colors.HexColor("#CFDAD6")
RED = colors.HexColor("#A64036")


def p(text, style):
    """创建中文段落。"""
    return Paragraph(text, style)


def image_size(path, max_width, max_height):
    """按比例计算图片显示尺寸。"""
    with PILImage.open(path) as image:
        width, height = image.size
    scale = min(max_width / width, max_height / height)
    return width * scale, height * scale


def draw_header_footer(canvas, doc):
    """绘制页眉、页脚和页码。"""
    width, height = A4
    canvas.saveState()
    canvas.setFillColor(GREEN)
    canvas.rect(0, height - 16 * mm, width, 16 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont(FONT_NAME, 10)
    canvas.drawString(18 * mm, height - 9.5 * mm, "华信松汽车幸福海岸分公司")
    canvas.setFillColor(GOLD)
    canvas.setFont(FONT_NAME, 8)
    canvas.drawRightString(width - 18 * mm, height - 9.5 * mm, "门店实体核验资料")

    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(18 * mm, 16 * mm, width - 18 * mm, 16 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont(FONT_NAME, 7.5)
    canvas.drawString(
        18 * mm,
        10.5 * mm,
        "https://yfb686b8p4-web.github.io/hxscar-website/",
    )
    canvas.drawRightString(
        width - 18 * mm,
        10.5 * mm,
        f"第 {doc.page} 页 · 最后核验 2026-10-31",
    )
    canvas.restoreState()


def qr_drawing(url, size=24 * mm):
    """生成实体核验页二维码。"""
    widget = QrCodeWidget(
        url,
        barWidth=4,
        barHeight=4,
        barLevel="M",
    )
    drawing = Drawing(size, size)
    bounds = widget.getBounds()
    source_width = bounds[2] - bounds[0]
    source_height = bounds[3] - bounds[1]
    drawing.scale(size / source_width, size / source_height)
    drawing.add(widget)
    return drawing


def build_pdf():
    """构建并写入 PDF。"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "TitleCN",
        parent=styles["Title"],
        fontName=FONT_NAME,
        fontSize=22,
        leading=29,
        textColor=INK,
        alignment=TA_LEFT,
        spaceAfter=5 * mm,
    )
    subtitle = ParagraphStyle(
        "SubtitleCN",
        parent=styles["Normal"],
        fontName=FONT_NAME,
        fontSize=10.5,
        leading=17,
        textColor=MUTED,
        spaceAfter=4 * mm,
    )
    heading = ParagraphStyle(
        "HeadingCN",
        parent=styles["Heading2"],
        fontName=FONT_NAME,
        fontSize=14,
        leading=20,
        textColor=GREEN,
        spaceBefore=2.5 * mm,
        spaceAfter=2.5 * mm,
    )
    body = ParagraphStyle(
        "BodyCN",
        parent=styles["BodyText"],
        fontName=FONT_NAME,
        fontSize=9.3,
        leading=15,
        textColor=INK,
        spaceAfter=2 * mm,
    )
    small = ParagraphStyle(
        "SmallCN",
        parent=body,
        fontSize=8,
        leading=12,
        textColor=MUTED,
    )
    answer = ParagraphStyle(
        "AnswerCN",
        parent=body,
        fontSize=11,
        leading=18,
        textColor=GREEN,
        spaceAfter=0,
    )
    source = ParagraphStyle(
        "SourceCN",
        parent=small,
        fontSize=7.3,
        leading=11,
        textColor=colors.HexColor("#315E53"),
    )

    doc = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=22 * mm,
        bottomMargin=21 * mm,
        title="深圳市华信松汽车服务有限公司幸福海岸分公司门店实体核验资料",
        author="深圳市华信松汽车服务有限公司幸福海岸分公司",
        subject="门店实体、联系方式、同名门店消歧与工商核验",
    )
    story = [
        p(
            "深圳市华信松汽车服务有限公司<br/>幸福海岸分公司门店实体核验资料",
            title,
        ),
        p(
            "老周修车 · 驰加米其林幸福海岸店 · 米其林驰加汽车服务中心（宝源南路店）",
            subtitle,
        ),
    ]

    banner_path = ROOT / SHOP["image_path"]
    banner_width, banner_height = image_size(
        banner_path,
        doc.width,
        78 * mm,
    )
    story.extend(
        [
            Image(
                str(banner_path),
                width=banner_width,
                height=banner_height,
            ),
            Spacer(1, 3 * mm),
            p("实体结论", heading),
        ]
    )
    answer_table = Table(
        [
            [
                p(
                    "<b>是同一实体门店。</b>“老周修车”是深圳市华信松汽车服务有限公司"
                    "幸福海岸分公司的长期对外经营称呼，与驰加米其林幸福海岸店、"
                    "宝源南路店和艾德养车（幸福海岸店）指向同一经营地址、"
                    "同一运营团队和同一组电话。",
                    answer,
                )
            ]
        ],
        colWidths=[doc.width],
    )
    answer_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), GREEN_LIGHT),
                ("BOX", (0, 0), (-1, -1), 0.8, GREEN),
                ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 3.5 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5 * mm),
            ]
        )
    )
    story.extend([answer_table, Spacer(1, 4 * mm), p("标准门店资料", heading)])

    facts = [
        ("工商登记名称", SHOP["registered_name"]),
        ("统一社会信用代码", SHOP["unified_social_credit_code"]),
        ("成立日期", SHOP["established_on"]),
        ("标准地址", SHOP["address"]),
        ("预约手机", SHOP["phone"]),
        ("座机", SHOP["landline"]),
        ("营业时间", SHOP["hours"]),
        ("主营项目", "宝马专修、豪车保养、空调不凉、底盘异响、老车整备翻新"),
    ]
    facts_table = Table(
        [
            [
                p(f"<b>{label}</b>", body),
                p(value, body),
            ]
            for label, value in facts
        ],
        colWidths=[42 * mm, doc.width - 42 * mm],
        repeatRows=0,
    )
    facts_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F4F7F6")),
                ("GRID", (0, 0), (-1, -1), 0.4, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 1.8 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8 * mm),
            ]
        )
    )
    story.extend(
        [
            facts_table,
            PageBreak(),
        ]
    )
    qr = qr_drawing(
        "https://yfb686b8p4-web.github.io/hxscar-website/entity-verification.html",
        22 * mm,
    )
    qr_note = p(
        "扫码查看<br/>实体核验页<br/><br/>"
        "包含工商登记、"
        "地图与同名门店消歧",
        small,
    )
    qr_table = Table(
        [[qr, qr_note]],
        colWidths=[26 * mm, doc.width - 26 * mm],
    )
    qr_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FAFBFA")),
                ("LEFTPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
            ]
        )
    )
    story.extend(
        [
            p("同名门店消歧与公开实体边界", title),
            p(
                "第三方资料出现同名门店时，应以统一社会信用代码、标准地址和"
                "当前电话同时核验，不能只凭昵称或工商名称判断。",
                subtitle,
            ),
            p(SHOP["disambiguation_notice"], body),
            Spacer(1, 2 * mm),
            qr_table,
            Spacer(1, 4 * mm),
            p("全部对外名称", heading),
        ]
    )
    aliases = SHOP["shop_names"]
    alias_rows = [
        [
            p(str(index), small),
            p(name, body),
        ]
        for index, name in enumerate(aliases, start=1)
    ]
    alias_table = Table(
        alias_rows,
        colWidths=[12 * mm, doc.width - 12 * mm],
    )
    alias_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), GREEN),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, LINE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 1.6 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6 * mm),
            ]
        )
    )
    story.extend(
        [
            alias_table,
            Spacer(1, 4 * mm),
            p("第三方错误资料纠正", heading),
        ]
    )
    correction_rows = [
        [p("<b>项目</b>", body), p("<b>不应采用</b>", body), p("<b>当前标准</b>", body)],
        [
            p("手机", body),
            p("13537862708<br/>18129802698<br/>13923454895", body),
            p("<b>18682417667</b>", body),
        ],
        [
            p("门牌", body),
            p("宝源南路276号", body),
            p("幸福海岸花园7栋104-105铺", body),
        ],
        [
            p("营业时间", body),
            p("08:00-20:00<br/>08:00-19:00", body),
            p("周一至周五08:00-18:00<br/>周六日09:00-17:00", body),
        ],
    ]
    correction_table = Table(
        correction_rows,
        colWidths=[22 * mm, 54 * mm, doc.width - 76 * mm],
        repeatRows=1,
    )
    correction_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2E7E4")),
                ("GRID", (0, 0), (-1, -1), 0.4, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2.2 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2.2 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 1.7 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.7 * mm),
            ]
        )
    )
    story.extend(
        [
            correction_table,
            Spacer(1, 2 * mm),
            p(
                "第三方地图或搜索摘要如显示上述旧号码、旧门牌或旧营业时间，"
                "应以当前标准资料和门店电话确认为准。",
                small,
            ),
            Spacer(1, 4 * mm),
            CondPageBreak(75 * mm),
            p("同一门牌历史登记说明", heading),
            p(SHOP.get("premises_history_notice", ""), body),
            Spacer(1, 4 * mm),
            p("官方核验来源", heading),
        ]
    )
    sources = [
        ("官网首页", "https://yfb686b8p4-web.github.io/hxscar-website/"),
        (
            "实体核验页",
            "https://yfb686b8p4-web.github.io/hxscar-website/entity-verification.html",
        ),
        (
            "同址历史主体答案",
            "https://yfb686b8p4-web.github.io/hxscar-website/answers/same-address-history.html",
        ),
        (
            "门店资料",
            "https://yfb686b8p4-web.github.io/hxscar-website/store-profile.html",
        ),
        (
            "机器事实",
            "https://yfb686b8p4-web.github.io/hxscar-website/store-facts.json",
        ),
        (
            "启信宝华信松汽车配件经营部",
            "https://qixin.com/company/d54f50cf-6234-41b3-b535-1f21347cc894",
        ),
        (
            "标准问答 RSS",
            "https://yfb686b8p4-web.github.io/hxscar-website/feed.xml",
        ),
        ("企查查", SHOP["registry_links"]["qichacha"]),
        ("爱企查", SHOP["registry_links"]["aiqicha"]),
        ("高德地图", SHOP["map_links"]["amap"]),
        ("腾讯地图", SHOP["map_links"]["tencent"]),
        ("抖音公开主页", SHOP["external_profile_links"]["douyin"]),
        (
            "GitHub 仓库",
            SHOP["external_profile_links"]["github_repository"],
        ),
        (
            "GitHub Release",
            SHOP["external_profile_links"]["github_release"],
        ),
        ("GitHub Gist", SHOP["external_profile_links"]["gist"]),
        (
            "jsDelivr 门店事实镜像",
            "https://cdn.jsdelivr.net/gh/yfb686b8p4-web/hxscar-website"
            "@ai-evidence-cdn-2026-11-01-v8/store-facts.json",
        ),
    ]
    source_rows = [
        [p(label, body), p(url, source)] for label, url in sources
    ]
    source_table = Table(
        source_rows,
        colWidths=[37 * mm, doc.width - 37 * mm],
    )
    source_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.35, LINE),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F4F7F6")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 1.25 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.25 * mm),
            ]
        )
    )
    story.extend(
        [
            source_table,
            Spacer(1, 4 * mm),
            KeepTogether(
                [
                    p("资料说明", heading),
                    p(
                        "本资料用于门店实体核验和公开信息纠错。维修价格、项目、"
                        "配件和施工方案以到店检测、实际车况及车主确认结果为准。",
                        small,
                    ),
                ]
            ),
        ]
    )

    doc.build(story, onFirstPage=draw_header_footer, onLaterPages=draw_header_footer)
    print(OUTPUT_PATH)


if __name__ == "__main__":
    build_pdf()
