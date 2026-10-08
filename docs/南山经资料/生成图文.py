"""从资料卡生成 Markdown、静态浏览版、六张原文要素示意图及图像来源清单。

仅使用 Python 标准库；运行：python docs/南山经资料/生成图文.py
三张古籍 SVG 保留下载原文件，本脚本不修改。
"""
from pathlib import Path
import hashlib
import html
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "资料卡.json").read_text(encoding="utf-8"))
IMAGES = ROOT / "images"
IMAGES.mkdir(exist_ok=True)


def text(x, y, value, size=23, fill="#253e3a", weight="400", anchor="start"):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{html.escape(value)}</text>'


def box(x, y, width, height, fill="#fffdf7", stroke="#c7d1c4", radius=14):
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'


def line(x1, y1, x2, y2, color="#497e8a", arrow=False, dash=False):
    return f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{color}" stroke-width="4" fill="none"' + (' marker-end="url(#arrow)"' if arrow else '') + (' stroke-dasharray="9 7"' if dash else '') + '/>'


def tree(x, y, scale=1):
    return f'<g transform="translate({x} {y}) scale({scale})"><path d="M0,10 V100" stroke="#67533c" stroke-width="13"/><path d="M0,-60 C-75,-44 -85,5 -48,22 C-81,70 -6,79 3,50 C66,74 99,22 48,0 C65,-44 20,-73 0,-60Z" fill="#668477"/></g>'


def svg(title, description, content):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="620" viewBox="0 0 1120 620" role="img" aria-labelledby="title desc">
<title id="title">{html.escape(title)}</title><desc id="desc">{html.escape(description)}</desc>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10Z" fill="#497e8a"/></marker></defs>
<rect width="1120" height="620" fill="#f4f0e5"/>
<g font-family="Microsoft YaHei, Noto Sans CJK SC, sans-serif">
{text(44, 52, title, 30, weight='700')}
{text(44, 85, description, 17, '#626e63')}
{content}
<path d="M44,557 H1076" stroke="#d1cfbd"/>
{text(44, 590, '原文要素示意 · 本次绘制 · 无比例尺 · 图形、摆位与尺寸不构成原著记载', 18, '#626e63')}
</g></svg>'''


diagrams = {}
diagrams["zhaoyao-ecology.svg"] = svg("招摇山 · 山、海、草木与金玉", "临西海与同山要素的关系；图中摆位不表示原文规定的植被分带。", ''.join([
    '<path d="M40,490 L210,210 L315,330 L440,175 L650,490Z" fill="#bec9b3" stroke="#78917c" stroke-width="3"/>',
    '<path d="M40,493 H730 V535 H40Z" fill="#c1b18c"/>',
    '<path d="M735,280 Q795,260 855,280 T1076,280 V535 H735Z" fill="#a8c9cc"/>',
    text(852, 388, "西海", 30, '#335f6b'), text(766, 450, "临海关系", 21),
    tree(206, 308, .64), tree(447, 293, .75),
    text(142, 219, "桂", 23, weight='700'), text(424, 192, "迷榖", 23, weight='700'),
    box(510, 112, 288, 100), text(532, 146, "如榖 · 黑理 · 花四照", 21), text(532, 184, "佩之不迷", 22),
    line(525, 215, 482, 250, dash=True),
    '<path d="M335,477 Q310,437 311,409 M335,477 Q333,425 344,399 M335,477 Q366,424 380,428" stroke="#5c8176" stroke-width="6" fill="none"/>',
    '<circle cx="311" cy="409" r="8" fill="#678f8d"/><circle cx="344" cy="399" r="8" fill="#678f8d"/>',
    text(350, 351, "祝余", 23, weight='700'), text(445, 418, "如韭 · 青花", 22), text(445, 454, "食之不饥", 22),
    '<path d="M80,493 L100,451 L139,473 L147,493Z" fill="#bf9a54"/>', text(75, 531, "多金玉", 20),
    box(816, 125, 260, 98), text(837, 163, "同山还有狌狌", 22), text(837, 198, "未记其具体食性", 20),
]))

diagrams["qingqiu-ecology.svg"] = svg("青丘山 · 坡向与水陆要素", "北侧为阴、南侧为阳采用传统释义；箭头仅标水流，不标捕食关系。", ''.join([
    box(44, 117, 430, 421),
    text(71, 157, "资源剖面示意", 23, weight='700'),
    '<path d="M78,385 L255,207 L443,385Z" fill="#bbc9b9" stroke="#78917c" stroke-width="3"/>',
    text(80, 218, "北 / 阴", 22), text(350, 218, "南 / 阳", 22),
    text(78, 412, "多青䨼（青雘）", 20), text(340, 412, "多玉", 22),
    text(73, 458, "陆兽：九尾狐", 23), text(73, 497, "鸟类：灌灌", 23),
    box(517, 117, 559, 421),
    text(545, 157, "水系关系示意", 23, weight='700'),
    box(547, 188, 220, 64, '#e7eddf'), text(657, 229, "青丘之山", 24, anchor='middle'),
    line(657, 255, 657, 312, arrow=True), text(690, 295, "发源", 20),
    box(547, 322, 220, 64, '#dbeaed'), text(657, 363, "英水", 24, anchor='middle'),
    line(657, 389, 657, 443, arrow=True), text(690, 428, "南流", 20),
    box(547, 454, 220, 64, '#b6d1d2'), text(657, 496, "即翼之泽", 24, anchor='middle'),
    box(804, 294, 241, 104), text(824, 332, "水中多赤鱬", 23), text(824, 370, "鱼形 · 人面", 21),
    line(804, 346, 769, 346, dash=True),
    text(801, 466, "不与柜山同名", 20), text(801, 498, "英水自动合并", 20),
]))

diagrams["nanyu-ecology.svg"] = svg("南禺山 · 季节水穴", "季节读法依据识典古籍 S1；维基文库对应处有异文，秋季未记。", ''.join([
    text(52, 140, "山上多金玉 / 山下多水", 22), text(600, 140, "佐水 → 东南入海；另有凤皇、鵷鶵", 20),
    *[box(x, 174, 320, 330) for x in (44, 400, 756)],
    *[text(x+160, 221, label, 27, weight='700', anchor='middle') for x, label in ((44,'春 · 水入'),(400,'夏 · 水出'),(756,'冬 · 闭'))],
    *[f'<path d="M{x+38},418 L{x+68},319 Q{x+160},227 {x+254},319 L{x+283},418Z" fill="#bfbdad"/><path d="M{x+109},417 V350 Q{x+160},276 {x+211},350 V417Z" fill="#555f58"/>' for x in (44,400,756)],
    line(71, 380, 197, 380, arrow=True), line(566, 380, 699, 380, arrow=True),
    '<path d="M872,322 L961,412 M961,322 L872,412" stroke="#a76345" stroke-width="5" stroke-dasharray="9 6"/>',
    text(204, 472, "水在春季进入", 21, anchor='middle'), text(560, 472, "夏季才出来", 21, anchor='middle'), text(916, 472, "封闭原因未说明", 21, anchor='middle'),
    text(46, 538, "水穴与佐水未明确连通；不据季节描述推定机关、冰冻或凤鸟穴居。", 21),
]))

diagrams["chengshan-space.svg"] = svg("成山 · 四方而三坛", "层叠轮廓为形态示意，正文没有建筑尺寸、台阶、屋顶或建造者。", ''.join([
    '<path d="M91,425 L444,338 L678,431 L326,515Z" fill="#a4b39b" stroke="#607c66" stroke-width="3"/>',
    '<path d="M91,425 V462 L326,548 V515Z M326,515 V548 L678,464 V431Z" fill="#83967b"/>',
    '<path d="M175,340 L443,274 L608,339 L340,406Z" fill="#b8c5a9" stroke="#607c66" stroke-width="3"/>',
    '<path d="M175,340 V378 L340,444 V406Z M340,406 V444 L608,377 V339Z" fill="#96a889"/>',
    '<path d="M269,255 L443,211 L545,255 L371,299Z" fill="#d0d6ba" stroke="#607c66" stroke-width="3"/>',
    '<path d="M269,255 V297 L371,340 V299Z M371,299 V340 L545,297 V255Z" fill="#aaba99"/>',
    text(365, 183, "三重坛状山体", 25, weight='700'),
    box(709, 122, 365, 168), text(736, 164, "正文", 24, weight='700'), text(736, 206, "四方而三坛", 27), text(736, 254, "上多金玉 / 下多青䨼", 22),
    box(709, 314, 365, 186), text(736, 355, "古注（S2 所附）", 23, weight='700'), text(736, 398, "形如人筑，坛相累也", 24), text(736, 449, "‘形如’不是建造事实", 22), text(736, 480, "不能直接认定人工祭坛", 22),
]))

diagrams["queshan-ritual-space.svg"] = svg("鹊山祭祀 · 材料与动作", "两个信息框不是场地平面图；祭礼转录有标点及用字差异，仅取可核对要素。", ''.join([
    box(44, 126, 484, 404), box(572, 126, 504, 404),
    text(76, 170, "白菅为席 / 糈用稌米", 25, weight='700'),
    '<path d="M85,347 L317,280 L469,365 L237,432Z" fill="#d4c599" stroke="#978b65" stroke-width="3"/>',
    *[f'<path d="M{109+i*21},{340-i*6} L{261+i*21},{425-i*6}" stroke="#aaa17a" stroke-width="2"/>' for i in range(10)],
    '<ellipse cx="276" cy="319" rx="57" ry="23" fill="#ede4cd" stroke="#9c8f6e" stroke-width="3"/>',
    *[f'<ellipse cx="{244+(i%5)*14}" cy="{308+(i//5)*8}" rx="5" ry="2" fill="#b6a37a"/>' for i in range(15)],
    text(76, 479, "席与米：具体摆位未载", 22),
    text(604, 170, "璋玉瘗 / 埋藏动作", 25, weight='700'),
    '<path d="M799,206 L850,223 L827,281 L787,267Z" fill="#8da99b" stroke="#557b6a" stroke-width="3"/>',
    line(817, 292, 817, 351, arrow=True),
    '<path d="M616,368 H773 L786,423 H864 L879,368 H1030 V443 H616Z" fill="#c3ae89"/>',
    '<path d="M616,368 H773 L786,423 H864 L879,368 H1030" fill="none" stroke="#877356" stroke-width="3"/>',
    '<path d="M801,391 L842,401 L828,416 L797,408Z" fill="#8da99b"/>',
    text(603, 480, "图示不是完整祭仪流程", 22),
    text(45, 548, "此处未记神庙、围墙、神像、屋顶或人工祭台形制。", 20),
]))

diagrams["yaoguang-cave-space.svg"] = svg("尧光山 · 穴居与冬蛰", "穴居主体为猾褢；穴的天然或人工成因、形状与内部布局均未交代。", ''.join([
    '<path d="M58,474 L166,282 Q260,127 434,260 L591,474Z" fill="#b9bdab" stroke="#7b8a73" stroke-width="3"/>',
    '<path d="M223,474 V348 Q308,222 399,349 V474Z" fill="#505d55"/>',
    text(258, 391, "穴居", 30, '#f3f0e7', weight='700'),
    text(102, 505, "洞形仅为占位示意", 22),
    box(631, 125, 445, 188), text(659, 170, "穴的居住者：猾褢", 25, weight='700'), text(659, 218, "状如人而彘鬣", 24), text(659, 270, "‘状如人’仍是兽类描述", 22),
    box(631, 335, 445, 180), text(659, 381, "冬蛰", 27, weight='700'), text(659, 429, "冬季蛰伏，不补写室内生活", 22), text(659, 476, "音如斫木 ≠ 会伐木造屋", 22),
    line(414, 373, 628, 225, dash=True),
]))

for name, content in diagrams.items():
    (IMAGES / name).write_text(content, encoding="utf-8", newline="\n")


def source_link(card):
    source = next(s for s in DATA["sources"] if s["id"] == card["source"])
    return f'[{source["id"]} · {source["title"]}]({source["url"]})'


method = "正文以 S1 在线转录为主，繁体引文保留其用字；标点作阅读整理，省略处用‘……’明示。解释与资料卡名称用简体，均为本次整理。S2 用于交叉核对和辨认古注；这份资料是有出处的初步整理，不宣称完成底本影印校勘。"
picture_note = "三张异兽图是后世古籍插图的数字化版本，不能称为《山海经》成书时的原始图像。六张生态与空间图为本次绘制的要素示意，图中尺寸、形状、摆位、颜色不超越正文成为历史事实。后世插图与本次示意均单独标注图像性质。"

md = [f'# {DATA["title"]}', f'整理日期：{DATA["date"]}。范围：{DATA["scope"]}',
      f'**范围说明：** {DATA["notice"]}',
      '[打开图文浏览版](南山经图文资料.html) · [结构化资料卡](资料卡.json) · [图片来源与校验清单](图片来源.json)',
      '## 阅读与取材方法', method, picture_note,
      '卡片分为正文引文、释读、可确认要素、古注／异文／边界、模组原创候选。最后一项只供改编讨论，不表示已确认开发内容。‘生态’在此指同山环境、物产、水系和栖居记载的组合，不预设现代生态学意义的食物链。',
      '## 九项总览', '![九项图文总览：三张古籍插图与六张原文要素示意](九项图文总览.png)', '总览为九张配图的浏览器渲染缩略表，供快速浏览；完整细节与图源见各卡片。更新图片后需重新导出这张预览。', '| 类别 | 三项 | 图像性质 |', '| --- | --- | --- |',
      '| 异兽 | 狌狌、鹿蜀、九尾狐 | 后世古籍插图 |',
      '| 生态 | 招摇山、青丘山、南禺山 | 原文要素示意 |',
      '| 建筑与空间线索 | 成山三坛、鹊山祭祀、尧光山穴居 | 形态／仪式／栖居示意；不能据此称为三座建筑 |']

groups = []
for category in ("异兽", "生态", "建筑与空间线索"):
    md.append(f'## {category} · 三项')
    cards_html = []
    for card in [c for c in DATA["cards"] if c["category"] == category]:
        md.extend([f'### {card["name"]}：{card["subtitle"]}',
                   f'定位：**{card["section"]}**。{source_link(card)}；{card["locator"]}。',
                   f'![{card["name"]} — {card["image_kind"]}]({card["image"]})',
                   f'图注：{card["caption"]}' + (f' [图像来源]({card["image_source"]})' if "image_source" in card else ''),
                   '**正文引文**', f'> {card["quote"]}', '**释读**', card["explanation"], '**可确认要素**',
                   '\n'.join(f'- {fact}' for fact in card["facts"]), '**古注、异文与取材边界**',
                   '\n'.join(f'- {note}' for note in card["notes"]), '**模组原创候选（非正文）**', card["adaptation"]])
        e = html.escape
        facts = ''.join(f'<li>{e(f)}</li>' for f in card['facts'])
        notes = ''.join(f'<li>{e(n)}</li>' for n in card['notes'])
        src = next(s for s in DATA['sources'] if s['id'] == card['source'])
        image_link = f' <a href="{e(card["image_source"])}">图像来源 ↗</a>' if 'image_source' in card else ''
        card_class = 'card' if category == '异兽' else 'card diagram'
        cards_html.append(f'''<article id="{card['id']}" class="{card_class}">
<div class="card-head"><span class="kicker">{e(card['section'])}</span><h3>{e(card['name'])}</h3><p class="subtitle">{e(card['subtitle'])}</p></div>
<div class="body"><figure><div class="plate"><a href="{e(card['image'])}" title="打开完整图像"><img src="{e(card['image'])}" alt="{e(card['name'] + '：' + card['image_kind'])}" loading="lazy"/></a></div><figcaption>{e(card['caption'])}{image_link}</figcaption></figure>
<div class="copy"><h4>正文</h4><blockquote>{e(card['quote'])}</blockquote><p>{e(card['explanation'])}</p><h4>可确认要素</h4><ul>{facts}</ul><details open><summary>古注、异文与取材边界</summary><ul>{notes}</ul></details><div class="adaptation"><h4>模组原创候选 · 非正文</h4><p>{e(card['adaptation'])}</p></div><p class="source"><a href="{e(src['url'])}">{e(src['id'])} · 正文查阅 ↗</a><br/>{e(card['locator'])}</p></div></div></article>''')
    groups.append(f'<section id="group-{len(groups)+1}"><div class="section-head"><span>0{len(groups)+1}</span><h2>{html.escape(category)}</h2><p>三项资料</p></div>{"".join(cards_html)}</section>')

md.extend(['## 来源与版本记录', *[f'- **{s["id"]}** [{s["title"]}]({s["url"]})：{s["note"]}' for s in DATA['sources']],
           '## 图片来源与使用说明',
           '三张异兽 SVG 从 Wikimedia Commons 提供的原文件地址保存，未改动图形。文件说明页将来源标为明代《山海经图》及胡文焕，并标注 Public Domain／PD-Art／Public Domain Mark。本站记录中的具体作者年代未在本次独立考证，故不据其数字推定版本出版年。逐图来源页、下载地址、SHA-256 与尺寸见 [图片来源清单](图片来源.json)。',
           '其余六张 SVG 为本项目绘制，不是历史插图或考古测绘，也不是具体建筑的复原。使用和改绘古籍图片时仍应保留图源说明，避免把后世画法说成正文规定的颜色或结构。',
           '## 更新资料',
           '编辑 `资料卡.json` 后运行 `python docs/南山经资料/生成图文.py`，同步生成 Markdown、HTML 和示意图。生成脚本只用 Python 标准库；古籍原图另行保存，不会由脚本重画。'])
(ROOT / '南山经原著图文资料.md').write_text('\n\n'.join(md) + '\n', encoding='utf-8', newline='\n')

sources_html = ''.join(f'<li><a href="{html.escape(s["url"])}">{html.escape(s["id"] + " · " + s["title"])}</a><p>{html.escape(s["note"])}</p></li>' for s in DATA['sources'])
page = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><title>{html.escape(DATA['title'])}</title>
<style>
:root{{--paper:#f4f0e6;--ink:#223b36;--muted:#667468;--accent:#a95b3c;--line:#d7d6c6}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.8 'Microsoft YaHei','PingFang SC',sans-serif}}a{{color:#356c6b;text-underline-offset:4px}}main{{max-width:1280px;margin:auto;padding:44px 32px 72px}}header{{padding:22px 0 34px;border-bottom:2px solid var(--ink)}}.eyebrow,.kicker{{font-size:13px;letter-spacing:.08em;color:var(--muted)}}h1{{font-size:48px;line-height:1.2;letter-spacing:.04em;margin:14px 0 20px;font-family:'Songti SC',SimSun,serif}}header .intro{{max-width:880px}}.date{{font-size:14px;color:var(--muted)}}nav{{display:flex;gap:12px;flex-wrap:wrap;margin-top:24px}}nav a{{padding:8px 20px;border:1px solid var(--line);border-radius:24px;text-decoration:none;background:#fffaf0}}.notice{{border-left:4px solid var(--accent);background:#eae5d5;padding:18px 24px;margin:28px 0}}.notice strong{{display:block}}.method{{max-width:1000px;color:var(--muted);font-size:15px}}.section-head{{display:flex;align-items:baseline;gap:18px;padding:24px 0 10px;margin-top:24px}}.section-head span{{color:var(--accent);font-size:17px}}h2{{font-size:30px;margin:0}}.section-head p{{color:var(--muted);font-size:14px}}.card{{border:1px solid var(--line);background:#fffdf7;margin:0 0 28px;border-radius:12px;overflow:hidden;scroll-margin-top:16px}}.card-head{{padding:26px 30px 18px;border-bottom:1px solid var(--line)}}h3{{font-size:32px;line-height:1.3;margin:6px 0;font-family:'Songti SC',SimSun,serif}}.subtitle{{margin:0;color:var(--muted)}}.body{{display:grid;grid-template-columns:42% 58%}}figure{{margin:0;padding:28px;background:#f0eedf;border-right:1px solid var(--line)}}.plate{{background:#fffdf7;display:flex;align-items:center;justify-content:center;min-height:260px}}img{{display:block;width:100%;max-height:520px;object-fit:contain}}figcaption{{font-size:13px;line-height:1.7;color:var(--muted);margin-top:18px}}.copy{{padding:22px 30px 28px}}h4{{font-size:14px;letter-spacing:.05em;color:var(--accent);margin:14px 0 6px}}blockquote{{margin:10px 0 16px;padding:12px 17px;background:#efefe3;border-left:3px solid #8a9e8a;line-height:1.9;font-family:'Songti SC',SimSun,serif;font-size:19px}}p{{margin:10px 0 14px}}ul{{padding-left:22px;margin:8px 0}}li{{margin:7px 0}}details{{font-size:15px;color:#536558}}summary{{cursor:pointer;font-weight:600;margin:16px 0 6px}}.adaptation{{padding:4px 16px 8px;margin-top:18px;background:#f5ebdb;font-size:15px}}.source{{font-size:13px;color:var(--muted);margin-bottom:0}}footer{{border-top:2px solid var(--ink);padding-top:32px;margin-top:44px;font-size:15px}}footer h2{{font-size:25px}}footer .legal{{color:var(--muted)}}
.plate a{{display:block;width:100%}}.diagram .body{{display:block}}.diagram figure{{border-right:0;border-bottom:1px solid var(--line)}}.diagram img{{max-height:none;max-width:1120px;margin:auto}}.diagram .copy{{max-width:1000px;margin:auto}}
@media(max-width:850px){{main{{padding:24px 16px 48px}}h1{{font-size:36px}}.body{{grid-template-columns:1fr}}figure{{border-right:0;border-bottom:1px solid var(--line)}}.plate{{min-height:0}}img{{max-height:430px}}.copy,.card-head{{padding-left:22px;padding-right:22px}}}}
@media print{{body{{background:white;font-size:11pt}}main{{max-width:none;padding:0}}nav{{display:none}}h1{{font-size:28pt}}.card{{border-radius:0;break-inside:auto}}.body{{grid-template-columns:35% 65%}}img{{max-height:300px}}a{{color:inherit}}.notice{{break-inside:avoid}}}}
</style></head><body><main>
<header><div class="eyebrow">山海经 · 卷一资料选 / 原文、古图与要素示意</div><h1>南山经</h1><p class="intro">从异兽形貌到山川物产，再到祭仪与栖居空间。每一项都保留原文依据、图像性质和取材边界，便于后续模组设计查阅。</p><div class="date">{DATA['date']} · 异兽 3 / 生态 3 / 建筑与空间线索 3</div><nav aria-label="资料分类"><a href="#group-1">异兽</a><a href="#group-2">生态</a><a href="#group-3">建筑与空间线索</a><a href="#sources">来源说明</a><a href="南山经原著图文资料.md">Markdown 文件</a></nav></header>
<aside class="notice"><strong>建筑类的原著边界</strong>{html.escape(DATA['notice'])}</aside>
<div class="method"><p>{html.escape(DATA['scope'])}</p><p>{html.escape(method)}</p><p>{html.escape(picture_note)}</p><p>“生态”在此整理同山物产与空间关系；模组原创候选独立标注，不属于原著记载。</p></div>
{''.join(groups)}
<footer id="sources"><h2>来源与图像记录</h2><ul>{sources_html}</ul><p class="legal">三张异兽图据 Commons 文件说明为明代《山海经图》、胡文焕相关图像，文件页标示 Public Domain / PD-Art。此处保留数字化原文件；未独立考证其具体版刻年代。六张要素图由本项目绘制。</p><p><a href="图片来源.json">逐图来源、下载地址与文件校验</a> · <a href="资料卡.json">结构化资料卡</a> · <a href="#">回到开篇 ↑</a></p></footer>
</main></body></html>'''
(ROOT / '南山经图文资料.html').write_text(page, encoding='utf-8', newline='\n')

original_urls = {
    'shengsheng.svg': 'https://upload.wikimedia.org/wikipedia/commons/3/3e/%E5%8D%97%E5%B1%B1%E7%B6%93-%E7%8B%8C%E7%8B%8C.svg',
    'lushu.svg': 'https://upload.wikimedia.org/wikipedia/commons/e/e3/%E5%8D%97%E5%B1%B1%E7%B6%93-%E9%B9%BF%E8%9C%80.svg',
    'nine-tailed-fox.svg': 'https://upload.wikimedia.org/wikipedia/commons/b/bc/%E5%8D%97%E5%B1%B1%E7%B6%93-%E4%B9%9D%E5%B0%BE%E7%8B%90.svg',
}
manifest = []
for card in DATA['cards']:
    path = ROOT / card['image']
    raw = path.read_bytes()
    xml = ET.fromstring(raw)
    if xml.tag != '{http://www.w3.org/2000/svg}svg':
        raise ValueError(f'无效 SVG：{path}')
    for element in xml.iter():
        if element.tag.rsplit('}', 1)[-1] in ('script', 'foreignObject'):
            raise ValueError(f'不应含有可执行元素：{path}')
        for attr, value in element.attrib.items():
            if attr.rsplit('}', 1)[-1].lower().startswith('on') or (attr.rsplit('}', 1)[-1] == 'href' and value.startswith(('http:', 'https:', '//'))):
                raise ValueError(f'不应依赖外部内容或事件：{path}')
    item = {'file': card['image'], 'card': card['name'], 'kind': card['image_kind'],
            'caption': card['caption'], 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
            'width': xml.get('width'), 'height': xml.get('height'), 'viewBox': xml.get('viewBox')}
    if path.name in original_urls:
        item.update({'source_page': card['image_source'], 'download_url': original_urls[path.name],
                     'downloaded': DATA['date'], 'attribution_as_listed': '明代《山海经图》／胡文焕（据 Commons 文件页）',
                     'digital_uploader_as_listed': 'Walter Grassroot，2011-09-24',
                     'license_as_listed': 'Public Domain / PD-Art / Public Domain Mark', 'modification': '下载后未改动 SVG 文件'})
    else:
        item.update({'creator': '本项目绘制', 'historical_image': False, 'proportion': '无比例尺，非测绘或建筑复原'})
    manifest.append(item)
(ROOT / '图片来源.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
assert len(DATA['cards']) == 9
assert len(manifest) == 9
assert len(diagrams) == 6
assert all(sum(c['category'] == group for c in DATA['cards']) == 3 for group in ('异兽', '生态', '建筑与空间线索'))
print('已生成：9 项资料卡、9 张有效 SVG、Markdown、HTML、图片来源清单。')
