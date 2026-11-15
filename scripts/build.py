#!/usr/bin/env python3
"""Generate the bilingual portfolio using only the Python standard library."""
import html
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
PROFILE = json.loads((ROOT / 'content/profile.json').read_text())
NOTES = json.loads((ROOT / 'content/notes.json').read_text())
ORIGIN = 'https://dengqirui.me'
PAGES = []


def esc(v):
    return html.escape(str(v), quote=True)


def tr(lang, zh, en):
    return en if lang == 'en' else zh


def field(obj, key, lang):
    return obj[f'{key}_{lang}']


def url(lang, page=''):
    return ('/' if lang == 'en' else '/zh/') + (page.strip('/') + '/' if page else '')


def arrow():
    return '<span class="arrow" aria-hidden="true">↗</span>'


def link(href, label, cls='text-link'):
    return f'<a class="{cls}" href="{esc(href)}">{label}{arrow()}</a>'


def tags(project):
    return '<div class="tags">' + ''.join(f'<span>{esc(t)}</span>' for t in project['tags']) + '</div>'


def header(lang, page):
    nav = [('research', '研究', 'Research'), ('projects', '项目', 'Projects'), ('notes', '笔记', 'Notes'), ('about', '关于', 'About')]
    nav_html = ''.join(f'<a href="{url(lang, slug)}"' + (' aria-current="page"' if page.split('/')[0] == slug else '') + f'>{tr(lang, zh, en)}</a>' for slug, zh, en in nav)
    other = 'en' if lang == 'zh' else 'zh'
    return f'''<a class="skip" href="#main">{tr(lang, '跳至正文', 'Skip to content')}</a>
<header class="site-header"><div class="wrap header-inner">
<a class="brand" href="{url(lang)}" aria-label="{tr(lang, 'DQR-Happy · 首页', 'DQR-Happy · Home')}"><span class="brand-mark" aria-hidden="true">dh</span><span class="brand-name">DQR-Happy</span></a>
<nav class="main-nav" id="navigation" aria-label="{tr(lang, '主导航', 'Main navigation')}">{nav_html}</nav>
<div class="header-tools"><a class="lang-link" lang="{other}" hreflang="{'en' if other == 'en' else 'zh-CN'}" href="{url(other, page)}" aria-label="{tr(lang, 'Read this page in English', '切换到中文页面')}">{tr(lang, 'EN', '中文')}</a>
<button class="theme-toggle js-only" aria-label="{tr(lang, '切换主题', 'Switch theme')}" aria-pressed="false"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.3A8.5 8.5 0 0 1 9.7 4a8.5 8.5 0 1 0 10.3 10.3Z"/></svg></button>
<button class="menu-toggle js-only" aria-controls="navigation" aria-expanded="false">{tr(lang, '菜单', 'Menu')}</button></div>
</div></header>'''


def footer(lang):
    return f'''<footer class="site-footer"><div class="wrap"><div class="footer-top"><a href="{url(lang)}"><strong>DQR-Happy.</strong></a><div class="footer-links"><a href="{PROFILE['github']}">GitHub ↗</a><a href="mailto:{PROFILE['email']}">{tr(lang, '邮件联系', 'Email')} ↗</a><a href="{url(lang, 'about')}">{tr(lang, '个人简介', 'Profile')} ↗</a></div></div>
<div class="footer-bottom"><span>© 2026 {PROFILE['name']}</span><span>{tr(lang, '以公开实现与可复现证据记录工作。', 'Work documented through public implementations and reproducible evidence.')} · {PROFILE['updated']}</span></div></div></footer>'''


def document(lang, page, title, description, body):
    path = url(lang, page)
    alternate = url('en' if lang == 'zh' else 'zh', page)
    title = f'{title} — DQR-Happy' if page else 'DQR-Happy — GPU Systems & AI Infrastructure'
    schema = {'@context': 'https://schema.org', '@type': 'Person', 'name': 'DQR-Happy', 'url': ORIGIN, 'sameAs': [PROFILE['github']], 'email': PROFILE['email'], 'knowsAbout': ['GPU profiling', 'AI infrastructure', 'LLM inference', 'Heterogeneous computing']}
    return f'''<!doctype html>
<html lang="{'en' if lang == 'en' else 'zh-CN'}" class="no-js"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light dark">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}"><meta name="author" content="DQR-Happy"><meta name="theme-color" content="#f6f5f8">
<link rel="canonical" href="{ORIGIN}{path}"><link rel="alternate" hreflang="{'zh-CN' if lang == 'en' else 'en'}" href="{ORIGIN}{alternate}"><link rel="alternate" hreflang="{'en' if lang == 'en' else 'zh-CN'}" href="{ORIGIN}{path}"><link rel="alternate" hreflang="x-default" href="{ORIGIN}{url('en', page)}">
<meta property="og:type" content="website"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{ORIGIN}{path}"><meta property="og:site_name" content="DQR-Happy"><meta name="twitter:card" content="summary">
<link rel="icon" href="/assets/favicon.svg?v=slate-lilac-1" type="image/svg+xml"><link rel="stylesheet" href="/assets/site.css?v=slate-lilac-1"><script src="/assets/site.js?v=slate-lilac-1" defer></script>
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script></head><body>{header(lang, page)}<main id="main" class="wrap">{body}</main>{footer(lang)}</body></html>'''


