#!/usr/bin/env python3
"""Build the approved S4T32 pages from data/coupons.json; no network or private media."""
from pathlib import Path
from html import escape
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://codewafra.com/'
PATH = '/'
DATA = json.loads((ROOT / 'data/coupons.json').read_text(encoding='utf-8'))
LISTING = next(item for item in DATA['coupons'] if item['code'] == DATA['primaryCode'] and item['published'])
CODE = escape(LISTING['code'])
REVIEWED = DATA['lastReviewed']
PAGE_UPDATED = '2026-11-16'
DESTINATION = escape(LISTING['destination'], quote=True)
DATE_EVIDENCE = LISTING.get('dateEvidence', {})


def link(route, text, classes='text-link'):
    return f'<a class="{classes}" href="{PATH}{route}">{text}</a>'


def schema_script(value):
    return '<script type="application/ld+json">' + json.dumps(value, ensure_ascii=False).replace('<', '\\u003c') + '</script>'


def conditions(lang):
    ar = lang == 'ar'
    headings = ['القسيمة التي ظهرت', 'قيمة الطلب', 'سقف الخصم', 'الأهلية'] if ar else ['Observed coupon', 'Order value', 'Discount cap', 'Eligibility']
    rows = []
    for coupon in LISTING['observedCoupons']:
        p, minimum, cap = coupon['discountPercent'], coupon['minimumSpend'], coupon['maximumDiscount']
        cells = [f'{p}% عند استخدام القسيمة المؤهلة', f'أكثر من {minimum} ريالًا', f'{cap} ريالًا', 'مستخدم جديد فقط · منتجات مختارة'] if ar else [f'{p}% with the eligible coupon', f'More than SAR {minimum}', f'SAR {cap}', 'New users only · Selected products']
        rows.append('<tr>' + ''.join(f'<td>{escape(cell)}</td>' for cell in cells) + '</tr>')
    caption = 'قسائم ظهرت في فيديو صاحب الموقع، وليست عروضًا مؤكدة الآن' if ar else 'Coupons seen in the owner’s video, not confirmed current offers'
    expiry = 'ظهرت عبارة «تنتهي في 1 يوم» وقت التصوير. لا نعرف تاريخ انتهاء مطلقًا، ولا نؤكد توفر هذه القسائم الآن.' if ar else 'The recording showed “expires in 1 day”. No absolute expiry date is known, and these coupons are not confirmed available now.'
    return f'''<div class="terms-wrap"><table class="terms-table"><caption>{caption}</caption><thead><tr>{''.join(f'<th scope="col">{heading}</th>' for heading in headings)}</tr></thead><tbody>{''.join(rows)}</tbody></table></div><p class="small-text muted">{expiry}</p>'''


