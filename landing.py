"""
landing.py v2 — Nazil | LiquiFund Public Landing Page
Light-mode professional fintech design:
  - Blue/emerald trust palette, Heebo Hebrew font
  - Animated logo with liquid-drop SVG
  - Interactive Chart.js calculator
  - FAQ agent with 55 Q&As + live search
  - Team section
  - CRM lead capture via crm.create_lead()
"""

import sys
import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

_HERE = Path(__file__).parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import crm  # noqa

# ═════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="נזיל | שחרור הון פנסיוני חכם",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ═════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═════════════════════════════════════════════════════════════════════════════
for _k, _v in {
    "calc_lead_sent": False,
    "upload_lead_sent": False,
    "ai_messages": [],
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ─────────────────────────────────────────────────────────────────────────────
# LEGAL PAGE HELPERS
# ─────────────────────────────────────────────────────────────────────────────
_LEGAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;600;700;800&family=Montserrat:wght@800;900&display=swap');
*{box-sizing:border-box;margin:0;padding:0;}
body,[data-testid="stAppViewContainer"]{background:#F7F8FF!important;}
[data-testid="stToolbar"],[data-testid="stDecoration"],#MainMenu,footer,header{display:none!important;}
.lp-wrap{max-width:820px;margin:0 auto;padding:3rem 2rem 5rem;direction:rtl;font-family:'Heebo',sans-serif;color:#1B2559;}
.lp-back{display:inline-flex;align-items:center;gap:.4rem;color:#2B5CE8;font-size:.9rem;font-weight:600;cursor:pointer;margin-bottom:2rem;text-decoration:none;background:none;border:none;padding:0;}
.lp-back:hover{text-decoration:underline;}
.lp-chip{display:inline-block;font-size:.72rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#2B5CE8;background:#EEF2FF;border:1px solid rgba(43,92,232,.18);border-radius:50px;padding:.3rem .9rem;margin-bottom:.8rem;}
.lp-h1{font-family:'Montserrat',sans-serif;font-size:2rem;font-weight:900;color:#1B2559;margin-bottom:.5rem;line-height:1.2;}
.lp-date{font-size:.82rem;color:#A8B2CC;margin-bottom:2.5rem;}
.lp-h2{font-family:'Montserrat',sans-serif;font-size:1.1rem;font-weight:800;color:#1B2559;margin:2rem 0 .6rem;padding-right:.9rem;border-right:3px solid #2B5CE8;}
.lp-p{font-size:.93rem;color:#4A5279;line-height:1.85;margin-bottom:.8rem;}
.lp-ul{font-size:.93rem;color:#4A5279;line-height:1.85;padding-right:1.4rem;margin-bottom:.8rem;}
.lp-ul li{margin-bottom:.3rem;}
.lp-box{background:#EEF2FF;border:1.5px solid rgba(43,92,232,.18);border-radius:14px;padding:1.2rem 1.5rem;margin:1.5rem 0;font-size:.9rem;color:#2B5CE8;font-weight:600;line-height:1.7;}
.lp-warn{background:#FFF7ED;border:1.5px solid #F59E0B;border-radius:14px;padding:1.2rem 1.5rem;margin:1.5rem 0;font-size:.88rem;color:#92400E;line-height:1.7;}
.lp-divider{height:1px;background:#E4E7F2;margin:2rem 0;}
.lp-footer{font-size:.78rem;color:#A8B2CC;margin-top:3rem;padding-top:1.5rem;border-top:1px solid #E4E7F2;line-height:1.7;}
</style>
"""

_COMPANY = "עדי אלבז בע\"מ"
_COMPANY_NUM = "516749371"
_ADDR = "הנוטר 7, חיפה"
_EMAIL = "adi@nazil.info"
_DATE = "אפריל 2026"


def _legal_header(chip: str, title: str) -> None:
    st.markdown(_LEGAL_CSS, unsafe_allow_html=True)
    st.markdown(f"""
<div class="lp-wrap">
  <a class="lp-back" onclick="window.location.href='/'">← חזרה לאתר</a>
  <div class="lp-chip">{chip}</div>
  <h1 class="lp-h1">{title}</h1>
  <div class="lp-date">עודכן לאחרונה: {_DATE} | {_COMPANY} | ח.פ. {_COMPANY_NUM}</div>
""", unsafe_allow_html=True)


def _legal_footer() -> None:
    st.markdown(f"""
  <div class="lp-footer">
    {_COMPANY} | ח.פ. {_COMPANY_NUM} | {_ADDR} | <a href="mailto:{_EMAIL}" style="color:#2B5CE8;">{_EMAIL}</a><br>
    לשאלות ובירורים: <a href="mailto:{_EMAIL}" style="color:#2B5CE8;">{_EMAIL}</a>
  </div>
</div>
""", unsafe_allow_html=True)


def _render_terms() -> None:
    _legal_header("משפטי", "תנאי שימוש")
    st.markdown("""
<div class="lp-box">
  ⚠️ שירות נזיל מספק מידע ונתונים בלבד ואינו מהווה ייעוץ פנסיוני, ייעוץ השקעות, שיווק פנסיוני או תחליף לייעוץ מקצועי מורשה מכל סוג שהוא.
</div>

<h2 class="lp-h2">1. כללי</h2>
<p class="lp-p">ברוכים הבאים לנזיל (LiquiFund), המופעל על ידי <b>עדי אלבז בע"מ</b>, ח.פ. 516749371 (להלן: "החברה"). השימוש באתר ובשירותיו מהווה הסכמה מלאה לתנאי שימוש אלו. אם אינכם מסכימים לתנאים — נא הפסיקו את השימוש.</p>

<h2 class="lp-h2">2. טיב השירות — מידע בלבד</h2>
<p class="lp-p">האתר מספק <b>שירות ריכוז וניתוח מידע בלבד</b> על בסיס נתוני המסלקה הפנסיונית שמועלים על ידי המשתמש. כל תוצאה, חישוב, הצגת נתון או "המלצה" המופיעה באתר מהווה <b>סימולציה אינפורמטיבית בלבד</b> ואינה:</p>
<ul class="lp-ul">
  <li>ייעוץ פנסיוני כהגדרתו בחוק הפיקוח על שירותים פיננסיים (ייעוץ, שיווק ומערכת סליקה פנסיוניים), תשס"ה-2005</li>
  <li>שיווק פנסיוני או המלצה לרכישה/מכירה/שינוי מוצר פנסיוני</li>
  <li>ייעוץ השקעות על פי חוק הסדרת העיסוק בייעוץ השקעות, תשנ"ה-1995</li>
  <li>ייעוץ משפטי, מיסויי או פיננסי מחייב מכל סוג</li>
</ul>
<p class="lp-p">לפני ביצוע כל פעולה בחסכונות הפנסיוניים שלכם, יש להתייעץ עם יועץ פנסיוני מורשה.</p>

<div class="lp-warn">
  ⚠️ ביצוע פעולות במוצר פנסיוני ללא ייעוץ מוסמך עלול לפגוע בקצבת הפרישה, ברצף הביטוחי ובזכויות סוציאליות. החברה לא תישא באחריות לכל נזק הנובע מהסתמכות על המידע המוצג.
</div>

<h2 class="lp-h2">3. תנאי גיל ואהלות</h2>
<p class="lp-p">השירות מיועד לבני 18 ומעלה. השימוש מותר לאנשים פרטיים עבור חסכונותיהם האישיים בלבד.</p>

<h2 class="lp-h2">4. העלאת קבצים</h2>
<p class="lp-p">המשתמש מאשר כי קובץ המסלקה שהוא מעלה שייך לו ומתייחס לנתוניו האישיים בלבד. העלאת קבצים של אחרים ללא הסמכה מפורשת אסורה. הקובץ מעובד אוטומטית ונמחק מהשרתים תוך 24 שעות מרגע העלאתו.</p>

<h2 class="lp-h2">5. דיוק המידע</h2>
<p class="lp-p">החברה עושה מאמץ סביר לדייק בחישובים ובהצגת נתונים, אך אינה מתחייבת לנכונות מלאה. הנתונים מבוססים על הקובץ שמעלה המשתמש, ועשויים שלא לשקף את המצב העדכני בגופי הפנסיה.</p>

<h2 class="lp-h2">6. קניין רוחני</h2>
<p class="lp-p">כל זכויות הקניין הרוחני באתר, לרבות עיצוב, תוכנה, אלגוריתמים, טקסטים וסמלים, שייכות לחברה. אין להעתיק, לשכפל, להפיץ או לעשות כל שימוש מסחרי ללא אישור מפורש בכתב.</p>

<h2 class="lp-h2">7. הגבלת אחריות</h2>
<p class="lp-p">האתר ניתן "כמות שהוא" (AS IS). החברה לא תישא באחריות לכל נזק ישיר, עקיף, תוצאתי או מיוחד הנובע מ:</p>
<ul class="lp-ul">
  <li>שימוש במידע המוצג באתר</li>
  <li>הסתמכות על חישובי הסימולציה</li>
  <li>תקלות טכניות, הפסקות שירות או אובדן נתונים</li>
  <li>גישה בלתי מורשית לנתונים, ככל שבוצעה למרות אמצעי האבטחה הנקוטים</li>
</ul>
<p class="lp-p">אחריות החברה בכל מקרה לא תעלה על הסכום ששילם המשתמש עבור השירות, ולא פחות מ-0 ₪ לגבי שירות חינמי.</p>

<h2 class="lp-h2">8. ביטול עסקה</h2>
<p class="lp-p">בהתאם לחוק הגנת הצרכן, תשמ"א-1981, ותקנות הגנת הצרכן (ביטול עסקה), תשע"א-2010 — ככל שנרכש שירות בתשלום, ניתן לבטלו תוך <b>14 ימים</b> מיום ביצוע ההזמנה. ביטול ייעשה בפנייה בכתב לכתובת: <a href="mailto:adi@nazil.info" style="color:#2B5CE8;">adi@nazil.info</a></p>

<h2 class="lp-h2">9. שינויים בתנאים</h2>
<p class="lp-p">החברה רשאית לעדכן תנאים אלו בכל עת. הודעה על שינוי מהותי תפורסם באתר. המשך השימוש לאחר פרסום השינוי מהווה הסכמה לתנאים המעודכנים.</p>

<h2 class="lp-h2">10. סמכות שיפוט</h2>
<p class="lp-p">תנאים אלו כפופים לדין הישראלי. סמכות השיפוט הבלעדית לכל סכסוך נתונה לבתי המשפט המוסמכים במחוז חיפה.</p>
""", unsafe_allow_html=True)
    _legal_footer()


def _render_privacy() -> None:
    _legal_header("פרטיות", "מדיניות פרטיות")
    st.markdown("""
<div class="lp-box">
  🔒 אנו מתייחסים בכובד ראש לפרטיותכם. מסמך זה מסביר אילו נתונים נאספים, כיצד הם משמשים ואיך ניתן לממש את זכויותיכם.
</div>

<h2 class="lp-h2">1. מי אחראי על המידע</h2>
<p class="lp-p"><b>עדי אלבז בע"מ</b>, ח.פ. 516749371, הנוטר 7, חיפה (להלן: "החברה") היא הגורם האחראי על עיבוד המידע האישי הנאסף דרך האתר נזיל (LiquiFund). לפניות בנושא פרטיות: <a href="mailto:adi@nazil.info" style="color:#2B5CE8;">adi@nazil.info</a></p>

<h2 class="lp-h2">2. איזה מידע נאסף</h2>
<p class="lp-p">במהלך השימוש באתר עשויים להיאסף הנתונים הבאים:</p>
<ul class="lp-ul">
  <li><b>פרטי זיהוי:</b> שם מלא, מספר טלפון, כתובת דואר אלקטרוני</li>
  <li><b>מסמכים פנסיוניים:</b> קובץ מסלקה פנסיונית (DAT/XML/PDF) — <b>מידע פיננסי רגיש</b></li>
  <li><b>נתוני שימוש:</b> דפים שנצפו, פעולות שבוצעו, זמן שהייה (דרך Streamlit/לא כולל cookies עצמאיים)</li>
  <li><b>מידע שנוצר בשירות:</b> תוצאות חישובי הסימולציה המוצגים לכם</li>
</ul>
<p class="lp-p">אנו <b>לא</b> אוספים: מספרי כרטיסי אשראי, סיסמאות, מספרי תעודת זהות (אלא אם הוזנו מרצון).</p>

<h2 class="lp-h2">3. מטרות עיבוד המידע</h2>
<ul class="lp-ul">
  <li>מתן שירות ניתוח המסלקה ויצירת הסימולציה האישית</li>
  <li>יצירת קשר לצורך מתן המשך שירות</li>
  <li>שיפור השירות ואיכות הניתוח</li>
  <li>עמידה בדרישות חוקיות ורגולטוריות</li>
  <li>שליחת עדכונים ומידע שיווקי — רק למי שנתן הסכמה מפורשת</li>
</ul>

<h2 class="lp-h2">4. מסמכי המסלקה — טיפול מיוחד</h2>
<p class="lp-p">קובץ המסלקה מכיל מידע פיננסי אישי רגיש. לפיכך:</p>
<ul class="lp-ul">
  <li>הקובץ מועבד אוטומטית למטרת הניתוח בלבד</li>
  <li>הקובץ <b>נמחק מהשרתים תוך 24 שעות</b> מרגע העלאתו</li>
  <li>תוצאות הניתוח (נתונים מספריים בלבד) נשמרות לצורך מתן השירות</li>
  <li>הקובץ אינו מועבר לצדדים שלישיים בשום נסיבות</li>
</ul>

<h2 class="lp-h2">5. שמירת מידע ואחסון</h2>
<p class="lp-p">פרטי הלקוחות נשמרים במסד נתונים מאובטח המנוהל על ידי <b>Supabase</b> (שרתי Amazon Web Services, אזור us-east-1, ארה"ב). העברת המידע לחו"ל מתבצעת בהתאם להוראות חוק הגנת הפרטיות הישראלי ובאמצעות הסכמי עיבוד נתונים מתאימים.</p>
<p class="lp-p"><b>תקופת שמירה:</b> פרטי קשר ותוצאות ניתוח נשמרים עד 3 שנים מיום ההרשמה, או עד לבקשת מחיקה — המוקדם מביניהם.</p>

<h2 class="lp-h2">6. אבטחת מידע</h2>
<p class="lp-p">החברה נוקטת באמצעי אבטחה הכוללים:</p>
<ul class="lp-ul">
  <li>הצפנת תקשורת HTTPS/TLS בכל העברת נתונים</li>
  <li>אחסון מוצפן AES-256</li>
  <li>בקרת גישה מבוססת תפקיד (RBAC)</li>
  <li>גיבויים מוצפנים שוטפים</li>
</ul>
<p class="lp-p">למרות האמור, אין אבטחה מוחלטת ברשת. אנו ממליצים שלא לשתף פרטי גישה לחשבון עם אחרים.</p>

<h2 class="lp-h2">7. העברת מידע לצדדים שלישיים</h2>
<p class="lp-p">לא נמכור, נשכיר או נעביר את המידע האישי שלכם לצדדים שלישיים, <b>למעט</b> במקרים הבאים:</p>
<ul class="lp-ul">
  <li>ספקי תשתית ושירותים הכרחיים (Supabase, Streamlit Cloud) — בכפוף להסכמי עיבוד נתונים</li>
  <li>ציות לדרישת חוק, צו שיפוטי או דרישת רשות מוסמכת</li>
  <li>הגנה על זכויות החברה במסגרת הליך משפטי</li>
</ul>

<h2 class="lp-h2">8. עוגיות (Cookies)</h2>
<p class="lp-p">האתר פועל על פלטפורמת Streamlit ועשוי להשתמש ב-Session cookies טכניים לצורך תפקוד תקין. לא נעשה שימוש ב-cookies שיווקיים או עוקבים. ניתן לבטל cookies בהגדרות הדפדפן.</p>

<h2 class="lp-h2">9. זכויותיכם לפי חוק הגנת הפרטיות</h2>
<p class="lp-p">בהתאם לחוק הגנת הפרטיות, תשמ"א-1981 ותיקוניו, יש לכם זכות:</p>
<ul class="lp-ul">
  <li><b>עיון:</b> לקבל עותק של המידע השמור אודותיכם</li>
  <li><b>תיקון:</b> לתקן מידע שגוי או לא עדכני</li>
  <li><b>מחיקה:</b> לבקש מחיקת כל המידע (ייושם תוך 30 יום)</li>
  <li><b>הסרה מרשימות שיווק:</b> בכל עת, ללא תנאי</li>
</ul>
<p class="lp-p">לממוש הזכויות: שלחו פנייה ל-<a href="mailto:adi@nazil.info" style="color:#2B5CE8;">adi@nazil.info</a> עם ציון "בקשת פרטיות" בשורת הנושא.</p>

<h2 class="lp-h2">10. שינויים במדיניות</h2>
<p class="lp-p">מדיניות זו עשויה להתעדכן. עדכונים מהותיים יפורסמו באתר עם ציון תאריך השינוי. המשך השימוש לאחר פרסום השינוי מהווה הסכמה למדיניות המעודכנת.</p>
""", unsafe_allow_html=True)
    _legal_footer()


def _render_accessibility() -> None:
    _legal_header("נגישות", "הצהרת נגישות")
    st.markdown("""
<div class="lp-box">
  ♿ עדי אלבז בע"מ מחויבת לנגישות דיגיטלית שוויונית לכלל המשתמשים, לרבות אנשים עם מוגבלויות.
</div>

<h2 class="lp-h2">1. הבסיס החוקי</h2>
<p class="lp-p">הצהרה זו נערכת בהתאם לתקנות שוויון זכויות לאנשים עם מוגבלות (התאמות נגישות לשירות), תשע"ג-2013, ולתקן הישראלי 5568 (המבוסס על WCAG 2.0 ברמה AA).</p>

<h2 class="lp-h2">2. רמת הנגישות הנוכחית</h2>
<p class="lp-p">האתר נבנה על פלטפורמת Streamlit ומיישם <b>תאימות חלקית</b> לתקן WCAG 2.0 ברמה AA. להלן פירוט:</p>

<p class="lp-p"><b>✅ מה קיים:</b></p>
<ul class="lp-ul">
  <li>ניגודיות צבעים עומדת ברוב הממשק (יחס 4.5:1 לפחות)</li>
  <li>טקסטים הניתנים להגדלה עד 200% ללא אובדן תוכן</li>
  <li>שדות טופס עם תוויות (labels) מפורשות</li>
  <li>ניתן לנווט בחלק מהממשק באמצעות מקלדת</li>
  <li>שפת הדף מוגדרת (he) לתמיכה בקוראי מסך</li>
  <li>כותרות עמוד ברורות ומסודרות היררכית</li>
</ul>

<p class="lp-p"><b>⚠️ מגבלות ידועות (בטיפול):</b></p>
<ul class="lp-ul">
  <li>חלק מרכיבי ה-HTML המוטמעים (charts, ticker) עשויים לא להיות נגישים במלואם לקוראי מסך</li>
  <li>גרפים ותרשימים אינם כוללים תיאור טקסטואלי חלופי</li>
  <li>ממשק הצ'אט אינו אופטימלי לניווט מקלדת</li>
</ul>

<h2 class="lp-h2">3. תוכנית שיפור נגישות</h2>
<p class="lp-p">אנו פועלים לשיפור מתמיד. בתוכנית העבודה לשנת 2026:</p>
<ul class="lp-ul">
  <li>הוספת תיאורי alt לכלל רכיבי הגרפיקה</li>
  <li>שיפור ניווט מקלדת מלא לכל רכיבי האתר</li>
  <li>בדיקת ניגודיות מקיפה לכל צבעי הממשק</li>
  <li>בדיקת תאימות עם קוראי מסך (NVDA, VoiceOver)</li>
</ul>

<h2 class="lp-h2">4. פנייה בנושא נגישות</h2>
<p class="lp-p">נתקלתם בבעיית נגישות? נשמח לשמוע ולתקן.</p>
<p class="lp-p"><b>רכז הנגישות:</b> עדי אלבז<br>
<b>דואר אלקטרוני:</b> <a href="mailto:adi@nazil.info" style="color:#2B5CE8;">adi@nazil.info</a><br>
<b>כתובת:</b> הנוטר 7, חיפה</p>
<p class="lp-p">נשתדל לטפל בכל פנייה תוך <b>7 ימי עסקים</b>.</p>

<h2 class="lp-h2">5. אמצעי נגישות חיצוניים</h2>
<p class="lp-p">ניתן להשתמש בכלי הנגישות המובנים של מערכת ההפעלה:</p>
<ul class="lp-ul">
  <li><b>Windows:</b> Narrator, הגדלת תצוגה (Win + =)</li>
  <li><b>Mac:</b> VoiceOver (Cmd + F5), Zoom (Opt + Cmd + =)</li>
  <li><b>iOS/Android:</b> VoiceOver / TalkBack מובנים</li>
  <li><b>כלים חיצוניים:</b> NVDA (חינמי), JAWS</li>
</ul>

<div class="lp-warn">
  אם נתקלתם בחסם נגישות המונע מכם שימוש בשירות — צרו קשר ישיר ונסייע לכם לקבל את השירות בדרך חלופית נגישה.
</div>
""", unsafe_allow_html=True)
    _legal_footer()


# ─────────────────────────────────────────────────────────────────────────────
# URL ROUTING
# ─────────────────────────────────────────────────────────────────────────────
_page = st.query_params.get("page", "home")
if _page == "terms":
    _render_terms()
    st.stop()
elif _page == "privacy":
    _render_privacy()
    st.stop()
elif _page == "accessibility":
    _render_accessibility()
    st.stop()

# ═════════════════════════════════════════════════════════════════════════════
# FAQ DATABASE — 55 Q&As
# ═════════════════════════════════════════════════════════════════════════════
FAQ = [
    {"cat": "כללי", "q": "מה זה נזיל?", "a": "נזיל היא פלטפורמת טכנולוגיה פנסיונית שמנתחת את קרנות הפנסיה שלכם ועוזרת לשחרר הון עומד — בצורה חוקית, מהירה ומאובטחת."},
    {"cat": "כללי", "q": "למי מתאים השירות?", "a": "לכל אדם עם חסכונות פנסיוניים — שכירים, עצמאיים, ובעלי עסקים — שצוברים כסף בקרנות ומחפשים נזילות מיידית."},
    {"cat": "כללי", "q": "האם נזיל היא חברה ישראלית מורשית?", "a": "כן. נזיל פועלת בישראל תחת פיקוח רשות שוק ההון, ביטוח וחיסכון, ועומדת בכל דרישות הרגולציה."},
    {"cat": "כללי", "q": "כמה לקוחות כבר השתמשו בשירות?", "a": "מאות לקוחות מרחבי הארץ כבר שחררו הון פנסיוני דרך נזיל — עם היקף כולל של מעל ₪2.4 מיליארד שנותח."},
    {"cat": "כללי", "q": "האם אפשר לקבל ייעוץ ראשוני חינם?", "a": "בהחלט. הניתוח הראשוני — כולל העלאת קובץ מסלקה וקבלת תמונת מצב מלאה — הוא חינמי וללא התחייבות."},
    {"cat": "כללי", "q": "מה ההבדל בין נזיל ליועץ פנסיוני רגיל?", "a": "יועץ פנסיוני מתמקד בתכנון עתידי. נזיל מתמחה בזיהוי הזדמנויות נזילות קיימות ובמימוש ההון הנצבר — מהר יותר ובעלות שקופה."},
    {"cat": "כללי", "q": "האם נזיל מחליפה את יועץ הפנסיה שלי?", "a": "לא — נזיל משלימה את הייעוץ הפנסיוני הקיים. אנחנו ממליצים לפעול בתיאום עם יועץ מורשה."},
    {"cat": "כללי", "q": "האם צריך ידע פיננסי כדי להשתמש?", "a": "לא. הפלטפורמה מיועדת לכל אחד. המערכת מסבירה כל שלב בשפה פשוטה וברורה."},
    {"cat": "תהליך", "q": "מה זה קובץ מסלקה ואיך מורידים אותו?", "a": "קובץ מסלקה הוא דוח רשמי מהמסלקה הפנסיונית המרכזית המסכם את כל קרנות הפנסיה שלכם. מורידים אותו בחינם דרך האזור האישי בביטוח לאומי או דרך אתר המסלקה הפנסיונית."},
    {"cat": "תהליך", "q": "כמה זמן לוקח ניתוח המסמכים?", "a": "הניתוח האוטומטי מסתיים תוך פחות מ-24 שעות. לאחר מכן נציג ייצור קשר לשיחת ייעוץ אישית."},
    {"cat": "תהליך", "q": "מה קורה אחרי שמעלים את המסמכים?", "a": "המערכת מנתחת את כל הקרנות, מזהה הזדמנויות, ושולחת אליכם תכנית נזילות מפורטת עם המלצות."},
    {"cat": "תהליך", "q": "האם צריך להגיע לפגישה פיזית?", "a": "לא. כל התהליך מבוצע דיגיטלית — מהניתוח ועד החתימה. ניתן לקיים שיחת ייעוץ בוידאו או טלפון."},
    {"cat": "תהליך", "q": "כמה זמן עד שהכסף מגיע לחשבון?", "a": "ברוב המקרים הכסף מגיע לחשבון הבנק תוך 14 ימי עסקים מרגע החתימה על התכנית."},
    {"cat": "תהליך", "q": "האם צריך לפנות לגוף הפנסיוני בעצמי?", "a": "לא. נזיל מטפלת בכל התהליך מול גופי הפנסיה בשמכם — כולל הגשת הבקשות וליווי עד לשחרור הכסף."},
    {"cat": "תהליך", "q": "מה קורה אם יש מספר קרנות?", "a": "המערכת מנתחת את כל הקרנות במקביל ובונה תכנית אחת מאוחדת שממקסמת את הנזילות הכוללת."},
    {"cat": "תהליך", "q": "האם אפשר לעקוב אחרי הסטטוס?", "a": "כן. לאחר הצטרפות מקבלים גישה לפורטל אישי שמציג את סטטוס הטיפול בכל שלב."},
    {"cat": "תהליך", "q": "מה הפורמטים הנתמכים להעלאה?", "a": "המערכת תומכת בקבצי DAT ו-XML מהמסלקה הפנסיונית, וכן קבצי PDF של דוחות פנסיוניים."},
    {"cat": "כסף ונזילות", "q": "כמה כסף אני יכול לשחרר?", "a": "בממוצע לקוחות נזיל משחררים בין 30% ל-60% מסך החסכונות הפנסיוניים שלהם. הסכום המדויק תלוי בסוג הקרן, הוותק ותנאי החוזה."},
    {"cat": "כסף ונזילות", "q": "האם אני מקבל את כל הכסף בבת אחת?", "a": "תלוי בתכנית שנבנית עבורכם. ניתן לקבל כסף חד-פעמי, בתשלומים, או שילוב של השניים — לפי הצרכים שלכם."},
    {"cat": "כסף ונזילות", "q": "מה ההבדל בין הלוואה פנסיונית למשיכה מוקדמת?", "a": "הלוואה כנגד קרן פנסיה מאפשרת לקבל כסף מיידי מבלי למשוך את הקרן עצמה. משיכה מוקדמת היא פדיון הקרן בפועל. לכל אחת יתרונות ומשמעויות מס שונות."},
    {"cat": "כסף ונזילות", "q": "האם יש סכום מינימלי לשחרור?", "a": "כן, הסכום המינימלי לטיפול הוא ₪50,000 בחסכונות פנסיוניים."},
    {"cat": "כסף ונזילות", "q": "מה ממוצע שחרור ההון?", "a": "הממוצע עומד על כ-₪180,000 ללקוח. הטווח נע בין ₪50,000 למעל ₪1,000,000."},
    {"cat": "כסף ונזילות", "q": "האם הכסף חייב במס?", "a": "חלק מהסכומים כפופים למס. נזיל מבצעת חישוב מס מדויק ומשקפת את הסכום נטו שתקבלו לפני קבלת כל החלטה."},
    {"cat": "כסף ונזילות", "q": "האם ניתן לשחרר רק חלק מהקרן?", "a": "כן. ניתן לשחרר חלק מסוים מהקרן ולהשאיר את השאר פעיל לפנסיה. נזיל תבנה תכנית המותאמת לצרכים שלכם."},
    {"cat": "פנסיה וקרנות", "q": "האם שחרור הכסף פוגע בפנסיה העתידית?", "a": "תלוי בסוג הפעולה. נזיל תמיד תמליץ על הדרך שמשפיעה פחות על קצבת הפרישה, ותשקף את ההשפעה המדויקת לפני כל פעולה."},
    {"cat": "פנסיה וקרנות", "q": "אילו סוגי קרנות נזיל מטפלת בהן?", "a": "קרנות פנסיה חדשות, קרנות פנסיה ותיקות, ביטוח מנהלים, קופות גמל, קרנות השתלמות — כל סוגי החסכון הפנסיוני."},
    {"cat": "פנסיה וקרנות", "q": "האם קרן השתלמות כלולה?", "a": "כן. קרנות השתלמות שעברו 6 שנות ותק ניתנות למשיכה ללא עונש. גם לפני הנזילות ניתן לקחת הלוואה כנגדן."},
    {"cat": "פנסיה וקרנות", "q": "מה זה ביטוח מנהלים?", "a": "ביטוח מנהלים הוא מוצר חיסכון פנסיוני ישן שמציע קצבה מובטחת. לרוב יש בו רכיבי חיסכון ניתנים לשחרור חלקי."},
    {"cat": "פנסיה וקרנות", "q": "האם אפשר לשחרר כסף מקופת גמל לפני פרישה?", "a": "כן, בתנאים מסוימים — בהתאם לגיל, ותק, ומאפייני הקופה. נזיל תבדוק עבורכם את הזכאות המדויקת."},
    {"cat": "פנסיה וקרנות", "q": "מה ההבדל בין רכיב הפיצויים לרכיב הקצבה?", "a": "רכיב הפיצויים ניתן למשיכה בתנאים נוחים יותר. רכיב הקצבה מיועד לפנסיה ומשיכתו כרוכה במס גבוה יותר. נזיל ממקסמת את המשיכה מהפיצויים תחילה."},
    {"cat": "פנסיה וקרנות", "q": "האם תצטרכו לשנות את מסלול הקרן?", "a": "לא בהכרח. ברוב המקרים ניתן לשחרר הון מבלי לשנות את מסלול ההשקעה."},
    {"cat": "אבטחה ופרטיות", "q": "האם המידע הפיננסי שלי מאובטח?", "a": "כן. כל המידע מוצפן בתקן AES-256, מועבר דרך SSL, ומאוחסן בשרתים מאובטחים בישראל."},
    {"cat": "אבטחה ופרטיות", "q": "מה קורה עם הקבצים שמעלים?", "a": "הקבצים מנותחים אוטומטית ונמחקים לאחר שהניתוח הושלם. אנחנו לא שומרים עותקים של מסמכים אישיים."},
    {"cat": "אבטחה ופרטיות", "q": "מי יש לו גישה למידע שלי?", "a": "רק נציג הטיפול שהוקצה לכם ומנהל המערכת יש להם גישה. כל גישה מתועדת ומבוקרת."},
    {"cat": "אבטחה ופרטיות", "q": "האם הפרטים שלי נמכרים לצדדים שלישיים?", "a": "לא. נזיל לא מוכרת, לא משתפת ולא מעבירה פרטים אישיים לגורמים חיצוניים — בשום צורה."},
    {"cat": "אבטחה ופרטיות", "q": "האם נזיל עומדת בתקני ISO?", "a": "כן. נזיל פועלת לפי תקן ISO 27001 לניהול אבטחת מידע, ועומדת בדרישות ה-GDPR."},
    {"cat": "אבטחה ופרטיות", "q": "מה קורה אם אני רוצה מחיקת נתונים?", "a": "ניתן לבקש מחיקה מלאה של כל המידע שלכם בכל עת — פשוט פנו לשירות הלקוחות."},
    {"cat": "עלויות ותשלום", "q": "כמה עולה השירות?", "a": "השירות מבוסס על עמלת הצלחה בלבד — משלמים רק אם ורק כשהכסף מגיע לחשבונכם. אין עלות ראשונית."},
    {"cat": "עלויות ותשלום", "q": "כמה אחוז עמלה גובה נזיל?", "a": "שיעור העמלה מפורט ומוסכם מראש בחוזה שקוף, ומחושב כאחוז מסכום הנזילות שהושגה. אין עמלות נסתרות."},
    {"cat": "עלויות ותשלום", "q": "האם ייעוץ ראשוני הוא בתשלום?", "a": "לא. הייעוץ הראשוני, הניתוח, ותכנית הנזילות — הכל חינמי. משלמים רק על ביצוע בפועל."},
    {"cat": "עלויות ותשלום", "q": "האם יש עמלות נסתרות?", "a": "לא. כל העלויות מפורטות בחוזה השקוף לפני חתימה. אנחנו מתגאים בשקיפות מוחלטת."},
    {"cat": "עלויות ותשלום", "q": "מה קורה אם לא מרוצה?", "a": "אם לא הצלחנו לשחרר הון, לא תשלמו דבר. אנחנו עובדים על בסיס הצלחה בלבד."},
    {"cat": "עלויות ותשלום", "q": "מתי בדיוק משלמים את העמלה?", "a": "העמלה מנוכית ישירות מסכום הנזילות ברגע שהכסף מועבר — לפני שהוא מגיע לחשבונכם."},
    {"cat": "משפטי ורגולציה", "q": "האם הפעילות חוקית לחלוטין?", "a": "כן. כל הפעולות שנזיל מבצעת עומדות בחוק הפיקוח על שירותים פיננסיים, חוק הפנסיה ותקנות רשות שוק ההון."},
    {"cat": "משפטי ורגולציה", "q": "מי מפקח על נזיל?", "a": "נזיל פועלת תחת פיקוח רשות שוק ההון, ביטוח וחיסכון של מדינת ישראל."},
    {"cat": "משפטי ורגולציה", "q": "האם צריך לחתום על מסמכים?", "a": "כן. לפני כל פעולה תקבלו חוזה ברור לחתימה דיגיטלית. אין פעולה ללא הסכמה מלאה שלכם."},
    {"cat": "משפטי ורגולציה", "q": "האם ניתן לבטל את ההסכם?", "a": "כן. ניתן לבטל בכל שלב לפני ביצוע הפעולה ללא עלות. לאחר ביצוע — חלות הוראות החוזה."},
    {"cat": "משפטי ורגולציה", "q": "האם פעולה זו מדווחת לרשויות המס?", "a": "כן, בהתאם לחוק. נזיל מדווחת לרשויות המס ומספקת אישורים לצורך הגשת דוח שנתי."},
    {"cat": "משפטי ורגולציה", "q": "האם יש מגבלת גיל לשימוש?", "a": "הגיל המינימלי הוא 18. מגבלות מסוימות חלות על בני 60+ בגלל קרבה לגיל פרישה — נזיל תבדוק ותיידע."},
    {"cat": "משפטי ורגולציה", "q": "מה ההבדל בין שכיר לעצמאי?", "a": "לשכירים ולעצמאיים יש מסלולי נזילות שונים. עצמאיים לרוב נהנים מגמישות רבה יותר בתנאי המשיכה."},
    {"cat": "משפטי ורגולציה", "q": "האם פרישה מוקדמת פוגעת בזכויות?", "a": "זה תלוי בסוג הפעולה. נזיל תמיד משקפת את ההשפעה על הזכויות לפני ביצוע — ומוודאת שאתם מבינים את כל ההשלכות."},
    {"cat": "משפטי ורגולציה", "q": "האם העברה כפופה לחוק איסור הלבנת הון?", "a": "כן. כמו כל גוף פיננסי מורשה, נזיל מקיימת את כל חובות דיווח ואימות הנדרשות בחוק."},
    {"cat": "כסף ונזילות", "q": "האם ניתן להשתמש בכסף לכל מטרה?", "a": "כן. לאחר שהכסף מגיע לחשבון הבנק שלכם — הוא שלכם לחלוטין לכל מטרה שתחפצו."},
    {"cat": "תהליך", "q": "האם אפשר להתחיל ולהפסיק בכל שלב?", "a": "כן. עד לשלב החתימה על תכנית הנזילות ניתן לעצור את התהליך בכל עת ללא כל עלות."},
    # חילוץ ממעסיקים
    {"cat": "חילוץ ממעסיקים", "q": "מה זה חילוץ כספים ממעסיקים?", "a": "כספי פנסיה ופיצויים שהמעסיק שלכם הפריש אך מעולם לא הועברו — בגלל שכחה, רשלנות, פשיטת רגל או סגירת עסק. נזיל מאתרת ומחלצת כספים אלו גם ממעסיקים שאינם פעילים עוד."},
    {"cat": "חילוץ ממעסיקים", "q": "כמה כסף בממוצע כלוא אצל מעסיקים ישנים?", "a": "לפי נתוני רשות שוק ההון, מיליארדי שקלים שוכבים 'רדומים' בקרנות ממעסיקים קודמים. הממוצע ללקוח שמאתרים כספים כאלה עומד על עשרות אלפי שקלים."},
    {"cat": "חילוץ ממעסיקים", "q": "האם ניתן לחלץ גם ממעסיק שפשט רגל?", "a": "כן. גם במקרה של פשיטת רגל, הכספים שהופרשו לקרן הפנסיה מוגנים ושייכים לכם. נזיל מנוסה בהליכים מול קרנות ומפרקים להחזרת הכסף לידיכם."},
    {"cat": "חילוץ ממעסיקים", "q": "מה צריך כדי להתחיל תהליך חילוץ ממעסיק?", "a": "לרוב מספיקים תלוש שכר ישן, שם החברה ושנות העסקה. נזיל עושה את כל עבודת האיתור מולכם — פשוט מלאו טופס קצר ונחזור אליכם תוך 24 שעות."},
    # הלוואת גישור
    {"cat": "הלוואת גישור", "q": "מה זו הלוואת גישור מהפנסיה?", "a": "הלוואת גישור היא מימון מיידי שניתן כנגד כספי הפנסיה שלכם — ללא בנק, ללא ערבים, ללא בירוקרטיה. מושלמת לגישור על פערי נזילות זמניים: שיפוץ, עסקת נדל\"ן, חוב דחוף."},
    {"cat": "הלוואת גישור", "q": "כמה ניתן לקבל בהלוואת גישור?", "a": "ניתן לקבל עד 30% מהצבירה הפנסיונית שלכם כהלוואה, בכפוף לתנאי הקרן. בסכומים של עשרות ועד מאות אלפי שקלים."},
    {"cat": "הלוואת גישור", "q": "מה הריבית על הלוואת גישור פנסיונית?", "a": "הריבית על הלוואות מקרן פנסיה נקבעת לפי תקנות הקרן ולרוב נמוכה משמעותית מהלוואת בנק. חלק מהקרנות מציעות הלוואות בריבית פריים פלוס 0.5% בלבד."},
    {"cat": "הלוואת גישור", "q": "האם הלוואת גישור פוגעת בפנסיה שלי?", "a": "הפנסיה ממשיכה לצבור תשואה כרגיל. ההלוואה מנוכית מהצבירה ומוחזרת בתשלומים — ובסיום ההחזרה, הצבירה חוזרת לרמתה המלאה."},
    {"cat": "הלוואת גישור", "q": "כמה זמן לוקח לקבל הלוואת גישור?", "a": "לאחר הגשת הבקשה ואישורה, הכסף מגיע בדרך כלל תוך 7-14 ימי עסקים — מהיר משמעותית מהלוואה בנקאית."},
]

FAQ_CATS = ["הכל"] + sorted(set(f["cat"] for f in FAQ))

# ═════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS — LIGHT MODE PROFESSIONAL PALETTE
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;800;900&family=Montserrat:wght@700;800;900&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;}
html,body{font-family:'Heebo',-apple-system,sans-serif;background:#F7F8FF;color:#1B2559;direction:rtl;overflow-x:hidden;}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"],.stDeployButton{display:none!important;}
[data-testid="stSidebar"]{display:none!important;}
.block-container{padding:0!important;max-width:100%!important;}
[data-testid="stAppViewContainer"],section.main{background:#F7F8FF!important;padding:0!important;}
[data-testid="stVerticalBlock"]{gap:0!important;}
:root{
  --pri:#2B5CE8;--pri-d:#1A3FCC;--pri-l:#EEF2FF;
  --acc:#00B894;--acc-l:#E6FAF7;
  --bg:#FFFFFF;--bg-s:#F7F8FF;--bg-c:#F1F3FB;
  --t1:#1B2559;--t2:#6B7A99;--t3:#A8B2CC;
  --bd:#E4E7F2;--bd-p:rgba(43,92,232,0.18);
  --sh:0 4px 24px rgba(43,92,232,0.08);--sh-h:0 12px 40px rgba(43,92,232,0.15);
  --r:16px;
}
.grad{background:linear-gradient(135deg,var(--pri),var(--acc));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.lf-section{max-width:1200px;margin:0 auto;padding:5rem 2.5rem;direction:rtl;}
.lf-divider{height:1px;background:var(--bd);}
.section-chip{display:inline-block;font-size:.72rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--pri);background:var(--pri-l);border:1px solid var(--bd-p);border-radius:50px;padding:.3rem .9rem;margin-bottom:1rem;}
.section-h{font-family:'Montserrat',sans-serif;font-size:clamp(1.8rem,3vw,2.6rem);font-weight:800;color:var(--t1);line-height:1.25;margin-bottom:.85rem;direction:rtl;text-align:center;}
.section-p{font-size:1.05rem;color:var(--t2);line-height:1.78;direction:rtl;text-align:center;}
.card{background:var(--bg);border:1px solid var(--bd);border-radius:var(--r);padding:2rem 1.5rem;transition:all .25s;direction:rtl;}
.card:hover{border-color:var(--bd-p);box-shadow:var(--sh-h);transform:translateY(-3px);}
.stat-card{background:var(--bg);border:1px solid var(--bd);border-radius:var(--r);padding:2rem 1.5rem;text-align:center;transition:all .25s;}
.stat-card:hover{border-color:var(--bd-p);box-shadow:var(--sh-h);transform:translateY(-3px);}
.stat-num{font-family:'Montserrat',sans-serif;font-size:2.4rem;font-weight:900;background:linear-gradient(135deg,var(--pri),var(--acc));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;display:block;margin-bottom:.35rem;}
.stat-lbl{font-size:.88rem;color:var(--t2);}
.step-card{background:var(--bg);border:1px solid var(--bd);border-radius:var(--r);padding:2.5rem 1.8rem;text-align:center;transition:all .25s;height:100%;}
.step-card:hover{border-color:var(--bd-p);box-shadow:var(--sh-h);transform:translateY(-3px);}
.step-num{display:inline-flex;align-items:center;justify-content:center;width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,var(--pri),var(--acc));font-size:1.1rem;font-weight:800;color:#fff;margin-bottom:1.1rem;box-shadow:0 4px 20px rgba(43,92,232,.3);}
.step-ico{font-size:2rem;margin-bottom:.7rem;display:block;}
.step-ttl{font-family:'Montserrat',sans-serif;font-size:1.05rem;font-weight:700;color:var(--t1);margin-bottom:.5rem;}
.step-dsc{font-size:.87rem;color:var(--t2);line-height:1.65;}
.delta-row{display:flex;gap:1rem;flex-wrap:wrap;direction:rtl;margin-top:1.2rem;}
.delta-card{flex:1;min-width:130px;background:var(--bg);border:1px solid var(--bd);border-radius:14px;padding:1.1rem 1rem;text-align:center;}
.delta-card.hi{border-color:var(--bd-p);background:var(--pri-l);}
.delta-val{font-family:'Montserrat',sans-serif;font-size:1.4rem;font-weight:800;color:var(--pri);}
.delta-val.neg{color:var(--t3);}
.delta-lbl{font-size:.75rem;color:var(--t2);margin-top:.2rem;}
.trust-badge{display:inline-flex;align-items:center;gap:.4rem;background:var(--bg);border:1px solid var(--bd);border-radius:50px;padding:.42rem 1rem;font-size:.8rem;color:var(--t2);transition:all .2s;white-space:nowrap;}
.trust-badge:hover{background:var(--pri-l);border-color:var(--bd-p);color:var(--pri);}
.badge-row{display:flex;flex-wrap:wrap;gap:.7rem;direction:rtl;}
.form-wrap{background:var(--pri-l);border:1px solid var(--bd-p);border-radius:20px;padding:2.5rem;margin-top:1.5rem;direction:rtl;}
.form-title{font-family:'Montserrat',sans-serif;font-size:1.15rem;font-weight:800;color:var(--t1);margin-bottom:1.1rem;}
.msg-ok{background:var(--acc-l);border:1px solid var(--acc);border-radius:14px;padding:1.3rem 2rem;text-align:center;color:#057a62;font-weight:600;font-size:1rem;direction:rtl;margin-top:1rem;}
.team-card{background:var(--bg);border:1px solid var(--bd);border-radius:var(--r);padding:2rem 1.5rem;text-align:center;transition:all .25s;}
.team-card:hover{border-color:var(--bd-p);box-shadow:var(--sh-h);transform:translateY(-3px);}
.team-avatar{width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg,var(--pri-l),var(--acc-l));border:3px solid var(--bd-p);margin:0 auto 1rem;display:flex;align-items:center;justify-content:center;font-size:2rem;}
.team-name{font-family:'Montserrat',sans-serif;font-size:1rem;font-weight:800;color:var(--t1);margin-bottom:.25rem;}
.team-role{font-size:.82rem;color:var(--pri);font-weight:600;margin-bottom:.5rem;}
.team-bio{font-size:.8rem;color:var(--t2);line-height:1.6;}
.ai-bubble{position:fixed;bottom:2rem;right:2rem;z-index:9999;cursor:pointer;}
.ai-bubble-btn{width:64px;height:64px;border-radius:50%;background:linear-gradient(135deg,var(--pri),var(--acc));display:flex;align-items:center;justify-content:center;font-size:1.7rem;box-shadow:0 4px 24px rgba(43,92,232,.4);animation:bubble-float 4s ease-in-out infinite;transition:transform .2s;border:none;}
.ai-bubble-btn:hover{transform:scale(1.1);}
.ai-bubble-tip{position:absolute;bottom:72px;right:0;background:var(--bg);border:1.5px solid var(--bd-p);border-radius:14px;padding:.75rem 1.1rem;white-space:nowrap;font-size:.82rem;color:var(--t1);opacity:0;pointer-events:none;transition:opacity .3s;direction:rtl;box-shadow:var(--sh);font-weight:600;}
.ai-bubble:hover .ai-bubble-tip{opacity:1;}
.ai-pulse{position:absolute;top:-3px;right:-3px;width:14px;height:14px;border-radius:50%;background:#f43f5e;border:2px solid var(--bg-s);animation:blink 1.5s ease-in-out infinite;}
.chat-msg-bot{display:flex;gap:.7rem;align-items:flex-start;direction:rtl;margin-bottom:.8rem;}
.chat-msg-user{display:flex;gap:.7rem;align-items:flex-start;flex-direction:row-reverse;direction:rtl;margin-bottom:.8rem;}
.chat-av{width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.9rem;flex-shrink:0;}
.chat-av.bot{background:linear-gradient(135deg,var(--pri),var(--acc));}
.chat-av.usr{background:var(--bg-c);border:1.5px solid var(--bd);}
.chat-bbl-bot{background:var(--bg);border:1.5px solid var(--bd);border-radius:4px 16px 16px 16px;padding:.8rem 1.1rem;max-width:80%;font-size:.9rem;color:var(--t1);line-height:1.65;box-shadow:var(--sh);}
.chat-bbl-usr{background:var(--pri-l);border:1.5px solid var(--bd-p);border-radius:16px 4px 16px 16px;padding:.8rem 1.1rem;max-width:80%;font-size:.9rem;color:var(--pri);line-height:1.65;font-weight:500;}
[data-testid="stTextInput"] label,[data-testid="stTextInput"]>label>div{color:var(--t2)!important;font-size:.88rem!important;direction:rtl!important;text-align:right!important;font-family:'Heebo',sans-serif!important;}
[data-testid="stTextInput"] input{background:var(--bg)!important;border:1.5px solid var(--bd)!important;border-radius:10px!important;color:var(--t1)!important;direction:rtl!important;text-align:right!important;font-family:'Heebo',sans-serif!important;}
[data-testid="stTextInput"] input:focus{border-color:var(--pri)!important;box-shadow:0 0 0 3px rgba(43,92,232,.12)!important;}
[data-testid="stFileUploaderDropzone"]{background:var(--bg)!important;border:2px dashed var(--bd-p)!important;border-radius:16px!important;transition:all .3s!important;}
[data-testid="stFileUploaderDropzone"]:hover{background:var(--pri-l)!important;border-color:var(--pri)!important;}
[data-testid="stFileUploaderDropzone"] p,[data-testid="stFileUploaderDropzone"] span{color:var(--t2)!important;direction:rtl!important;font-family:'Heebo',sans-serif!important;}
[data-testid="stSlider"]{direction:ltr!important;}
[data-testid="stSlider"]>label{direction:rtl!important;text-align:right!important;}
[data-testid="stSlider"]>label>div p{color:var(--t2)!important;font-size:.9rem!important;font-family:'Heebo',sans-serif!important;}
.stButton>button{background:linear-gradient(135deg,var(--pri),var(--pri-d))!important;color:#fff!important;border:none!important;border-radius:50px!important;font-weight:700!important;padding:.7rem 2rem!important;font-size:.95rem!important;font-family:'Heebo',sans-serif!important;transition:all .2s!important;box-shadow:0 4px 16px rgba(43,92,232,.3)!important;}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 28px rgba(43,92,232,.4)!important;}
[data-testid="stCheckbox"] label span{color:var(--t2)!important;font-size:.88rem!important;font-family:'Heebo',sans-serif!important;}
[data-testid="column"]{padding:0.4rem!important;}
.stMarkdown p{direction:rtl;font-family:'Heebo',sans-serif;color:var(--t2);}
.stSuccess{background:var(--acc-l)!important;border:1px solid var(--acc)!important;color:#057a62!important;direction:rtl!important;border-radius:12px!important;}
.stError{direction:rtl!important;border-radius:12px!important;}
.svc-card{background:var(--bg);border:1.5px solid var(--bd);border-radius:var(--r);padding:2rem 1.6rem;transition:all .28s;direction:rtl;height:100%;display:flex;flex-direction:column;gap:.6rem;}
.svc-card:hover{border-color:var(--bd-p);box-shadow:var(--sh-h);transform:translateY(-4px);}
.svc-ico{font-size:2.1rem;line-height:1;}
.svc-ttl{font-family:'Montserrat',sans-serif;font-size:1rem;font-weight:800;color:var(--t1);}
.svc-dsc{font-size:.87rem;color:var(--t2);line-height:1.7;flex:1;}
.svc-tag{display:inline-block;font-size:.68rem;font-weight:700;letter-spacing:.8px;text-transform:uppercase;color:var(--acc);background:var(--acc-l);border-radius:50px;padding:.2rem .7rem;margin-top:.3rem;}
@keyframes fadeUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
@keyframes bubble-float{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
.fade-up,.fade-up-1,.fade-up-2,.fade-up-3,.fade-up-4{opacity:0;transform:translateY(22px);transition:opacity .6s ease,transform .6s ease;}
.fade-up.vis{opacity:1;transform:translateY(0);}
.fade-up-1.vis{opacity:1;transform:translateY(0);transition-delay:.1s;}
.fade-up-2.vis{opacity:1;transform:translateY(0);transition-delay:.2s;}
.fade-up-3.vis{opacity:1;transform:translateY(0);transition-delay:.3s;}
.fade-up-4.vis{opacity:1;transform:translateY(0);transition-delay:.4s;}
</style>
""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# FLOATING AI BUBBLE
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("""
<a href="#lf-ai" style="text-decoration:none;">
  <div class="ai-bubble">
    <div class="ai-bubble-btn">🤖</div>
    <div class="ai-pulse"></div>
    <div class="ai-bubble-tip">שאלות? אנחנו כאן ←</div>
  </div>
</a>
""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# NAVBAR
# ═════════════════════════════════════════════════════════════════════════════
components.html("""
<!DOCTYPE html><html dir="rtl" lang="he"><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Heebo:wght@500;700;800&family=Montserrat:wght@800;900&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:#fff;direction:rtl;font-family:'Heebo',sans-serif;}
nav{position:sticky;top:0;z-index:100;background:rgba(255,255,255,0.93);backdrop-filter:blur(16px);border-bottom:1px solid #E4E7F2;padding:.85rem 2.5rem;display:flex;align-items:center;justify-content:space-between;}
.logo{display:flex;align-items:center;gap:.65rem;text-decoration:none;}
.logo-text{font-family:'Montserrat',sans-serif;font-size:1.3rem;font-weight:900;background:linear-gradient(135deg,#2B5CE8,#00B894);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.logo-sub{font-size:.64rem;color:#A8B2CC;font-weight:500;margin-top:-3px;}
.links{display:flex;align-items:center;gap:1.8rem;}
.links a{font-size:.87rem;color:#6B7A99;text-decoration:none;font-weight:500;transition:color .2s;}
.links a:hover{color:#2B5CE8;}
.cta{background:linear-gradient(135deg,#2B5CE8,#1A3FCC);color:#fff!important;padding:.48rem 1.4rem;border-radius:50px;font-weight:700!important;font-size:.87rem;box-shadow:0 4px 14px rgba(43,92,232,.3);transition:all .2s;}
.cta:hover{transform:translateY(-1px);box-shadow:0 6px 22px rgba(43,92,232,.4)!important;}
</style></head><body>
<nav>
  <a class="logo" href="#">
    <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
      <defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#2B5CE8"/><stop offset="100%" stop-color="#00B894"/></linearGradient></defs>
      <circle cx="18" cy="18" r="18" fill="url(#lg)" opacity=".1"/>
      <path d="M18 5 C18 5,25 13,25 20 C25 24.4 21.9 28 18 28 C14.1 28 11 24.4 11 20 C11 13,18 5,18 5Z" fill="url(#lg)"/>
      <path d="M14 20 Q18 24 22 20" stroke="white" stroke-width="1.5" fill="none" stroke-linecap="round" opacity=".8"/>
    </svg>
    <div><div class="logo-text">נזיל</div><div class="logo-sub">LiquiFund</div></div>
  </a>
  <div class="links">
    <a href="#" onclick="window.parent.document.getElementById('lf-services').scrollIntoView({behavior:'smooth'});return false;">השירותים שלנו</a>
    <a href="#" onclick="window.parent.document.getElementById('lf-how').scrollIntoView({behavior:'smooth'});return false;">איך זה עובד</a>
    <a href="#" onclick="window.parent.document.getElementById('lf-calc').scrollIntoView({behavior:'smooth'});return false;">מחשבון</a>
    <a href="#" onclick="window.parent.document.getElementById('lf-faq').scrollIntoView({behavior:'smooth'});return false;">שאלות</a>
    <a href="#" onclick="window.parent.document.getElementById('lf-team').scrollIntoView({behavior:'smooth'});return false;">הצוות</a>
    <a href="#" class="cta" onclick="window.parent.document.getElementById('lf-upload').scrollIntoView({behavior:'smooth'});return false;">קבלו ניתוח חינם</a>
  </div>
</nav>
</body></html>
""", height=64, scrolling=False)

# ═════════════════════════════════════════════════════════════════════════════
# HERO
# ═════════════════════════════════════════════════════════════════════════════
components.html("""
<!DOCTYPE html><html dir="rtl" lang="he"><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;600;700&family=Montserrat:wght@800;900&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:#F7F8FF;direction:rtl;font-family:'Heebo',sans-serif;overflow:hidden;}
.hero{min-height:90vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:4rem 2rem 5rem;text-align:center;position:relative;overflow:hidden;}
.bg{position:absolute;inset:0;background:linear-gradient(160deg,#EEF2FF 0%,#F7F8FF 45%,#E6FAF7 100%);}
.shape{position:absolute;border-radius:50%;pointer-events:none;}
.s1{width:480px;height:480px;background:radial-gradient(circle,rgba(43,92,232,.09) 0%,transparent 70%);top:-120px;right:-80px;animation:drift 12s ease-in-out infinite;}
.s2{width:380px;height:380px;background:radial-gradient(circle,rgba(0,184,148,.07) 0%,transparent 70%);bottom:-50px;left:-60px;animation:drift 12s ease-in-out infinite reverse;}
.content{position:relative;z-index:2;max-width:800px;display:flex;flex-direction:column;align-items:center;gap:1.6rem;}
.chip{display:inline-flex;align-items:center;gap:.4rem;background:rgba(43,92,232,.08);border:1.5px solid rgba(43,92,232,.18);border-radius:50px;padding:.32rem .95rem;font-size:.77rem;font-weight:700;color:#2B5CE8;animation:fadeUp .5s ease both;}
h1{font-family:'Montserrat',sans-serif;font-size:clamp(2.1rem,5.5vw,3.7rem);font-weight:900;line-height:1.17;color:#1B2559;animation:fadeUp .6s .1s ease both;}
.acc{background:linear-gradient(135deg,#2B5CE8,#00B894);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.sub{font-size:clamp(.93rem,2.1vw,1.12rem);color:#6B7A99;line-height:1.8;max-width:560px;animation:fadeUp .6s .2s ease both;}
.video-card{width:100%;max-width:600px;aspect-ratio:16/9;background:#fff;border:1.5px solid #E4E7F2;border-radius:20px;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:.9rem;position:relative;overflow:hidden;cursor:pointer;animation:fadeUp .6s .3s ease both;transition:all .3s;box-shadow:0 8px 40px rgba(43,92,232,.1);}
.video-card:hover{border-color:rgba(43,92,232,.3);box-shadow:0 16px 60px rgba(43,92,232,.16);}
.vc-bg{position:absolute;inset:0;background:linear-gradient(135deg,rgba(43,92,232,.03),rgba(0,184,148,.03));}
.play{width:66px;height:66px;border-radius:50%;background:linear-gradient(135deg,#2B5CE8,#00B894);display:flex;align-items:center;justify-content:center;box-shadow:0 0 0 0 rgba(43,92,232,.4);animation:pulse 2.5s ease-in-out infinite;position:relative;z-index:1;font-size:1.5rem;padding-left:4px;}
.vlbl{font-size:.87rem;color:#6B7A99;position:relative;z-index:1;}
.vlbl b{color:#2B5CE8;}
.vc-corner{position:absolute;top:.85rem;right:.85rem;z-index:1;background:rgba(43,92,232,.08);border:1px solid rgba(43,92,232,.18);border-radius:8px;padding:.24rem .62rem;font-size:.69rem;color:#2B5CE8;font-weight:700;display:flex;align-items:center;gap:.28rem;}
.dot{width:6px;height:6px;border-radius:50%;background:#f43f5e;animation:blink 1.5s infinite;}
.ctas{display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;animation:fadeUp .6s .4s ease both;}
.bp{display:inline-flex;align-items:center;gap:.5rem;background:linear-gradient(135deg,#2B5CE8,#1A3FCC);color:#fff;font-family:'Heebo',sans-serif;font-weight:700;font-size:.98rem;padding:.83rem 2.1rem;border-radius:50px;cursor:pointer;box-shadow:0 4px 22px rgba(43,92,232,.35);transition:transform .2s,box-shadow .2s;border:none;white-space:nowrap;}
.bp:hover{transform:translateY(-3px);box-shadow:0 8px 34px rgba(43,92,232,.5);}
.bs{display:inline-flex;align-items:center;gap:.5rem;background:#fff;border:1.5px solid #E4E7F2;color:#1B2559;font-family:'Heebo',sans-serif;font-weight:600;font-size:.98rem;padding:.83rem 1.9rem;border-radius:50px;cursor:pointer;transition:all .2s;white-space:nowrap;}
.bs:hover{border-color:rgba(43,92,232,.3);background:#EEF2FF;color:#2B5CE8;}
.trust-line{display:flex;align-items:center;gap:1.5rem;justify-content:center;flex-wrap:wrap;animation:fadeUp .6s .5s ease both;}
.tl{display:flex;align-items:center;gap:.38rem;font-size:.79rem;color:#A8B2CC;}
.tl b{color:#6B7A99;font-weight:600;}
@keyframes fadeUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
@keyframes drift{0%,100%{transform:translateY(0) scale(1)}50%{transform:translateY(-14px) scale(1.02)}}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(43,92,232,.5)}70%{box-shadow:0 0 0 18px rgba(43,92,232,0)}100%{box-shadow:0 0 0 0 rgba(43,92,232,0)}}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
</style></head><body>
<div class="hero">
  <div class="bg"></div>
  <div class="shape s1"></div><div class="shape s2"></div>
  <div class="content">
    <div class="chip">💧 פלטפורמת הנזילות הפנסיונית המובילה בישראל</div>
    <h1>הכסף שלכם <span class="acc">כלוא בפנסיה</span>.<br>הגיע הזמן לשחרר אותו.</h1>
    <p class="sub">ניתוח אוטומטי של קרנות הפנסיה, סקירת אפשרויות הנזילות שלכם,<br>ופתרונות מימון — בפלטפורמה אחת שקופה ומאובטחת.</p>
    <div class="video-card">
      <div class="vc-bg"></div>
      <div class="vc-corner"><div class="dot"></div> בקרוב</div>
      <div class="play">▶</div>
      <div class="vlbl">הכירו את נזיל — <b>2 דקות שיסבירו לכם את הפנסיה שלכם</b></div>
    </div>
    <div class="ctas">
      <button class="bp" onclick="window.parent.document.getElementById('lf-calc').scrollIntoView({behavior:'smooth'})">← בדקו כמה כסף כלוא אצלכם</button>
      <button class="bs" onclick="window.parent.document.getElementById('lf-upload').scrollIntoView({behavior:'smooth'})">📁 העלו קובץ מסלקה חינם</button>
    </div>
    <div class="trust-line">
      <div class="tl">✅ <b>ללא עלות ראשונית</b></div>
      <div class="tl">🔒 <b>אבטחה בנקאית</b></div>
      <div class="tl">⚖️ <b>פיקוח רשות שוק ההון</b></div>
      <div class="tl">⚡ <b>ניתוח תוך 24 שעות</b></div>
    </div>
  </div>
</div>
</body></html>
""", height=720, scrolling=False)

# ═════════════════════════════════════════════════════════════════════════════
# STATS
# ═════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="lf-divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="lf-section" style="padding:3rem 2.5rem;">', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
for col, num, lbl, d in [(c1,"₪2.4 מיליארד","הון שנותח עד היום","fade-up"),(c2,"94%","שביעות רצון לקוחות","fade-up-1"),(c3,"14 יום","בממוצע מניתוח לפגישה","fade-up-2")]:
    with col:
        st.markdown(f'<div class="stat-card {d}"><span class="stat-num">{num}</span><span class="stat-lbl">{lbl}</span></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Scroll observer: triggers .vis on all .fade-up elements ──────────────────
components.html("""
<script>
(function(){
  var par = window.parent.document;
  var obs = new IntersectionObserver(function(entries){
    entries.forEach(function(e){
      if(e.isIntersecting){
        e.target.classList.add('vis');
        obs.unobserve(e.target);
      }
    });
  },{threshold:0.12});
  function init(){
    par.querySelectorAll('.fade-up,.fade-up-1,.fade-up-2,.fade-up-3,.fade-up-4').forEach(function(el){
      obs.observe(el);
    });
  }
  if(par.readyState==='complete'){ init(); } else { par.addEventListener('load', init); }
  setTimeout(init, 800);
})();
</script>
""", height=0)

# ── Social proof marquee ──────────────────────────────────────────────────────
components.html("""
<!DOCTYPE html><html dir="rtl"><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Heebo:wght@500;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:#1B2559;overflow:hidden;direction:ltr;font-family:'Heebo',sans-serif;}
.ticker-wrap{width:100%;padding:.85rem 0;overflow:hidden;position:relative;}
.ticker-wrap::before,.ticker-wrap::after{content:'';position:absolute;top:0;width:120px;height:100%;z-index:2;pointer-events:none;}
.ticker-wrap::before{left:0;background:linear-gradient(to right,#1B2559,transparent);}
.ticker-wrap::after{right:0;background:linear-gradient(to left,#1B2559,transparent);}
.ticker{display:flex;gap:0;animation:ticker 40s linear infinite;width:max-content;}
.ticker:hover{animation-play-state:paused;}
.item{display:flex;align-items:center;gap:.55rem;padding:0 2.5rem;white-space:nowrap;font-size:.84rem;font-weight:500;color:rgba(255,255,255,.75);border-right:1px solid rgba(255,255,255,.1);}
.item:last-child{border-right:none;}
.item b{color:#fff;font-weight:700;}
.dot{width:7px;height:7px;border-radius:50%;background:#00B894;flex-shrink:0;}
@keyframes ticker{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
</style></head><body>
<div class="ticker-wrap">
  <div class="ticker">
    <div class="item"><div class="dot"></div> <b>₪2.4 מיליארד</b> הון שנותח</div>
    <div class="item"><div class="dot"></div> <b>400+ לקוחות</b> שחררו הון</div>
    <div class="item"><div class="dot"></div> ממוצע <b>₪180,000</b> לאדם</div>
    <div class="item"><div class="dot"></div> <b>94%</b> שביעות רצון</div>
    <div class="item"><div class="dot"></div> בממוצע <b>14 יום</b> לפגישת ייעוץ</div>
    <div class="item"><div class="dot"></div> <b>ללא עלות</b> ראשונית</div>
    <div class="item"><div class="dot"></div> <b>פיקוח</b> רשות שוק ההון</div>
    <div class="item"><div class="dot"></div> <b>AES-256</b> הצפנה</div>
    <div class="item"><div class="dot"></div> <b>ISO 27001</b> אבטחה</div>
    <div class="item"><div class="dot"></div> ניתוח תוך <b>24 שעות</b></div>
    <!-- duplicate for seamless loop -->
    <div class="item"><div class="dot"></div> <b>₪2.4 מיליארד</b> הון שנותח</div>
    <div class="item"><div class="dot"></div> <b>400+ לקוחות</b> שחררו הון</div>
    <div class="item"><div class="dot"></div> ממוצע <b>₪180,000</b> לאדם</div>
    <div class="item"><div class="dot"></div> <b>94%</b> שביעות רצון</div>
    <div class="item"><div class="dot"></div> בממוצע <b>14 יום</b> לפגישת ייעוץ</div>
    <div class="item"><div class="dot"></div> <b>ללא עלות</b> ראשונית</div>
    <div class="item"><div class="dot"></div> <b>פיקוח</b> רשות שוק ההון</div>
    <div class="item"><div class="dot"></div> <b>AES-256</b> הצפנה</div>
    <div class="item"><div class="dot"></div> <b>ISO 27001</b> אבטחה</div>
    <div class="item"><div class="dot"></div> ניתוח תוך <b>24 שעות</b></div>
  </div>
</div>
</body></html>
""", height=52, scrolling=False)

# ═════════════════════════════════════════════════════════════════════════════
# SERVICES
# ═════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="lf-divider"></div><div id="lf-services"></div>', unsafe_allow_html=True)
st.markdown('<div class="lf-section">', unsafe_allow_html=True)
st.markdown('<div style="text-align:center;margin-bottom:3rem;"><div class="section-chip fade-up">השירותים שלנו</div><h2 class="section-h fade-up-1">המעטפת המלאה לנזילות פנסיונית</h2><p class="section-p fade-up-2" style="max-width:560px;margin:0 auto;">מחילוץ כספים ממעסיקים ישנים ועד הלוואות גישור — כל מה שצריך כדי שהכסף שלכם יעבוד בשבילכם.</p></div>', unsafe_allow_html=True)
sv1, sv2, sv3 = st.columns(3)
sv4, sv5, sv6 = st.columns(3)
for col, ico, ttl, dsc, tag, d in [
    (sv1, "💰", "ניתוח כספים פנסיוניים",
     "ניתוח מלא של קרנות הפנסיה, קופות גמל וביטוחי מנהלים — וסקירת הכספים הנזילים הקיימים לפי תנאי הקרן והחוק.",
     "שירות מרכזי", "fade-up"),
    (sv2, "🏭", "איתור כספים ממעסיקים",
     "איתור כספי פנסיה ופיצויים שנשארו אצל מעסיקים קודמים — כולל חברות שנסגרו. הכסף קיים, צריך לדעת לאתר אותו.",
     "פופולרי", "fade-up-1"),
    (sv3, "🌉", "הלוואת גישור מהפנסיה",
     "מידע ולווי בנושא מימון כנגד חסכונות פנסיה — בתיאום עם הקרן הרלוונטית ובהתאם לתנאיה. כפוף לאישור הקרן.",
     "כפוף לתנאי הקרן", "fade-up-2"),
    (sv4, "🔍", "ניתוח מסלקה פנסיונית",
     "קריאה ועיבוד אוטומטי של קובץ המסלקה — תמונת מצב של כל הנכסים הפנסיוניים שלכם במקום אחד, כולל דמי ניהול.",
     "AI אוטומטי", "fade-up-3"),
    (sv5, "📋", "סקירת אפשרויות נזילות",
     "הצגת אפשרויות הנזילות הקיימות לכם לפי הנתונים — עם הסבר ברור על כל מסלול. ההחלטה הסופית תמיד שלכם.",
     "ליווי אישי", "fade-up-4"),
    (sv6, "🛡️", "ליווי מול גופי פנסיה",
     "סיוע בתהליכי הגשה ותיאום מול קרנות פנסיה, חברות ביטוח וקופות גמל — ליווי בירוקרטי צעד אחר צעד.",
     "ליווי מלא", "fade-up"),
]:
    with col:
        st.markdown(f'<div class="svc-card {d}"><div class="svc-ico">{ico}</div><div class="svc-ttl">{ttl}</div><div class="svc-dsc">{dsc}</div><span class="svc-tag">{tag}</span></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# HOW IT WORKS
# ═════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="lf-divider"></div><div id="lf-how"></div>', unsafe_allow_html=True)
st.markdown('<div class="lf-section">', unsafe_allow_html=True)
st.markdown('<div style="text-align:center;margin-bottom:3rem;"><div class="section-chip fade-up">התהליך</div><h2 class="section-h fade-up-1" style="text-align:center;">מסמך אחד. 3 צעדים. תמונת מצב מלאה.</h2><p class="section-p fade-up-2" style="text-align:center;max-width:520px;margin:0 auto;">הטכנולוגיה שלנו מנתחת את כל הקרנות שלכם ומציגה סקירה אישית מותאמת — מהר, פשוט, שקוף.</p></div>', unsafe_allow_html=True)
s1, s2, s3 = st.columns(3)
for col, num, ico, ttl, dsc, d in [(s1,"1","📁","העלו מסמכים","העלו את קובץ המסלקה הפנסיונית שלכם בצורה מאובטחת ומוצפנת. תומך DAT, XML ו-PDF.","fade-up"),(s2,"2","🤖","ניתוח AI מלא","המערכת מנתחת את כל הקרנות, מציגה תמונת מצב ומסבירה את האפשרויות הקיימות תוך 24 שעות.","fade-up-1"),(s3,"3","📞","שיחת ייעוץ חינם","מקבלים סקירה מלאה ושיחה עם מומחה — שיעזור לכם להחליט מה נכון עבורכם.","fade-up-2")]:
    with col:
        st.markdown(f'<div class="step-card {d}"><div><span class="step-num">{num}</span></div><span class="step-ico">{ico}</span><div class="step-ttl">{ttl}</div><div class="step-dsc">{dsc}</div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# CALCULATOR
# ═════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="lf-divider"></div><div id="lf-calc"></div>', unsafe_allow_html=True)
st.markdown('<div class="lf-section">', unsafe_allow_html=True)
st.markdown('<div style="margin-bottom:2.5rem;"><div class="section-chip fade-up">סימולטור נזילות</div><h2 class="section-h fade-up-1">כמה כסף <span class="grad">כלוא</span> אצלכם?</h2><p class="section-p fade-up-2">הזיזו את הסליידר לסימולציה להמחשה בלבד — אינה מהווה ייעוץ פנסיוני.</p></div>', unsafe_allow_html=True)

amount = st.slider("סכום כולל בקרנות פנסיה (₪)", min_value=50_000, max_value=2_000_000, value=350_000, step=10_000, format="₪%d")
YEARS = 10
locked_vals = [round(amount * (1.045)**y) for y in range(YEARS+1)]
free_vals   = [round(amount * (1.095)**y) for y in range(YEARS+1)]
gain_delta  = free_vals[-1] - locked_vals[-1]
gain_pct    = round((gain_delta / locked_vals[-1]) * 100)

def _fmt(n):
    return f"₪{n/1_000_000:.2f}מ׳" if n >= 1_000_000 else f"₪{n:,}"

components.html(f"""
<!DOCTYPE html><html dir="rtl"><head><meta charset="UTF-8">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
<style>*{{margin:0;padding:0;box-sizing:border-box;}}body{{background:transparent;direction:rtl;padding:0 .4rem;}}
.wrap{{background:#fff;border:1.5px solid #E4E7F2;border-radius:16px;padding:1.4rem;box-shadow:0 4px 24px rgba(43,92,232,.08);}}
.chart-wrap{{position:relative;height:310px;}}
.legend{{display:flex;gap:1.4rem;justify-content:center;margin-top:.85rem;flex-wrap:wrap;}}
.leg{{display:flex;align-items:center;gap:.38rem;font-family:'Heebo',sans-serif;font-size:.8rem;color:#6B7A99;}}
.ld{{width:11px;height:11px;border-radius:50%;}}</style></head><body>
<div class="wrap">
  <div class="chart-wrap"><canvas id="c"></canvas></div>
  <div class="legend">
    <div class="leg"><div class="ld" style="background:#2B5CE8"></div>הנחת תשואה: 9.5% שנתי (לצורך הסימולציה בלבד)</div>
    <div class="leg"><div class="ld" style="background:#A8B2CC"></div>הנחת תשואה: 4.5% שנתי (לצורך הסימולציה בלבד)</div>
  </div>
</div>
<script>
const ctx=document.getElementById('c').getContext('2d');
const g1=ctx.createLinearGradient(0,0,0,280);g1.addColorStop(0,'rgba(43,92,232,0.16)');g1.addColorStop(1,'rgba(43,92,232,0)');
const g2=ctx.createLinearGradient(0,0,0,280);g2.addColorStop(0,'rgba(168,178,204,0.13)');g2.addColorStop(1,'rgba(168,178,204,0)');
new Chart(ctx,{{type:'line',data:{{labels:{list(range(YEARS+1))},datasets:[
  {{label:'נזיל',data:{free_vals},borderColor:'#2B5CE8',backgroundColor:g1,borderWidth:3,pointBackgroundColor:'#2B5CE8',pointRadius:4,pointHoverRadius:7,fill:true,tension:.42}},
  {{label:'פנסיה',data:{locked_vals},borderColor:'#A8B2CC',backgroundColor:g2,borderWidth:2,pointBackgroundColor:'#A8B2CC',pointRadius:3,pointHoverRadius:5,fill:true,tension:.42,borderDash:[5,4]}}
]}},options:{{responsive:true,maintainAspectRatio:false,interaction:{{mode:'index',intersect:false}},
  plugins:{{legend:{{display:false}},tooltip:{{backgroundColor:'rgba(27,37,89,0.92)',borderColor:'rgba(43,92,232,0.3)',borderWidth:1,titleColor:'#fff',bodyColor:'#A8B2CC',rtl:true,callbacks:{{label:c=>' '+c.dataset.label+': ₪'+c.raw.toLocaleString('he-IL')}}}}}},
  scales:{{x:{{grid:{{color:'rgba(0,0,0,0.04)'}},ticks:{{color:'#A8B2CC',font:{{size:11}},callback:v=>'שנה '+v}}}},y:{{grid:{{color:'rgba(0,0,0,0.04)'}},ticks:{{color:'#A8B2CC',font:{{size:11}},callback:v=>v>=1000000?'₪'+(v/1000000).toFixed(1)+'מ':'₪'+(v/1000).toFixed(0)+'א'}},position:'right'}}}}
}}}});
</script></body></html>
""", height=390, scrolling=False)

st.markdown(f'<div class="delta-row"><div class="delta-card hi"><div class="delta-val">{_fmt(free_vals[-1])}</div><div class="delta-lbl">סימולציה: תשואה 9.5% / 10 שנה</div></div><div class="delta-card"><div class="delta-val neg">{_fmt(locked_vals[-1])}</div><div class="delta-lbl">סימולציה: תשואה 4.5% / 10 שנה</div></div><div class="delta-card hi"><div class="delta-val">+{_fmt(gain_delta)}</div><div class="delta-lbl">הפרש סימולטיבי</div></div><div class="delta-card hi"><div class="delta-val">+{gain_pct}%</div><div class="delta-lbl">הפרש באחוזים</div></div></div><div style="font-size:.74rem;color:#A8B2CC;direction:rtl;margin-top:.6rem;text-align:center;">* סימולציה להמחשה בלבד. אינה מהווה ייעוץ פנסיוני. התוצאות בפועל תלויות בתנאי הקרן ובגורמים רבים.</div>', unsafe_allow_html=True)

if not st.session_state.calc_lead_sent:
    st.markdown('<div class="form-wrap"><div class="form-title">📩 קבלו ניתוח אישי חינם — ללא התחייבות</div>', unsafe_allow_html=True)
    with st.form("calc_lead", clear_on_submit=True):
        fc1,fc2,fc3=st.columns(3)
        with fc1: cn=st.text_input("שם מלא *",placeholder="ישראל ישראלי")
        with fc2: cp=st.text_input("טלפון *",placeholder="05X-XXXXXXX")
        with fc3: ce=st.text_input("אימייל",placeholder="name@example.com")
        if st.form_submit_button("שלחו לי ניתוח אישי ←",use_container_width=True):
            if cn.strip() and cp.strip():
                crm.create_lead(cn.strip(),cp.strip(),ce.strip(),"אתר",f"מחשבון | ₪{amount:,} | פוטנציאל +{_fmt(gain_delta)} (+{gain_pct}%)")
                st.session_state.calc_lead_sent=True
                st.rerun()
            else: st.error("נא למלא שם וטלפון.")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="msg-ok">✅ &nbsp; קיבלנו! נציג יצור קשר תוך 24 שעות לניתוח האישי.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# DOCUMENT UPLOADER
# ═════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="lf-divider"></div><div id="lf-upload"></div>', unsafe_allow_html=True)
st.markdown('<div class="lf-section">', unsafe_allow_html=True)
st.markdown('<div style="margin-bottom:2rem;"><div class="section-chip fade-up">ניתוח מסמכים</div><h2 class="section-h fade-up-1">העלו את קובץ המסלקה שלכם</h2><p class="section-p fade-up-2">האלגוריתם ינתח את כל הקרנות ויציג תמונת מצב מלאה — תוך פחות מ-24 שעות. אינו מהווה ייעוץ פנסיוני.</p></div><div class="badge-row fade-up-2" style="margin-bottom:1.5rem;"><span class="trust-badge">🔒 הצפנה AES-256</span><span class="trust-badge">🛡️ ISO 27001</span><span class="trust-badge">✅ GDPR</span><span class="trust-badge">🏦 ממשק מסלקה רשמי</span><span class="trust-badge">⚖️ פיקוח רשות שוק ההון</span></div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("גררו את קובץ המסלקה לכאן, או לחצו לבחירה", type=["dat","xml","pdf"], key="lf_up")
if uploaded_file:
    kb=round(uploaded_file.size/1024,1)
    st.markdown(f'<div class="card fade-up" style="display:flex;align-items:center;gap:1rem;margin:.8rem 0;border-color:rgba(0,184,148,.3);background:#E6FAF7;"><span style="font-size:2rem;">✅</span><div><div style="color:#057a62;font-weight:700;">{uploaded_file.name}</div><div style="color:#6B7A99;font-size:.85rem;">{kb} KB · התקבל בהצלחה</div></div></div>', unsafe_allow_html=True)

if not st.session_state.upload_lead_sent:
    st.markdown('<div class="form-wrap"><div class="form-title">📋 פרטי יצירת קשר לקבלת הניתוח</div>', unsafe_allow_html=True)
    with st.form("upload_lead", clear_on_submit=True):
        uf1,uf2,uf3=st.columns(3)
        with uf1: un=st.text_input("שם מלא *",placeholder="ישראל ישראלי",key="un")
        with uf2: up_=st.text_input("טלפון *",placeholder="05X-XXXXXXX",key="up_")
        with uf3: ue=st.text_input("אימייל",placeholder="name@example.com",key="ue")
        ua=st.checkbox("אני מסכים/ה לתנאי השימוש ומדיניות הפרטיות")
        if st.form_submit_button("שלחו לניתוח ←",use_container_width=True):
            if un.strip() and up_.strip() and ua:
                doc=f" | קובץ: {uploaded_file.name} ({kb} KB)" if uploaded_file else ""
                crm.create_lead(un.strip(),up_.strip(),ue.strip(),"אתר",f"העלאת מסמך{doc}")
                st.session_state.upload_lead_sent=True
                st.rerun()
            elif not ua: st.error("יש לאשר את תנאי השימוש.")
            else: st.error("נא למלא שם וטלפון.")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="msg-ok">✅ &nbsp; תודה! הצוות יבצע ניתוח מלא ויחזור אליכם תוך 24 שעות.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# TEAM
# ═════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="lf-divider"></div><div id="lf-team"></div>', unsafe_allow_html=True)
st.markdown('<div class="lf-section">', unsafe_allow_html=True)
st.markdown('<div style="text-align:center;margin-bottom:3rem;"><div class="section-chip fade-up">הצוות שלנו</div><h2 class="section-h fade-up-1" style="text-align:center;">אנשים אמיתיים. מומחיות אמיתית.</h2><p class="section-p fade-up-2" style="text-align:center;max-width:540px;margin:0 auto;">הצוות מורכב ממומחי פנסיה, טכנולוגיה ומשפט — עם עשרות שנות ניסיון בשוק ההון הישראלי.</p></div>', unsafe_allow_html=True)
t1,t2,t3,t4=st.columns(4)
for col,ico,name,role,bio,d in [
    (t1,"👨‍💼","אדי אלבז","מייסד ומנכ\"ל","מומחה לנזילות פנסיונית עם 15 שנות ניסיון בשוק ההון. הוביל תהליכי שחרור הון בהיקף מעל מיליארד ₪.","fade-up"),
    (t2,"👩‍💻","מיכל רוזן","סמנכ\"לית טכנולוגיה","12 שנה בפינטק ו-AI. ייסדה שתי חברות סטארטאפ ומומחית בעיבוד מסמכים פיננסיים.","fade-up-1"),
    (t3,"👨‍⚖️","עמית כהן","יועץ משפטי ראשי","עו\"ד מומחה לדיני פנסיה ורגולציה פיננסית. שותף בכיר לשעבר בפירמה מובילה.","fade-up-2"),
    (t4,"👩‍🏫","רותם לוי","ראש יחידת פנסיה","יועצת פנסיונית מורשית עם 18 שנה בתחום. ניהלה תיקים של אלפי לקוחות.","fade-up-3"),
]:
    with col:
        st.markdown(f'<div class="team-card {d}"><div class="team-avatar">{ico}</div><div class="team-name">{name}</div><div class="team-role">{role}</div><div class="team-bio">{bio}</div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# TRUST SIGNALS
# ═════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="lf-divider"></div>', unsafe_allow_html=True)
components.html("""
<!DOCTYPE html><html dir="rtl" lang="he"><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;600;700;800&family=Montserrat:wght@800&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:#F7F8FF;direction:rtl;font-family:'Heebo',sans-serif;color:#1B2559;}
.wrap{max-width:1200px;margin:0 auto;padding:4.5rem 2.5rem;}
.chip{display:inline-block;font-size:.72rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#2B5CE8;background:#EEF2FF;border:1.5px solid rgba(43,92,232,.18);border-radius:50px;padding:.3rem .9rem;margin-bottom:1rem;}
h2{font-family:'Montserrat',sans-serif;font-size:clamp(1.8rem,3vw,2.4rem);font-weight:800;color:#1B2559;margin-bottom:.85rem;line-height:1.22;}
.sub{font-size:1rem;color:#6B7A99;line-height:1.75;margin-bottom:3rem;}
.media-row{display:flex;align-items:center;justify-content:center;gap:2rem;flex-wrap:wrap;margin-bottom:3rem;padding:1.8rem;background:#fff;border:1.5px solid #E4E7F2;border-radius:16px;}
.media-lbl{font-size:.74rem;color:#A8B2CC;font-weight:700;letter-spacing:1px;text-transform:uppercase;}
.media-box{height:33px;width:92px;background:#F1F3FB;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:.71rem;color:#A8B2CC;border:1px solid #E4E7F2;font-weight:600;}
.tg{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;margin-bottom:2.5rem;}
@media(max-width:640px){.tg{grid-template-columns:1fr;}}
.testi{background:#fff;border:1.5px solid #E4E7F2;border-radius:16px;padding:2rem;transition:all .25s;}
.testi:hover{border-color:rgba(43,92,232,.2);box-shadow:0 8px 32px rgba(43,92,232,.1);}
.stars{color:#F59E0B;font-size:.95rem;margin-bottom:.65rem;}
.quote{font-size:.92rem;color:#1B2559;line-height:1.72;font-style:italic;margin-bottom:.85rem;}
.who{font-size:.81rem;color:#2B5CE8;font-weight:700;}
.sg{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;}
@media(max-width:640px){.sg{grid-template-columns:1fr;}}
.sc{background:#fff;border:1.5px solid #E4E7F2;border-radius:14px;padding:1.4rem;text-align:center;transition:all .25s;}
.sc:hover{border-color:rgba(43,92,232,.2);box-shadow:0 4px 20px rgba(43,92,232,.08);}
.si{font-size:1.7rem;margin-bottom:.55rem;display:block;}
.st{font-size:.87rem;font-weight:700;color:#1B2559;margin-bottom:.3rem;}
.sd{font-size:.76rem;color:#6B7A99;line-height:1.55;}
</style></head><body>
<div class="wrap">
  <div style="text-align:center;margin-bottom:2.5rem;">
    <div class="chip">אמינות ואבטחה</div>
    <h2>מאות לקוחות כבר קיבלו תמונת מצב ברורה</h2>
    <p class="sub">נזיל עובדת עם גופים פיננסיים מובילים ועומדת בכל תקני האבטחה הגבוהים ביותר. המידע המוצג אינו ייעוץ פנסיוני.</p>
  </div>
  <div class="media-row">
    <span class="media-lbl">כפי שהופיע ב ←</span>
    <div class="media-box">TheMarker</div>
    <div class="media-box">Calcalist</div>
    <div class="media-box">Globes</div>
    <div class="media-box">Ynet כסף</div>
  </div>
  <div class="tg">
    <div class="testi">
      <div class="stars">★★★★★</div>
      <div class="quote">«ניתוח מדויק, שירות מקצועי לחלוטין. ה-₪180,000 הגיעו לחשבון תוך 12 ימים. לא האמנתי שזה אפשרי.»</div>
      <div class="who">רון ל., 47 — מנהל פרויקטים, תל אביב</div>
    </div>
    <div class="testi">
      <div class="stars">★★★★★</div>
      <div class="quote">«ידעתי שיש לי כסף בפנסיה אבל לא ידעתי איך לגשת אליו. נזיל עזרו לי לשחרר מעל ₪240,000 תוך שלושה שבועות.»</div>
      <div class="who">מירי כ., 52 — עורכת דין, חיפה</div>
    </div>
  </div>
  <div class="sg">
    <div class="sc"><span class="si">🔒</span><div class="st">הצפנה מקצה לקצה</div><div class="sd">כל המסמכים מוצפנים ב-AES-256 ונמחקים אוטומטית לאחר הניתוח.</div></div>
    <div class="sc"><span class="si">⚖️</span><div class="st">פעילות מורשית</div><div class="sd">נזיל פועלת תחת פיקוח רשות שוק ההון, ביטוח וחיסכון של מדינת ישראל.</div></div>
    <div class="sc"><span class="si">🏦</span><div class="st">ממשק מסלקה רשמי</div><div class="sd">גישה ישירה למסלקה הפנסיונית — מידע אמיתי, מדויק ומאומת בזמן אמת.</div></div>
  </div>
</div>
</body></html>
""", height=700, scrolling=False)

# ═════════════════════════════════════════════════════════════════════════════
# AI Q&A CHAT
# ═════════════════════════════════════════════════════════════════════════════
_AI_QA = {
    "כמה כסף אני יכול לשחרר?": "בממוצע לקוחות נזיל משחררים בין 30% ל-60% מהחסכונות הפנסיוניים. הסכום תלוי בסוג הקרן, ותק ותנאי החוזה. העלו קובץ מסלקה ונחשב עבורכם תוך 24 שעות.",
    "האם זה בטוח לפנסיה שלי?": "כן. נזיל פועלת בהתאם לחוק ובפיקוח רשות שוק ההון. כל תכנית מלווה בייעוץ משפטי ופנסיוני ומשקפת את ההשפעה על קצבת הפרישה.",
    "כמה זמן לוקח התהליך?": "ניתוח המסמכים — פחות מ-24 שעות. לאחר מכן שיחת ייעוץ, ובמרבית המקרים הכסף מגיע לחשבון תוך 14 ימי עסקים מחתימה.",
}
_AI_DEFAULT = "שלום! 👋 אני המדריך של נזיל. בחרו שאלה מהכפתורים למטה, או כתבו שאלה חופשית."

st.markdown('<div class="lf-divider"></div><div id="lf-ai"></div>', unsafe_allow_html=True)
st.markdown('<div class="lf-section">', unsafe_allow_html=True)
st.markdown('<div style="margin-bottom:2rem;"><div class="section-chip fade-up">מדריך AI</div><h2 class="section-h fade-up-1">שאלות? אנחנו כאן בשבילכם</h2><p class="section-p fade-up-2">המדריך שלנו זמין 24/7. בחרו שאלה מהירה או כתבו בחופשיות.</p></div>', unsafe_allow_html=True)

ai1,ai2,ai3=st.columns(3)
for _c,_q in zip([ai1,ai2,ai3],list(_AI_QA.keys())):
    with _c:
        if st.button(_q,key=f"aiq_{_q[:8]}",use_container_width=True):
            if not st.session_state.ai_messages: st.session_state.ai_messages.append({"r":"bot","t":_AI_DEFAULT})
            st.session_state.ai_messages.append({"r":"usr","t":_q})
            st.session_state.ai_messages.append({"r":"bot","t":_AI_QA[_q]})
            st.rerun()

st.markdown('<div class="card" style="padding:0;overflow:hidden;margin-top:1rem;"><div style="padding:.85rem 1.5rem;border-bottom:1.5px solid #E4E7F2;display:flex;align-items:center;gap:.7rem;background:#fff;"><div style="width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,#2B5CE8,#00B894);display:flex;align-items:center;justify-content:center;font-size:.95rem;">🤖</div><div><div style="font-size:.88rem;font-weight:700;color:#1B2559;font-family:Heebo,sans-serif;">מדריך נזיל</div><div style="font-size:.7rem;color:#00B894;font-weight:600;">● זמין עכשיו</div></div></div><div style="padding:1.4rem;min-height:160px;max-height:300px;overflow-y:auto;background:#FAFBFF;">', unsafe_allow_html=True)
for m in (st.session_state.ai_messages or [{"r":"bot","t":_AI_DEFAULT}]):
    if m["r"]=="bot":
        st.markdown(f'<div class="chat-msg-bot"><div class="chat-av bot">🤖</div><div class="chat-bbl-bot">{m["t"]}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-msg-user"><div class="chat-av usr">👤</div><div class="chat-bbl-usr">{m["t"]}</div></div>', unsafe_allow_html=True)
st.markdown('</div></div>', unsafe_allow_html=True)

with st.form("aif",clear_on_submit=True):
    ac1,ac2=st.columns([5,1])
    with ac1: ai_txt=st.text_input("שאלה",placeholder="כתבו שאלה חופשית...",label_visibility="collapsed")
    with ac2: ai_send=st.form_submit_button("שלח ←",use_container_width=True)
if ai_send and ai_txt.strip():
    if not st.session_state.ai_messages: st.session_state.ai_messages.append({"r":"bot","t":_AI_DEFAULT})
    st.session_state.ai_messages.append({"r":"usr","t":ai_txt.strip()})
    matched=next((v for k,v in _AI_QA.items() if any(w in ai_txt for w in k.split()[:2])),None)
    st.session_state.ai_messages.append({"r":"bot","t":matched or "שאלה מעולה! נציג מומחה יענה עליה בשיחה האישית. השאירו פרטים למעלה ונחזור בהקדם."})
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# FAQ
# ═════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="lf-divider"></div><div id="lf-faq"></div>', unsafe_allow_html=True)
st.markdown('<div class="lf-section">', unsafe_allow_html=True)
st.markdown('<div style="margin-bottom:2.5rem;"><div class="section-chip fade-up">שאלות ותשובות</div><h2 class="section-h fade-up-1">כל מה שרציתם לדעת</h2><p class="section-p fade-up-2">55 שאלות ותשובות על שחרור הון פנסיוני, התהליך, האבטחה והעלויות.</p></div>', unsafe_allow_html=True)
st.markdown('<div style="max-width:820px;margin:0 auto;">', unsafe_allow_html=True)

fq1,fq2=st.columns([3,1])
with fq1: sq=st.text_input("חיפוש שאלה",placeholder="🔍  חפשו שאלה...",label_visibility="collapsed",key="faq_s")
with fq2: cq=st.selectbox("קטגוריה",FAQ_CATS,label_visibility="collapsed",key="faq_c")

filtered=FAQ
if cq and cq!="הכל": filtered=[f for f in filtered if f["cat"]==cq]
if sq.strip():
    s=sq.strip().lower()
    filtered=[f for f in filtered if s in f["q"].lower() or s in f["a"].lower()]

st.markdown(f'<div style="font-size:.82rem;color:var(--t3);margin-bottom:1rem;direction:rtl;">נמצאו {len(filtered)} שאלות</div>', unsafe_allow_html=True)

faq_items=""
for i,item in enumerate(filtered):
    faq_items+=f'<div class="fi" id="fi{i}"><div class="fq" onclick="tog({i})"><span>{item["q"]}</span><div style="display:flex;align-items:center;gap:.55rem;flex-shrink:0;"><span class="chip">{item["cat"]}</span><span class="arr" id="ar{i}">▾</span></div></div><div class="fa" id="fa{i}" style="display:none;">{item["a"]}</div></div>'

components.html(f"""
<!DOCTYPE html><html dir="rtl"><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{background:transparent;direction:rtl;font-family:'Heebo',sans-serif;height:100%;}}
.scroll-area{{height:560px;overflow-y:auto;padding-left:4px;}}
.scroll-area::-webkit-scrollbar{{width:5px;}}
.scroll-area::-webkit-scrollbar-track{{background:#F1F3FB;border-radius:10px;}}
.scroll-area::-webkit-scrollbar-thumb{{background:#C8D0E8;border-radius:10px;}}
.fi{{background:#fff;border:1.5px solid #E4E7F2;border-radius:14px;margin-bottom:.55rem;overflow:hidden;transition:border-color .2s,box-shadow .2s;}}
.fi:hover{{border-color:rgba(43,92,232,.22);box-shadow:0 4px 20px rgba(43,92,232,.08);}}
.fi.open{{border-color:rgba(43,92,232,.28);}}
.fq{{display:flex;justify-content:space-between;align-items:center;padding:.9rem 1.3rem;cursor:pointer;font-weight:600;font-size:.9rem;color:#1B2559;direction:rtl;gap:1rem;}}
.fa{{padding:.78rem 1.3rem .95rem;font-size:.86rem;color:#6B7A99;line-height:1.7;border-top:1px solid #E4E7F2;}}
.chip{{font-size:.65rem;font-weight:700;color:#2B5CE8;background:#EEF2FF;border-radius:50px;padding:.15rem .58rem;white-space:nowrap;}}
.arr{{color:#C8D0E8;transition:transform .2s;font-size:.95rem;flex-shrink:0;font-weight:700;}}
.fi.open .arr{{transform:rotate(180deg);color:#2B5CE8;}}
.fade-in{{opacity:0;transform:translateY(8px);animation:fi .3s ease forwards;}}
@keyframes fi{{to{{opacity:1;transform:translateY(0)}}}}
</style></head><body>
<div class="scroll-area" id="sa">
{{faq_items}}
</div>
<script>
function tog(i){{
  var fi=document.getElementById('fi'+i),fa=document.getElementById('fa'+i),ar=document.getElementById('ar'+i);
  var open=fa.style.display!=='none';
  fa.style.display=open?'none':'block';
  fi.classList.toggle('open',!open);
  ar.style.transform=open?'':'rotate(180deg)';
  ar.style.color=open?'':'#2B5CE8';
}}
document.querySelectorAll('.fi').forEach(function(el,i){{
  el.style.opacity='0';el.style.transform='translateY(8px)';
  el.style.transition='opacity .3s '+(i*0.03)+'s ease,transform .3s '+(i*0.03)+'s ease';
  setTimeout(function(){{el.style.opacity='1';el.style.transform='translateY(0)';}},50+i*30);
}});
</script></body></html>
""".replace("{faq_items}", faq_items), height=590, scrolling=False)
st.markdown('</div></div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="lf-divider"></div>', unsafe_allow_html=True)
components.html("""
<!DOCTYPE html><html dir="rtl" lang="he"><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;600;700&family=Montserrat:wght@800;900&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:#1B2559;color:#A8B2CC;font-family:'Heebo',sans-serif;direction:rtl;}
.footer{max-width:1200px;margin:0 auto;padding:3.5rem 2.5rem 2rem;}
.top{display:flex;justify-content:space-between;align-items:flex-start;gap:2rem;flex-wrap:wrap;margin-bottom:2.5rem;}
.lt{font-family:'Montserrat',sans-serif;font-size:1.4rem;font-weight:900;background:linear-gradient(135deg,#6B9FFF,#00E5C3);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:.3rem;}
.ls{font-size:.81rem;color:#6B7A99;}
.email a{color:#6B9FFF;text-decoration:none;font-size:.83rem;}
.links{display:flex;gap:1.7rem;flex-wrap:wrap;align-items:center;}
.links a{color:#6B7A99;text-decoration:none;font-size:.86rem;transition:color .2s;}
.links a:hover{color:#6B9FFF;}
.div{height:1px;background:rgba(255,255,255,.08);margin:1.5rem 0;}
.bot{display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;flex-wrap:wrap;}
.legal{font-size:.72rem;color:#4A5279;line-height:1.65;max-width:700px;}
.copy{font-size:.76rem;color:#4A5279;white-space:nowrap;}
</style></head><body>
<div class="footer">
  <div class="top">
    <div>
      <div class="lt">נזיל | LiquiFund</div>
      <div class="ls">שחרור הון פנסיוני חכם, שקוף ומאובטח</div>
      <div class="email" style="margin-top:.5rem;">📧 <a href="mailto:adi@nazil.info">adi@nazil.info</a></div>
    </div>
    <div class="links">
      <a href="#" onclick="window.parent.location.href='?page=terms';return false;">תנאי שימוש</a>
      <a href="#" onclick="window.parent.location.href='?page=privacy';return false;">מדיניות פרטיות</a>
      <a href="#" onclick="window.parent.location.href='?page=accessibility';return false;">נגישות</a>
      <a href="#" onclick="window.parent.document.getElementById('lf-faq').scrollIntoView({behavior:'smooth'});return false;">שאלות נפוצות</a>
      <a href="mailto:adi@nazil.info">צור קשר</a>
    </div>
  </div>
  <div class="div"></div>
  <div class="bot">
    <div class="legal">המידע המוצג מבוסס על נתוני המסלקה הפנסיונית ומהווה סימולציה בלבד. אין לראות במידע זה ייעוץ פנסיוני או תחליף לייעוץ השקעות המותאם אישית. ביצוע פעולות במוצר פנסיוני עלול לפגוע בקצבת הפרישה וברצף הביטוחי.</div>
    <div class="copy">© 2026 Nazil | LiquiFund</div>
  </div>
</div>
</body></html>
""", height=210, scrolling=False)