def heading(lang, eyebrow, title, lead):
    return f'<div class="page-heading"><div class="eyebrow">{eyebrow}</div><h1>{title}</h1><p class="lead">{lead}</p></div>'


def diagram(lang):
    return f'''<div class="hero-art"><figure><div class="art-title">EXECUTION CONTEXT → LOSSLESS REPRESENTATION</div>
<svg viewBox="0 0 440 348" role="img" aria-labelledby="diagram-title diagram-desc"><title id="diagram-title">{tr(lang, '执行参考编码机制示意', 'Execution-reference encoding schematic')}</title><desc id="diagram-desc">{tr(lang, '原始记录通过 SM 或 CTA 参考和精确残差编码，经过范围检查，必要时 raw 回退，并可以精确恢复。', 'Original records use SM or CTA references and exact residuals, with range checks, raw fallback when required, and exact recovery.')}</desc>
<defs><pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" class="diagram-line" stroke-width=".5"/></pattern></defs>
<rect x="20" y="20" width="400" height="300" fill="url(#grid)"/>
<g fill="none" class="diagram-line"><path d="M20 12v16M12 20h16M420 12v16M412 20h16M20 312v16M12 320h16M420 312v16M412 320h16"/><path d="M40 75H400M40 285H400"/></g>
<text x="42" y="57" class="diagram-small">01 / RAW RECORDS</text><text x="286" y="57" class="diagram-small">WARP × SM / CTA</text>
<g class="diagram-paper diagram-ink" stroke-width="1"><rect x="42" y="92" width="118" height="40"/><rect x="160" y="92" width="116" height="40"/><rect x="276" y="92" width="122" height="40"/></g>
<text x="71" y="117" class="diagram-text">start</text><text x="190" y="117" class="diagram-text">elapsed</text><text x="310" y="117" class="diagram-text">SM ID</text>
<path d="M220 133v29M216 158l4 5 4-5" fill="none" class="diagram-accent" stroke-width="1.5"/>
<rect x="42" y="174" width="118" height="73" class="diagram-fill diagram-accent"/>
<text x="59" y="201" class="diagram-small">REFERENCE</text><text x="59" y="226" class="diagram-text">SM / CTA</text>
<rect x="175" y="174" width="223" height="73" class="diagram-residual"/>
<text x="193" y="201" class="diagram-small">EXACT RESIDUALS</text><text x="193" y="226" class="diagram-text">δ + preserved fields</text>
<path d="M101 248v17h185v-17" class="diagram-accent" fill="none"/>
<text x="42" y="309" class="diagram-small">CHECK → ENCODE / RAW FALLBACK</text>
<path d="M360 247v40" fill="none" class="diagram-accent"/><circle cx="360" cy="292" r="14" class="diagram-fill diagram-accent"/><path d="m354 292 4 4 8-9" class="diagram-accent" stroke-width="1.5" fill="none"/>
</svg><figcaption>{tr(lang, 'ERETrace · 编码结构示意，非实测时间线', 'ERETrace · encoding structure, not a measured timeline')}</figcaption></figure></div>'''


def note_card(note, lang):
    return f'''<article class="note-card"><div class="note-meta"><span>{note['category']}</span><span>{note['date']}</span></div><h3><a href="{url(lang, 'notes/' + note['slug'])}">{esc(field(note, 'title', lang))}</a></h3><p>{esc(field(note, 'dek', lang))}</p>{link(url(lang, 'notes/' + note['slug']), tr(lang, '阅读笔记', 'Read note'))}</article>'''


def contact(lang):
    return f'''<section class="contact-band" aria-labelledby="contact-title"><div><h2 id="contact-title">{tr(lang, '从一个具体问题开始交流。', 'Start with a concrete problem.')}</h2><p>{tr(lang, '欢迎交流 GPU 系统、推理优化与相关研究。', 'Open to conversations on GPU systems, inference optimization, and research.')}</p></div>{link('mailto:' + PROFILE['email'], PROFILE['email'])}</section>'''