def evidence(lang):
    ar = lang == 'ar'
    country_ar = 'السعودية — بحسب تصريح صاحب الموقع؛ إعداد الدولة لم يظهر صراحة في الفيديو' if LISTING.get('country') == 'SA' else 'غير معروف'
    country_en = 'Saudi Arabia — reported by the owner; the selected country setting was not explicitly shown' if LISTING.get('country') == 'SA' else 'Unknown'
    reported_date = str(DATE_EVIDENCE.get('reportedTestDate', 'غير محدد'))
    displayed_time = str(DATE_EVIDENCE.get('displayedTime', '4:51'))
    visible_day_month = str(DATE_EVIDENCE.get('visibleGregorianDayMonth', '15 November'))
    visible_day_month_ar = visible_day_month.replace('November', 'نوفمبر')
    image_path = PATH + str(DATE_EVIDENCE.get('imagePath', ''))
    image_width = str(DATE_EVIDENCE.get('imageWidth', 768))
    image_height = str(DATE_EVIDENCE.get('imageHeight', 1365))
    date_note_ar = f'{reported_date} — الوقت الظاهر {displayed_time}. يؤكد صاحب الموقع أن لقطة الساعة مرتبطة بفيديو التجربة. هذا توثيق مقدم منه، وليس تسجيلًا متصلًا يثبت زمن الفيديو بصورة مستقلة أو نجاح خصم السلة؛ صباح/مساء والمنطقة الزمنية غير ظاهرين.'
    date_note_en = f'{reported_date} — displayed time {displayed_time}. The owner confirms that the clock screenshot belongs with the test video. This is owner-provided evidence, not an independently timestamped continuous recording or proof of a checkout discount. AM/PM and time zone are not shown.'
    items = [('مصدر الدليل', 'فيديوهان قدمهما صاحب الموقع'), ('تاريخ مراجعة الفيديو', REVIEWED), ('بلد التجربة المبلغ عنه', country_ar), ('تاريخ التجربة المبلغ عنه', date_note_ar), ('تاريخ التصوير', 'غير موثق؛ لا نستنتجه من ساعة الجهاز'), ('ما ظهر', 'فتح الحملة واستلام قسائم'), ('تطبيق خصم في السلة', 'لم يظهر في الفيديو'), ('الاستخدام العالمي', 'غير متحقق منه')] if ar else [('Evidence source', 'Two owner-submitted videos'), ('Video review date', REVIEWED), ('Reported test country', country_en), ('Reported test date', date_note_en), ('Recording date', 'Unverified; not inferred from the device clock'), ('Observed result', 'Campaign opened; coupons received'), ('Coupon applied to cart', 'Not shown in the recording'), ('Worldwide availability', 'Not independently verified')]
    disclosure = ('عرض لقطة التاريخ والساعة' if ar else 'View date screenshot')
    alt = f'ساعة الهاتف تعرض {visible_day_month_ar} عند {displayed_time}؛ ليست صفحة دفع' if ar else f'Phone clock showing {visible_day_month} at {displayed_time}; not a checkout page'
    caption = ('لقطة الساعة مقدمة من صاحب الموقع، بلا بيانات التقاط موثوقة، ولا تتحقق من نجاح الدفع.' if ar else 'Screenshot supplied by the owner, without trusted capture metadata, and it does not verify payment success.')
    proof = f'<details class="proof-disclosure"><summary>{disclosure}</summary><figure class="proof-figure"><img width="{escape(image_width, quote=True)}" height="{escape(image_height, quote=True)}" src="{escape(image_path, quote=True)}" loading="lazy" decoding="async" alt="{escape(alt, quote=True)}"><figcaption class="proof-caption">{caption}</figcaption></figure></details>'
    return '<dl class="evidence-grid">' + ''.join(f'<div class="evidence-item"><dt>{escape(key)}</dt><dd>{escape(value)}</dd></div>' for key, value in items) + '</dl>' + proof