def home(lang):
    p = PROFILE['paper']
    rows = ''
    for i, project in enumerate(PROFILE['projects'][1:], 2):
        rows += f'''<a class="project-row" href="{url(lang, 'projects')}#{'hqsb' if i == 2 else 'activations'}"><span class="number">0{i}</span><div><h3>{project['name']}</h3><span class="status">{field(project, 'state', lang)}</span></div><p>{field(project, 'desc', lang)}</p>{arrow()}</a>'''
    principles = [
        ('先理解机制，再优化实现', 'Understand the mechanism first', '从硬件、执行路径和数据布局出发，把性能现象落实到可解释的系统行为。', 'Connect hardware, execution paths, and data layouts to explain the behavior behind a performance result.'),
        ('同时关心速度、语义与边界', 'Keep speed and semantics together', '优化需要保留任务语义。捕获范围、数值精度、回退路径与计时终点，都是方法的一部分。', 'Optimization must preserve task semantics. Capture scope, precision, fallback paths, and timing endpoints are part of the method.'),
        ('用可复现证据连接研究与工程', 'Connect research to reproducible engineering', '将实现、配置、运行记录和比较结果关联起来，让结论可以检查，让系统可以继续迭代。', 'Link implementations, configurations, run records, and comparisons so claims can be inspected and systems can evolve.')]
    principles_html = ''.join(f'<div class="principle"><b>0{i}</b><div><h3>{tr(lang, zh, en)}</h3><p>{tr(lang, zdesc, edesc)}</p></div></div>' for i, (zh, en, zdesc, edesc) in enumerate(principles, 1))
    return f'''<section class="hero" aria-labelledby="hero-name"><div><div class="eyebrow">GPU systems · AI infrastructure</div><h1 id="hero-name">DQR-Happy<span aria-hidden="true">.</span></h1><p class="intro">{tr(lang, '研究 GPU 可观测性与高效推理，连接微电子背景与计算机系统实践。', 'Exploring GPU observability and efficient inference, from a foundation in microelectronics to computer systems research.')}</p><p class="affiliation">{tr(lang, '桂林电子科技大学 · 计算机科学与技术 · 学术型硕士在读', 'M.Sc. student in Computer Science and Technology<br>Guilin University of Electronic Technology')}</p><div class="actions">{link(url(lang, 'research'), tr(lang, '了解我的研究', 'Explore my research'), 'button')}{link(PROFILE['github'], 'GitHub')}</div></div>{diagram(lang)}</section>
<div class="hero-bottom"><span class="place">{tr(lang, '微电子 → 计算机系统 → AI 基础设施', 'Microelectronics → Systems → AI infrastructure')}</span><div class="interests"><span><i class="dot"></i>GPU observability</span><span>LLM inference</span><span>Heterogeneous computing</span></div></div>
<section class="section" aria-labelledby="research-title"><div class="section-head"><div><div class="eyebrow">Selected research</div><h2 id="research-title">{tr(lang, '研究，为系统留下更清晰的证据。', 'Research that makes systems more observable.')}</h2></div>{link(url(lang, 'research'), tr(lang, '研究详情', 'Research details'))}</div>
<article class="featured"><div><div class="eyebrow">ISPA 2026 · {field(p, 'status', lang)}</div><h3>ERETrace</h3><div class="paper-title">{p['title']}</div><p style="margin-top:20px">{tr(lang, '执行参考编码与面向恢复的采集设计，在完整推理期间保留细粒度记录，降低追踪的时间与空间成本。', 'Execution-reference encoding and recovery-aware collection preserve fine-grained records while reducing tracing costs during complete inference.')}</p><div class="actions">{link(p['site'], tr(lang, '项目主页', 'Project site'))}{link(p['code'], tr(lang, '代码与复现', 'Code & reproduction'))}</div></div>
<div class="featured-details"><div class="result-pair"><div><strong>11–24%</strong><span>{tr(lang, '完整采集请求延迟降低', 'Lower complete-request latency')}</span></div><div><strong>31–33%</strong><span>{tr(lang, '无损 trace 文件缩小', 'Smaller lossless trace files')}</span></div></div><p class="feature-note">{tr(lang, '相对同配置的字段感知 nvCOMP Cascaded 采集器；RTX 3090，三个模型，B1，256 输入 / 64 输出 token。具体数据与口径见研究详情。', 'Versus the matched field-aware nvCOMP Cascaded collector; RTX 3090, three models, B1, 256 input / 64 output tokens. Data and scope are documented in Research.')}</p><div class="mini-flow" aria-label="{tr(lang, '记录、编码、采集流程', 'Record, encode, collect pipeline')}"><span>Record</span><b>→</b><span>Reference</span><b>→</b><span>Collect</span></div></div></article></section>
<section class="section" style="padding-top:0" aria-labelledby="projects-title"><div class="section-head"><div><div class="eyebrow">Engineering & resources</div><h2 id="projects-title">{tr(lang, '把想法做成能够继续生长的系统。', 'Ideas carried into working systems.')}</h2></div>{link(url(lang, 'projects'), tr(lang, '项目索引', 'All projects'))}</div><div class="project-list">{rows}</div></section>
<section class="two-cols approach" aria-labelledby="approach-title"><div class="section-head"><div class="eyebrow">How I work</div><h2 id="approach-title">{tr(lang, '从现象，到机制，<br>再回到真实工作流。', 'From observations to mechanisms,<br>back to real workflows.')}</h2><p>{tr(lang, '硬件背景让我关注执行细节；系统研究让我追问，这些细节如何影响真实任务。', 'A hardware background draws me to execution details. Systems research asks how those details change a real task.')}</p>{link(url(lang, 'about'), tr(lang, '背景与研究兴趣', 'Background & interests'))}</div><div>{principles_html}</div></section>
<section class="section" aria-labelledby="notes-title"><div class="section-head"><div><div class="eyebrow">Field notes</div><h2 id="notes-title">{tr(lang, '关于测量、追踪与推理的技术笔记。', 'Notes on measurement, tracing, and inference.')}</h2></div>{link(url(lang, 'notes'), tr(lang, '全部笔记', 'All notes'))}</div><div class="notes-grid">{''.join(note_card(n, lang) for n in NOTES)}</div></section>{contact(lang)}'''


def research(lang):
    p = PROFILE['paper']
    rows = [('Qwen3-8B', '703.67', '624.70', '1.941', '1.303'), ('Llama3.2-1B', '228.62', '174.00', '0.643', '0.441'), ('Gemma3-4B', '558.40', '485.81', '1.598', '1.081')]
    table = ''.join(f'<tr><td>{r[0]}</td><td>{r[1]}</td><td class="ours">{r[2]}</td><td>{r[3]}</td><td class="ours">{r[4]}</td></tr>' for r in rows)
    mechanisms = [
        ('01 / Execution references', '使用 SM / CTA 参考关系减少重复表示，在范围条件满足时使用窄字段，并保留精确恢复所需的信息。', 'Use SM / CTA references to reduce redundant representation, with narrow fields under checked range conditions and the information needed for exact recovery.'),
        ('02 / Checked fallback', '不满足编码接受条件时保留 raw 记录。字段值、精度、顺序与执行归属保持可恢复，独立正确性运行检查无损性。', 'Retain raw records when encoding acceptance conditions fail. Field values, precision, order, and execution attribution remain recoverable; dedicated correctness runs verify losslessness.'),
        ('03 / Bounded collection', '将参考编码放入有界异步采集流水线，协调编码、D2H 与文件输出，以完整请求成本评价系统收益。', 'Integrate reference encoding with a bounded asynchronous collection pipeline, coordinating encoding, D2H transfers, and output to evaluate the complete request cost.')]
    mech = ''.join(f'<article><h3>{name}</h3><p>{tr(lang, zh, en)}</p></article>' for name, zh, en in mechanisms)

    return heading(lang, 'Research / 01', tr(lang, '研究与论文', 'Research & publications'), tr(lang, '关注 GPU 的细粒度可观测性，以及采集机制与真实推理工作流之间的关系。', 'Fine-grained GPU observability, with a focus on how collection mechanisms interact with real inference workflows.')) + f'''
<section class="publication content-section" aria-labelledby="paper-title"><div class="venue">ISPA 2026<span class="badge">{field(p, 'status', lang)}</span></div><div><h2 id="paper-title">{p['title']}</h2><p class="authors">School of Computer Science and Information Security, Guilin University of Electronic Technology</p><p class="abstract">{tr(lang, '细粒度 GPU 追踪会产生大量记录，采集开销可能显著改变被观测任务。ERETrace 将执行参考编码与面向恢复的采集设计结合，在保留完整记录语义的条件下，降低完整推理请求的采集延迟与输出体积。', 'Fine-grained GPU tracing produces large volumes of records, and collection overhead can substantially perturb the workload being observed. ERETrace combines execution-reference encoding with recovery-aware collection to reduce complete-request collection latency and output size while preserving record semantics.')}</p><div class="actions">{link(p['site'], tr(lang, '项目主页', 'Project site'), 'button')}{link(p['code'], 'GitHub')}{link(p['release'], 'v1.0.0')}</div></div></section>
<section class="content-section" aria-labelledby="mechanisms-title"><h2 id="mechanisms-title" class="section-title">{tr(lang, '方法的三个组成部分', 'Three parts of the method')}</h2><div class="research-columns">{mech}</div></section>
<section class="content-section" aria-labelledby="results-title"><h2 id="results-title" class="section-title">{tr(lang, '公开评估中的一个切面', 'A view into the public evaluation')}</h2><p>{tr(lang, '下表摘自论文公开结果，比较字段感知 nvCOMP Cascaded 采集器与 ERETrace。两者使用一致的任务与捕获范围。', 'The table below reproduces public paper results comparing the field-aware nvCOMP Cascaded collector with ERETrace under the same task and capture scope.')}</p>
<div class="table-wrap"><table><caption>{tr(lang, '完整推理 + 完整 trace 采集', 'Complete inference + complete trace collection')}</caption><thead><tr><th scope="col">{tr(lang, '模型', 'Model')}</th><th scope="col">nvCOMP<br>{tr(lang, '总时间 (ms)', 'Total (ms)')}</th><th scope="col">ERETrace<br>{tr(lang, '总时间 (ms)', 'Total (ms)')}</th><th scope="col">nvCOMP<br>Trace (GB)</th><th scope="col">ERETrace<br>Trace (GB)</th></tr></thead><tbody>{table}</tbody></table></div>
<p class="table-note">{tr(lang, 'NVIDIA RTX 3090 24GB；batch = 1；输入 256、输出 64 token；7 个独立进程轮次，每轮 3 次请求，展示均值。总时间从推理请求开始，到完整 trace 文件关闭；不含离线解码 / 分析。GB 为十进制单位。此处为该配置的结果，不代表所有模型、硬件或捕获范围。', 'NVIDIA RTX 3090 24GB; batch = 1; 256 input and 64 output tokens; means from 7 independent process rounds with 3 requests per round. Total spans request start through complete trace-file close; offline decoding / analysis is excluded. GB is decimal. These results describe this configuration, rather than every model, device, or capture scope.')}</p>{link('https://github.com/DQR-Happy/ERETrace/blob/main/results/paper/main-results.json', tr(lang, '查看完整数据与其他对照', 'Full data and additional comparisons'))}</section>
<section class="content-section"><h2 class="section-title">{tr(lang, '实现与复现', 'Implementation & reproduction')}</h2><div class="research-columns"><article><h3>{tr(lang, '运行环境', 'Execution environment')}</h3><p>{tr(lang, 'Linux / CUDA，基于 Neutrino 可编程探针。公开制品包含构建说明、补丁、工作负载入口与配置。', 'Linux / CUDA, built on Neutrino programmable probing. The public artifact includes build instructions, patches, workload entry points, and configurations.')}</p></article><article><h3>{tr(lang, '记录语义', 'Record semantics')}</h3><p>{tr(lang, '默认细粒度记录包含每个 warp 的 start、elapsed 与 SM ID，以及执行归属信息。数据应能逐条精确恢复。', 'Default fine-grained records include per-warp start, elapsed, and SM ID, with execution attribution. Records must be exactly recoverable.')}</p></article><article><h3>{tr(lang, '工程边界', 'Engineering scope')}</h3><p>{tr(lang, '主评估、NVBit / XTrace 适配和容量原型分别有各自配置与支持范围，具体条件见制品文档。', 'The main evaluation, NVBit / XTrace integrations, and capacity prototype have separate configurations and support scopes, documented in the artifact.')}</p></article></div><div class="callout"><p>{tr(lang, 'GPU 追踪的收益需要同时看语义、时间与空间。更小的文件不等于更快的 kernel；采集器的性能也不等于模型本身的原生推理性能。', 'Tracing benefits depend on semantics, time, and space together. Smaller files do not imply faster kernels, and collector performance is distinct from native model inference performance.')}</p></div></section>
{contact(lang)}'''