def card(lang, compact=False):
    ar = lang == 'ar'
    badge = 'رمز بحث داخل التطبيق' if ar else 'App search campaign code'
    heading = 'ابحث عن الرمز في تطبيق SHEIN' if ar else 'Search for the code in the SHEIN app'
    copy = 'نسخ الرمز' if ar else 'Copy code'
    visit = 'زيارة SHEIN الرسمية' if ar else 'Visit official SHEIN'
    instruction = 'افتح التطبيق والصق الرمز في شريط البحث. لا نوصي بإدخاله في خانة القسيمة بناءً على هذا الدليل.' if ar else 'Open the app and paste the code into its search bar. The recording does not establish that this is a checkout coupon code.'
    result = 'ظهر فتح حملة WELCOME TO SHEIN واستلام قسائم بشروط. لا يثبت الفيديو تطبيق خصم في السلة.' if ar else 'The recording showed WELCOME TO SHEIN and receipt of conditional coupons. It did not show a discount applied to a cart.'
    note = 'زر الزيارة يفتح صفحة المتجر الرسمية، وليس رابطًا مباشرًا للحملة أو تفعيلًا تلقائيًا للرمز. قد تحتاج إلى فتح التطبيق بنفسك.' if ar else 'The visit button opens the official store homepage, not a campaign deep link or automatic activation. You may need to open the app yourself.'
    first, second = LISTING['observedCoupons'][:2]
    summary = (f"قسائم ظهرت في التجربة: {first['discountPercent']}% فوق {first['minimumSpend']} ريالًا بسقف {first['maximumDiscount']} ريالًا، و{second['discountPercent']}% فوق {second['minimumSpend']} ريالًا بسقف {second['maximumDiscount']} ريالًا؛ للمستخدم الجديد وعلى منتجات مختارة فقط. لا نؤكد توفرها الآن." if ar else f"Observed coupons: {first['discountPercent']}% above SAR {first['minimumSpend']}, capped at SAR {first['maximumDiscount']}; and {second['discountPercent']}% above SAR {second['minimumSpend']}, capped at SAR {second['maximumDiscount']}. New users and selected products only. Current availability is unverified.")
    tail = f'<p class="observed-note">{summary}</p>' if compact else ''
    return f'''<article class="campaign-card" data-coupon-card>
  <div class="coupon-header"><span class="coupon-label">SHEIN · {badge}</span></div>
  <h2>{heading}</h2>
  <div class="coupon-code-box"><strong class="coupon-code" dir="ltr">{CODE}</strong><button class="button" type="button" data-copy="{CODE}" aria-label="{copy} {CODE}">{copy}</button></div>
  <p class="code-instruction">{instruction}</p>
  {tail}
  <div class="code-actions"><a class="button button-secondary" href="{DESTINATION}" target="_blank" rel="noopener noreferrer" data-store-link>{visit}</a></div>
  <p class="small-text muted">{note}</p>
  <p class="small-text muted">{result}</p>
</article>'''


def steps(lang):
    ar = lang == 'ar'
    values = [('انسخ الرمز', 'اضغط زر نسخ الرمز أو انسخه يدويًا.'), ('ابحث داخل التطبيق', 'افتح تطبيق SHEIN والصق الرمز في شريط البحث ثم نفذ البحث.'), ('راجع القسائم', 'إذا ظهرت الحملة، اقرأ القسائم المتاحة لحسابك والأهلية والسقف والصلاحية.'), ('تحقق قبل الدفع', 'استخدم القسيمة المؤهلة وفق تعليماتها، وتأكد من ظهور مبلغ خصمها في ملخص الطلب.')] if ar else [('Copy the code', 'Use the copy button or copy the code manually.'), ('Search in the app', 'Open the SHEIN app, paste the code into the search bar and search.'), ('Read coupon conditions', 'If a campaign appears, check the coupons available to your account, eligibility, caps and expiry.'), ('Check before payment', 'Use an eligible coupon according to its instructions and confirm its separate deduction in the order summary.')]
    return '<ol class="use-steps">' + ''.join(f'<li><strong>{escape(title)}</strong><p>{escape(text)}</p></li>' for title, text in values) + '</ol>'


def faq_values(lang):
    if lang == 'ar':
        return [
            ('أين أكتب S4T32؟', 'اكتبه في شريط البحث داخل تطبيق SHEIN. هذا هو مكان الاستخدام الظاهر في الفيديو، وليس خانة قسيمة الدفع.'),
            ('ما قيمة الخصم المضمون؟', 'لا يثبت الفيديو نسبة خصم ثابتة. ظهرت قسائم منفصلة بشروط ونسب وسقوف، ولم يظهر تطبيقها على السلة.'),
            ('هل القسائم لجميع المستخدمين؟', 'القسيمتان اللتان استطعنا قراءة شروطهما تحملان «مستخدم جديد فقط» و«منتجات مختارة». لا نستنتج من ذلك أهلية حسابك.'),
            ('هل يعمل في السعودية وبقية الدول؟', 'ذكر صاحب الموقع أن السعودية هي بلد التجربة، وظهرت مبالغ بالريال السعودي. إعداد الدولة لم يظهر صراحة، ولم يظهر تطبيق قسيمة في السلة. لا نضمن التوفر لكل حساب سعودي أو أي بلد آخر؛ راجع الشروط في تطبيقك.'),
            ('هل استلام القسائم يعني تطبيق الخصم؟', 'لا. رسالة «تم الاستلام بنجاح» تعني استلام قسائم في التجربة، ولا تثبت استخدامها عند الدفع أو إتمام شراء.'),
            ('هل Couponova معتمدة من SHEIN؟', 'Couponova موقع مستقل، وليس موقع SHEIN الرسمي ولا يدعي اعتمادًا منها. أسماء العلامات التجارية تعود لأصحابها.')
        ]
    return [
        ('Where do I enter S4T32?', 'Enter it in the SHEIN app search bar. That is the entry point shown in the video, not the checkout coupon field.'),
        ('What guaranteed discount applies?', 'The recording does not establish a fixed discount. It showed separate conditional coupons and did not show their application to a cart.'),
        ('Are the observed coupons for everyone?', 'The two readable coupons stated new users only and selected products. Your own account eligibility is not verified.'),
        ('Does it work in Saudi Arabia and worldwide?', 'The owner reports Saudi Arabia as the test country, and Saudi riyal amounts were visible. The country setting and a coupon applied to a cart were not shown. Availability for every Saudi account or another country is not guaranteed.'),
        ('Does receipt of coupons prove a checkout discount?', 'No. The receipt message establishes that coupons were received in that recording, not that they were redeemed or a purchase completed.'),
        ('Is Couponova officially endorsed by SHEIN?', 'Couponova is an independent website, not the official SHEIN website, and does not claim official endorsement.')
    ]


def faq_html(values):
    return '<div class="faq-list">' + ''.join(f'<details><summary>{escape(question)}</summary><p>{escape(answer)}</p></details>' for question, answer in values) + '</div>'


def section(identifier, title, content):
    return f'<section class="section" id="{identifier}"><div class="container"><h2>{title}</h2>{content}</div></section>'