def projects(lang):
    filters = [('all', '全部', 'All'), ('systems', 'GPU 系统', 'GPU systems'), ('inference', '推理工程', 'Inference'), ('resources', '资料', 'Resources')]
    buttons = ''.join(f'<button class="filter" data-filter="{value}" aria-pressed="{str(value == "all").lower()}">{tr(lang, zh, en)}</button>' for value, zh, en in filters)
    items = ''
    for project, ident in zip(PROFILE['projects'], ['eretrace', 'hqsb', 'activations']):
        items += f'''<article id="{ident}" class="project-detail" data-category="{project['category']}"><div><div class="eyebrow">{project['kind']}</div><h2>{project['name']}</h2><span class="state">{field(project, 'state', lang)}</span>{tags(project)}</div><div><h3>{field(project, 'title', lang)}</h3><p>{field(project, 'desc', lang)}</p><ul>{''.join('<li>' + esc(item) + '</li>' for item in field(project, 'items', lang))}</ul><div class="actions">{link(project['url'], tr(lang, '查看项目', 'Explore project'))}{link(project['code'], tr(lang, '源码仓库', 'Source repository')) if project['url'] != project['code'] else ''}</div></div></article>'''
    return heading(lang, 'Projects / Engineering', tr(lang, '项目与开源', 'Projects & open source'), tr(lang, '一组围绕 GPU 追踪、推理优化和技术学习的公开工作。项目状态与实际支持范围以各仓库为准。', 'Public work in GPU tracing, inference optimization, and technical learning. Each repository documents its current status and supported scope.')) + f'''
<div class="filter-bar js-only"><div class="filters" role="group" aria-label="{tr(lang, '项目类别', 'Project categories')}">{buttons}</div><label class="search-label" for="project-search">{tr(lang, '搜索项目', 'Search projects')}<input id="project-search" type="search" autocomplete="off" placeholder="{tr(lang, '名称、技术或关键词', 'Name, technology, keyword')}"></label></div><p id="filter-status" class="filter-status js-only" role="status"></p>
<div>{items}</div><div id="empty-projects" class="empty" hidden><p>{tr(lang, '没有匹配的项目。试试其他关键词或类别。', 'No matching projects. Try another keyword or category.')}</p><button id="clear-filters" class="copy-button">{tr(lang, '清除筛选', 'Clear filters')}</button></div>
{contact(lang)}'''


def notes_index(lang):
    return heading(lang, 'Field notes / Writing', tr(lang, '技术笔记', 'Field notes'), tr(lang, '将研究与工程中反复遇到的问题写清楚：如何测量、如何观测，以及如何让结论跟得上证据。', 'Working notes on recurring research and engineering questions: how to measure, what to observe, and how to keep claims connected to evidence.')) + f'<section class="content-section"><div class="notes-grid">{"".join(note_card(n, lang) for n in NOTES)}</div></section><p class="notice content-section">{tr(lang, "本站笔记为技术解释与方法总结；实验数据以所链接项目中的公开记录为准。", "These notes explain techniques and methodology. Experimental data are defined by the public records in the linked projects.")}</p>{contact(lang)}'


def markdown_sections(path):
    """Render the deliberately small Markdown subset used by authored notes."""
    lines = path.read_text(encoding='utf-8').splitlines()
    sections, current, paragraph = [], None, []
    in_code, code = False, []

    def inline(text):
        parts = re.split(r'(`[^`]+`|\[[^\]]+\]\(https://[^\s)]+\))', text)
        rendered = []
        for part in parts:
            if part.startswith('`') and part.endswith('`'):
                rendered.append('<code>' + esc(part[1:-1]) + '</code>')
            elif re.fullmatch(r'\[[^\]]+\]\(https://[^\s)]+\)', part):
                label, href = part[1:].split('](', 1)
                rendered.append('<a href="' + esc(href[:-1]) + '">' + esc(label) + '</a>')
            else:
                rendered.append(esc(part))
        return ''.join(rendered)

    def flush():
        if paragraph:
            if current is None:
                raise ValueError('Markdown content must begin with a level-two heading')
            current['body'].append('<p>' + inline(' '.join(paragraph)) + '</p>')
            paragraph.clear()

    for line in lines:
        if line.startswith('```'):
            if in_code:
                current['body'].append('<pre><code>' + esc('\n'.join(code)) + '</code></pre>')
                code.clear()
                in_code = False
            else:
                flush()
                in_code = True
        elif in_code:
            code.append(line)
        elif line.startswith('## '):
            flush()
            current = {'heading': line[3:].strip(), 'body': []}
            sections.append(current)
        elif not line.strip():
            flush()
        else:
            paragraph.append(line.strip())
    if in_code:
        raise ValueError('Unclosed Markdown code fence')
    flush()
    return sections