def page(route, lang, title, description, heading, intro, content, alternate=None, homepage=False, faqs=None, kind='WebPage'):
    ar = lang == 'ar'
    home = '' if ar else 'en/'
    store = 'shein/' if ar else 'en/shein/'
    direction = 'rtl' if ar else 'ltr'
    url = BASE + route
    default_route = route if ar or alternate is None else alternate
    hreflang = {lang: url, 'x-default': BASE + default_route}
    if alternate is not None:
        hreflang['en' if ar else 'ar'] = BASE + alternate
    alternates = '\n'.join(f'  <link rel="alternate" hreflang="{language}" href="{target}">' for language, target in hreflang.items())
    nav = [('الرئيسية', ''), ('تفاصيل شي ان', 'shein/'), ('طريقة الاستخدام', 'shein/how-to-use/'), ('المستخدم الجديد', 'shein/new-user-code/')] if ar else [('Home', 'en/'), ('Code details', 'en/shein/')]
    nav_markup = ''.join(f'<a href="{PATH}{target}"' + (' aria-current="page"' if target == route else '') + f'>{label}</a>' for label, target in nav)
    if alternate is not None:
        nav_markup += f'<a class="language-link" href="{PATH}{alternate}" lang="{"en" if ar else "ar"}">{"English" if ar else "العربية"}</a>'
    else:
        nav_markup += f'<a class="language-link" href="{PATH}en/shein/" lang="en">English</a>'
    website = {'@type': 'WebSite', '@id': BASE + '#website', 'name': 'Couponova', 'url': BASE, 'inLanguage': ['ar', 'en']}
    web_page = {'@type': kind, '@id': url + '#webpage', 'name': title, 'description': description, 'url': url, 'inLanguage': lang, 'dateModified': PAGE_UPDATED, 'isPartOf': {'@id': BASE + '#website'}}
    crumbs = [{'@type': 'ListItem', 'position': 1, 'name': 'الرئيسية' if ar else 'Home', 'item': BASE + home}]
    if route != home:
        crumbs.append({'@type': 'ListItem', 'position': 2, 'name': heading, 'item': url})
    graph = [website, web_page]
    if len(crumbs) > 1:
        graph.append({'@type': 'BreadcrumbList', 'itemListElement': crumbs})
    if faqs:
        graph.append({'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faqs]})
    # Only observed facts are marked up. No Product, Offer, rating or guessed validity.
    schema = schema_script({'@context': 'https://schema.org', '@graph': graph})
    footer_links = ''.join(link(target, label) for target, label in [('about/', 'من نحن'), ('editorial-policy/', 'سياسة التحرير'), ('contact/', 'اتصل بنا')])
    independent = 'Couponova موقع مستقل ولا يدعي اعتمادًا من SHEIN. شروط حسابك والخصم الظاهر قبل الدفع هي المرجع النهائي.' if ar else 'Couponova is independent and does not claim SHEIN endorsement. Your account’s terms and the order summary are the final reference.'
    jump = 'انتقل إلى المحتوى' if ar else 'Skip to content'
    hero_card = card(lang, compact=True).replace('data-coupon-card', 'data-coupon-card id="coupons"', 1) if homepage else ''
    home_css = f'<link rel="stylesheet" href="{PATH}assets/home.css">' if homepage else ''
    html = f'''<!doctype html>
<html lang="{lang}" dir="{direction}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#{'111111' if homepage else '090909'}">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description, quote=True)}">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <link rel="canonical" href="{url}">
{alternates}
  <meta property="og:type" content="website">
  <meta property="og:locale" content="{'ar_AR' if ar else 'en_US'}">
  <meta property="og:site_name" content="Couponova">
  <meta property="og:title" content="{escape(title, quote=True)}">
  <meta property="og:description" content="{escape(description, quote=True)}">
  <meta property="og:url" content="{url}">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{escape(title, quote=True)}">
  <meta name="twitter:description" content="{escape(description, quote=True)}">
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='18' fill='%23111111'/%3E%3Ctext x='50' y='69' font-size='62' text-anchor='middle' fill='white' font-family='Arial' font-weight='bold'%3EC%3C/text%3E%3C/svg%3E">
  <link rel="stylesheet" href="{PATH}assets/site.css">
  {home_css}
  {schema}
  <script src="{PATH}assets/site.js" defer></script>
</head>
<body class="{'home-page' if homepage else 'content-page'}">
<a class="skip-link" href="#main">{jump}</a>
<header class="site-header"><div class="container navbar"><a class="logo" href="{PATH}{home}"><span class="logo-mark" aria-hidden="true">C</span>Couponova</a><nav class="nav-links" aria-label="{'التنقل الرئيسي' if ar else 'Main navigation'}">{nav_markup}</nav></div></header>
<main id="main">
  <section class="hero"><div class="container"><p class="eyebrow">COUPONOVA · SHEIN</p><h1>{heading}</h1><p class="hero-description">{intro}</p>{hero_card}</div></section>
  {content}
</main>
<footer class="site-footer"><div class="container"><div class="footer-row"><strong>Couponova</strong><nav class="footer-links" aria-label="{'روابط الموقع' if ar else 'Site links'}">{footer_links}{link(store, 'تفاصيل شي ان' if ar else 'Code details')}</nav></div><p class="small-text">{independent}</p><p class="small-text">© <span data-year>2026</span> Couponova</p></div></footer>
</body>
</html>
'''
    html = '\n'.join(line.rstrip() for line in html.splitlines()) + '\n'
    target = ROOT / route / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding='utf-8')
    return route


modified = []
for lang, route, alternate in [('ar', '', 'en/'), ('en', 'en/', '')]:
    ar = lang == 'ar'
    values = faq_values(lang)
    title = 'كود خصم شي ان السعودية S4T32 | طريقة البحث وشروط القسائم' if ar else 'SHEIN S4T32 Code | App Search and Coupon Conditions'
    heading = 'كود خصم شي ان السعودية<br>رمز البحث <span dir="ltr">S4T32</span>' if ar else 'SHEIN code <span>S4T32</span><br>Start with app search'
    description = 'دليل كود خصم شي ان السعودية S4T32: البحث داخل التطبيق وشروط القسائم التي ظهرت في الفيديو، مع الأهلية وسقف الخصم وحدود التحقق دون ضمان خصم ثابت.' if ar else 'How to use S4T32 in SHEIN app search. See observed coupon conditions, new-user eligibility, discount caps and evidence limits, without a fixed-discount guarantee.'
    intro = 'تبحث عن كوبون شي ان في السعودية؟ ابحث عن الرمز داخل التطبيق. يذكر صاحب الموقع السعودية بلدًا للتجربة؛ شاهدنا حملة وقسائم بشروط، وليس خصمًا ثابتًا على كل طلب.' if ar else 'Looking for a SHEIN coupon code? Search for the code in the app. The recording showed a campaign with conditional coupons, not a fixed discount on every order.'
    form = f'''<form class="search-form" role="search"><label class="sr-only" for="code-search">{'ابحث داخل بطاقة الرمز' if ar else 'Search the code information'}</label><input id="code-search" type="search" data-coupon-search placeholder="{'ابحث عن شروط القسائم' if ar else 'Search coupon conditions'}"><button class="button" type="submit">{'بحث' if ar else 'Search'}</button></form><p class="empty-message" data-empty hidden>{'لا توجد نتيجة مطابقة للمعلومات المتاحة.' if ar else 'No matching information was found.'}</p>'''
    content = section('conditions', 'شروط القسائم التي ظهرت في الفيديو' if ar else 'Coupon conditions observed in the video', conditions(lang))
    content += section('how', 'طريقة استخدام الرمز' if ar else 'How to use the code', steps(lang))
    content += section('evidence', 'ما الذي تحققنا منه؟' if ar else 'What did we verify?', evidence(lang))
    content += section('search', 'العثور على معلومات الرمز' if ar else 'Find code information', form)
    content += section('guides', 'تفاصيل تساعدك قبل الاستخدام' if ar else 'Details to read before use', '<p>' + link('shein/' if ar else 'en/shein/', 'تفاصيل رمز بحث شيان' if ar else 'Code details') + '</p><p>' + link('shein/how-to-use/', 'دليل الاستخدام وأسباب عدم ظهور الحملة' if ar else 'Usage guide in Arabic') + '</p><p>' + link('shein/new-user-code/', 'شروط قسائم المستخدم الجديد' if ar else 'New-user coupon conditions in Arabic') + '</p>')
    content += section('faq', 'أسئلة شائعة' if ar else 'Frequently asked questions', faq_html(values))
    modified.append(page(route, lang, title, description, heading, intro, content, alternate, homepage=True, faqs=values))

for lang, route, alternate in [('ar', 'shein/', 'en/shein/'), ('en', 'en/shein/', 'shein/')]:
    ar = lang == 'ar'
    title = 'S4T32: رمز بحث شي ان وشروط القسائم | Couponova' if ar else 'S4T32 SHEIN Search Code and Observed Coupons | Couponova'
    heading = 'S4T32: رمز بحث شي ان، لا خصم ثابت مضمون' if ar else 'S4T32: SHEIN app search, not a guaranteed fixed discount'
    intro = 'تفاصيل رمز بحث شيان: مكان إدخاله، ما ظهر في الفيديو، وشروط القسائم وحدود ما نعرفه.' if ar else 'Code details: the app entry point, observed campaign, coupon conditions and verification limits.'
    content = section('coupons', 'رمز الحملة الأساسي' if ar else 'Featured campaign code', card(lang))
    content += section('conditions', 'قسائم ظهرت في التجربة' if ar else 'Coupons observed in the recording', conditions(lang))
    content += section('how-to-use', 'من البحث إلى مراجعة الخصم' if ar else 'From app search to checking a discount', steps(lang))
    content += section('evidence', 'حدود التحقق' if ar else 'Evidence limits', evidence(lang))
    content += section('guides', 'اقرأ قبل الاستخدام' if ar else 'Read before use', '<p>' + link('shein/how-to-use/', 'طريقة البحث وأسباب عدم ظهور العرض' if ar else 'Usage guide in Arabic') + '</p><p>' + link('shein/new-user-code/', 'شروط قسائم المستخدم الجديد' if ar else 'New-user conditions in Arabic') + '</p>')
    values = faq_values(lang)
    content += section('faq', 'أسئلة عن الرمز' if ar else 'Questions about the code', faq_html(values))
    modified.append(page(route, lang, title, intro, heading, intro, content, alternate, faqs=values))

intro = 'ظهرت بعد البحث قسائم شي ان للمستخدم الجديد تحمل «مستخدم جديد فقط» و«منتجات مختارة». نوضح ما ظهر دون افتراض أهلية حسابك أو توفر القسائم الآن.'
content = section('codes', 'البحث عن الحملة', card('ar'))
content += section('conditions', 'النسب والسقوف والأهلية في الفيديو', conditions('ar'))
content += section('eligibility', 'هل حسابك مؤهل؟', '<p>الحصول على رسالة استلام لا يثبت أهلية الحساب عند الدفع. اقرأ تعريف المستخدم الجديد وشروط المنتجات داخل حسابك، ولا تعتمد على النسبة وحدها. لا ننصح بإنشاء حسابات للتحايل على شروط SHEIN.</p><p>القسائم المعروضة هنا سجل لما ظهر في فيديو، وليست قائمة عروض مؤكدة الآن. راجع القيمة المؤهلة وسقف الخصم والصلاحية قبل استخدام أي قسيمة.</p>')
content += section('evidence', 'مصدر المعلومات وحدودها', evidence('ar'))
content += section('how-to-use', 'طريقة الاستخدام الصحيحة', steps('ar'))
values = [faq_values('ar')[2], faq_values('ar')[4], ('هل يمكن جمع القسيمتين في الطلب نفسه؟', 'لم يثبت الفيديو إمكانية الجمع. لا تفترض السماح به؛ اتبع شروط SHEIN والقسيمة المختارة. لا تضف النسبتين معًا.')]
content += section('faq', 'أسئلة المستخدم الجديد', faq_html(values))
modified.append(page('shein/new-user-code/', 'ar', 'قسائم شي ان للمستخدم الجديد عبر S4T32 | الشروط والسقوف', intro, 'قسائم المستخدم الجديد: ما ظهر بعد بحث S4T32', intro, content, faqs=values))

intro = 'طريقة استخدام كوبون شي ان تبدأ من بحث التطبيق لفتح حملة. هذا يختلف عن إدخال رمز قسيمة عند الدفع؛ نجاح النسخ أو الاستلام وحده لا يثبت الخصم.'
content = section('how-to-use', 'خطوات البحث داخل التطبيق', steps('ar'))
content += section('difference', 'رمز البحث ليس قسيمة الدفع', '<p>رمز البحث يفتح صفحة حملة أو عروض. القسيمة التي تحصل عليها من الحملة لها شروطها الخاصة، وقد تستخدم وفق تعليمات حسابك عند الدفع. لا ننقل خصومات المنتجات الظاهرة في الحملة إلى نسبة ثابتة للرمز.</p><p>إذا لم تظهر الحملة، تحقق من كتابة الرمز والدولة المختارة ونسخة التطبيق وتوفر الحملة. لا نملك دليلًا يحدد سبب فشل تجربة معينة أو بلدًا مضمونًا.</p>')
content += section('evidence', 'ما يثبته الدليل وما لا يثبته', evidence('ar'))
content += section('codes', 'بطاقة نسخ الرمز', card('ar', compact=True))
values = [faq_values('ar')[0], faq_values('ar')[4], ('كيف أتأكد من الخصم الحقيقي؟', 'راجع سطر خصم القسيمة وإجمالي الطلب قبل الدفع، وافصل خصم القسيمة عن تخفيضات المنتجات والشحن. لا تحتاج إلى إتمام شراء لمجرد التحقق من المبلغ الظاهر.')]
content += section('faq', 'أسئلة الاستخدام', faq_html(values))
modified.append(page('shein/how-to-use/', 'ar', 'طريقة استخدام S4T32 في بحث شي ان | دليل Couponova', intro, 'أين تكتب S4T32 وكيف تتحقق من القسيمة؟', intro, content, faqs=values))

intro = 'نفصل بين فتح حملة، واستلام قسيمة، وتطبيق خصم في السلة، وإتمام شراء. لكل ادعاء مستوى دليل مختلف.'
content = section('verification', 'مستويات التحقق', '<p><strong>فتح حملة مشاهد:</strong> يظهر إدخال رمز البحث وفتح الحملة في تسجيل. لا يعني خصمًا مؤكدًا في السلة.</p><p><strong>استلام قسيمة مشاهد:</strong> تظهر رسالة الاستلام وشروط القسيمة. لا يثبت ذلك استردادها عند الدفع.</p><p><strong>خصم سلة موثق:</strong> يحتاج ملخصًا يبين مبلغ خصم القسيمة وشروط التجربة. هذا لم يظهر في التسجيل الحالي.</p><p><strong>غير متحقق:</strong> ما لا تدعمه تجربة أو مصدر واضح لا يوصف بأنه مضمون. لا نضمن التوفر لكل حساب أو بلد.</p>')
content += section('records', 'ما نسجله؟', '<p>نسجل مصدر الدليل وتاريخ مراجعته، ونفصل ذلك عن تاريخ التصوير والتجربة. نميز بين الدولة الظاهرة في التطبيق والدولة التي يذكرها صاحب التجربة، ولا نضع تاريخًا لم نستطع توثيقه. نسجل النسبة والحد الأدنى وسقف الخصم والمنتجات والصلاحية كما ظهرت، لا كما نتمنى أن تكون.</p>')
content += section('current', 'الدليل الحالي للرمز', evidence('ar') + '<p>القسائم المرصودة بشروطها موضحة في ' + link('shein/new-user-code/', 'صفحة المستخدم الجديد') + '. لا نوصفها بأنها متوفرة الآن دون إعادة تحقق.</p>')
content += section('privacy', 'الخصوصية والتصحيح', '<p>لا ننشر الفيديو الأصلي أو بيانات الحساب والطلب والدفع. يمكن تقديم دليل منقح لمراجعته، ويجب عدم إرسال البيانات الحساسة في بلاغات GitHub العامة.</p><p>نراجع المعلومات عند توفر دليل جديد أو بلاغ، ونصحح الحالة دون تحويل تاريخ تعديل الصفحة إلى تاريخ اختبار. لا نستنتج اعتماد SHEIN أو شراكة أو عمولة من مجرد ظهور الكود.</p><p>' + link('contact/', 'إرسال ملاحظة أو بلاغ') + '</p>')
modified.append(page('editorial-policy/', 'ar', 'سياسة التحرير والتحقق من الرموز والقسائم | Couponova', intro, 'سياسة التحرير والتحقق', intro, content))

# Keep every existing sitemap URL, including trust pages that are not rewritten.
ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
tree = ET.parse(ROOT / 'sitemap.xml')
ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
for entry in tree.getroot().findall('s:url', ns):
    location = entry.find('s:loc', ns)
    if location is not None and location.text in {BASE + route for route in modified}:
        lastmod = entry.find('s:lastmod', ns)
        if lastmod is None:
            lastmod = ET.SubElement(entry, '{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
        lastmod.text = PAGE_UPDATED
ET.indent(tree, space='  ')
tree.write(ROOT / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
with (ROOT / 'sitemap.xml').open('ab') as handle:
    handle.write(b'\n')
print('Built', len(modified), 'approved pages. Retained all sitemap URLs.')