def note_page(note, lang):
    if lang == 'en' and 'markdown_en' in note:
        entries = markdown_sections(ROOT / note['markdown_en'])
    else:
        entries = [{'heading': field(s, 'heading', lang), 'body': ['<p>' + esc(field(s, 'body', lang)) + '</p>']} for s in note['sections']]
    sections = ''.join(f'<section aria-labelledby="s{i}"><h2 id="s{i}">{esc(s["heading"])}</h2>{"".join(s["body"])}</section>' for i, s in enumerate(entries, 1))
    toc = ''.join(f'<li><a href="#s{i}">{esc(s["heading"])}</a></li>' for i, s in enumerate(entries, 1))
    if lang == 'zh' and 'markdown_en' in note:
        sections += '<p><a href="' + url('en', 'notes/' + note['slug']) + '">Read the complete revised article in English →</a></p>'
    next_note = NOTES[(NOTES.index(note) + 1) % len(NOTES)]
    return f'''<div class="page-heading article-heading"><a class="back-link" href="{url(lang, 'notes')}">← {tr(lang, '全部笔记', 'All notes')}</a><div class="eyebrow">{note['category']}</div><h1>{esc(field(note, 'title', lang))}</h1><p class="lead">{esc(field(note, 'dek', lang))}</p><div class="note-meta"><span>DQR-Happy</span><time datetime="{note['date']}">{note['date']}</time><span>{note['minutes']} {tr(lang, '分钟阅读', 'min read')}</span></div></div>
<div class="article-layout"><nav class="article-toc" aria-label="{tr(lang, '本文目录', 'On this page')}"><strong>{tr(lang, '本文目录', 'On this page')}</strong><ol>{toc}</ol></nav><article class="prose">{sections}<div class="article-source">{tr(lang, '相关项目与原始说明', 'Related project and documentation')}<br>{link(note['source'], field(note, 'source_label', lang))}</div><div class="article-nav">{link(url(lang, 'notes'), tr(lang, '返回笔记索引', 'Back to notes'))}{link(url(lang, 'notes/' + next_note['slug']), tr(lang, '下一篇', 'Next note'))}</div></article></div>'''


def about(lang):
    return heading(lang, 'About / Background', tr(lang, '关于我', 'About me'), tr(lang, '从微电子到计算机系统，把对底层机制的兴趣延伸到 GPU 可观测性与 AI 推理工程。', 'From microelectronics to computer systems, following an interest in low-level mechanisms into GPU observability and AI inference engineering.')) + f'''
<section class="about-layout"><div class="bio-copy"><p>{tr(lang, '你好，我是 DQR-Happy，目前在桂林电子科技大学攻读计算机科学与技术学术型硕士。本科就读于湖南大学，学习背景为微电子与集成电路方向。', 'I am DQR-Happy, an M.Sc. student in Computer Science and Technology at Guilin University of Electronic Technology. My undergraduate background at Hunan University is in microelectronics and integrated circuits.')}</p><p>{tr(lang, '我关注 GPU 追踪与性能观测，也在做大模型推理系统的工程实践。感兴趣的问题通常发生在软硬件交界：执行行为如何被可靠观测，采集成本如何影响完整工作流，算子和运行时的改动如何转化为真实任务中的收益。', 'My work centers on GPU tracing and performance observation, alongside engineering practice in LLM inference systems. I am interested in questions at the hardware–software boundary: how to observe execution reliably, how collection costs affect complete workflows, and how kernel or runtime changes translate into real-task benefits.')}</p><p>{tr(lang, '我希望把研究方法和工程实现放在一起：明确问题、理解机制、实现系统，再用可复现的实验检查它究竟解决了什么。', 'I aim to keep research methods close to implementation: define the problem, understand the mechanism, build the system, and use reproducible experiments to see what it actually solves.')}</p></div>
<aside class="profile-card"><h2>DQR-Happy</h2><dl><dt>{tr(lang, '研究领域', 'Focus')}</dt><dd>GPU observability · LLM inference · AI infrastructure</dd><dt>{tr(lang, '学校', 'Affiliation')}</dt><dd>{tr(lang, '桂林电子科技大学', 'Guilin University of Electronic Technology')}</dd><dt>{tr(lang, '邮箱', 'Email')}</dt><dd><a href="mailto:{PROFILE['email']}">{PROFILE['email']}</a></dd><dt>GitHub</dt><dd><a href="{PROFILE['github']}">DQR-Happy ↗</a></dd></dl><button class="copy-button print-button js-only" data-print>{tr(lang, '打印 / 保存此页为 PDF', 'Print / save this profile as PDF')}</button></aside></section>
<section class="content-section"><h2 class="section-title">{tr(lang, '教育背景', 'Education')}</h2><div class="education"><article><span class="degree">{tr(lang, '学术型硕士 · 在读', 'M.Sc. student')}</span><h3>{tr(lang, '桂林电子科技大学', 'Guilin University of Electronic Technology')}</h3><p>{tr(lang, '计算机科学与技术', 'Computer Science and Technology')}</p></article><article><span class="degree">{tr(lang, '本科背景', 'Undergraduate background')}</span><h3>{tr(lang, '湖南大学', 'Hunan University')}</h3><p>{tr(lang, '微电子与集成电路方向', 'Microelectronics and integrated circuits')}</p></article></div></section>
<section class="content-section"><h2 class="section-title">{tr(lang, '当前关注的技术问题', 'Current technical interests')}</h2><div class="capabilities"><article><h3>GPU observability</h3><p>{tr(lang, '细粒度探针、执行参考编码、完整 trace 语义、异步回传与采集开销。', 'Fine-grained probes, execution-reference encoding, complete trace semantics, asynchronous transfers, and collection overhead.')}</p></article><article><h3>Inference systems</h3><p>{tr(lang, 'CUDA / Triton 算子、量化执行、KV cache、运行时、服务与可比较的模型评测。', 'CUDA / Triton kernels, quantized execution, KV caches, runtimes, serving, and comparable model evaluation.')}</p></article><article><h3>Experimental engineering</h3><p>{tr(lang, '正确性与性能分开验证，配置与实际执行关联，以日志、数据和机制对照支撑结论。', 'Separate correctness and performance validation, link configurations to execution, and support conclusions with logs, data, and mechanism comparisons.')}</p></article></div></section>{contact(lang)}'''


def write(lang, page, title, description, body):
    target = ROOT / url(lang, page).lstrip('/') / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(document(lang, page, title, description, body), encoding='utf-8')
    PAGES.append(url(lang, page))
    if lang == 'en':
        # Keep previously published /en/ links working, including query and fragment.
        destination = url('en', page)
        alias = ROOT / 'en' / page / 'index.html'
        alias.parent.mkdir(parents=True, exist_ok=True)
        moved = heading('en', 'Redirect', 'This page has moved.', 'Continue to the English page at its new address.')
        redirect = document('en', page, title, description, moved + '<div class="content-section">' + link(destination, 'Continue', 'button') + '</div>')
        refresh = f'<meta http-equiv="refresh" content="0;url={esc(destination)}"><meta name="robots" content="noindex">'
        script = '<script>location.replace(' + json.dumps(destination) + '+location.search+location.hash);</script>'
        alias.write_text(redirect.replace('</head>', refresh + script + '</head>'), encoding='utf-8')


def main():
    for lang in ('zh', 'en'):
        write(lang, '', '', tr(lang, 'DQR-Happy的个人主页。桂林电子科技大学计算机科学与技术硕士在读，关注 GPU 可观测性、LLM 推理与 AI 基础设施。', 'DQR-Happy: M.Sc. student at Guilin University of Electronic Technology, working on GPU observability, LLM inference, and AI infrastructure.'), home(lang))
        for page, zh, en, render in [('research', '研究与论文', 'Research & publications', research), ('projects', '项目与开源', 'Projects & open source', projects), ('notes', '技术笔记', 'Field notes', notes_index), ('about', '关于我', 'About me', about)]:
            write(lang, page, tr(lang, zh, en), tr(lang, zh, en) + ' · DQR-Happy', render(lang))
        for note in NOTES:
            write(lang, 'notes/' + note['slug'], field(note, 'title', lang), field(note, 'dek', lang), note_page(note, lang))
    missing = heading('en', '404 / Not found', 'This page could not be found.', 'Return to the homepage or explore the public projects.')
    not_found = document('en', '', 'Page not found', 'Page not found', missing + '<div class="content-section">' + link('/', 'Back home', 'button') + '</div>')
    not_found = not_found.replace('<title>DQR-Happy — GPU Systems &amp; AI Infrastructure</title>', '<title>404 — DQR-Happy</title>')
    not_found = not_found.replace('<meta name="author"', '<meta name="robots" content="noindex"><meta name="author"')
    (ROOT / '404.html').write_text(not_found, encoding='utf-8')
    entries = ''.join(f'<url><loc>{xml_escape(ORIGIN + path)}</loc><lastmod>{PROFILE["updated"]}</lastmod></url>' for path in PAGES)
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + entries + '</urlset>\n')
    (ROOT / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://dengqirui.me/sitemap.xml\n')
    (ROOT / '.nojekyll').touch()
    print(f'Built {len(PAGES)} bilingual pages + 404; CNAME unchanged.')


if __name__ == '__main__':
    main()
