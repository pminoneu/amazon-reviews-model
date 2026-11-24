"""Build a two-page English proposal plus one Streamlit sketch page."""
from pathlib import Path
import json
import os
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle, Flowable

BASE = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get('A6_PDF_OUTPUT_DIR', str(BASE / 'submission')))
OUT.mkdir(parents=True, exist_ok=True)
A = json.loads((BASE/'results/audit.json').read_text())
PDF = OUT/'Assignment6_Proposal_Early_Product_Success.pdf'
INK = colors.HexColor('#172D39')
TEAL = colors.HexColor('#1D6C70')
GRAY = colors.HexColor('#52616C')
LIGHT = colors.HexColor('#E4EAED')
PALE = colors.HexColor('#F4F7F8')
W, H, M = 612, 792, 43
CW = W-2*M
# Prefer an installed Arial pair; use ReportLab's built-in Helvetica otherwise.
# Font files are not redistributed in this package.
font_pairs = [
    (Path('/System/Library/Fonts/Supplemental/Arial.ttf'), Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf')),
    (Path(os.environ.get('WINDIR', 'C:/Windows'))/'Fonts/arial.ttf', Path(os.environ.get('WINDIR', 'C:/Windows'))/'Fonts/arialbd.ttf'),
    (Path('/usr/share/fonts/truetype/msttcorefonts/Arial.ttf'), Path('/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf')),
]
FONT_REGULAR, FONT_BOLD = 'Helvetica', 'Helvetica-Bold'
for regular, bold in font_pairs:
    if regular.is_file() and bold.is_file():
        pdfmetrics.registerFont(TTFont('A6Arial', str(regular)))
        pdfmetrics.registerFont(TTFont('A6Arial-Bold', str(bold)))
        pdfmetrics.registerFontFamily('A6Arial', normal='A6Arial', bold='A6Arial-Bold', italic='A6Arial', boldItalic='A6Arial-Bold')
        FONT_REGULAR, FONT_BOLD = 'A6Arial', 'A6Arial-Bold'
        break


BODY = ParagraphStyle('body',fontName=FONT_REGULAR,fontSize=10.1,leading=12.9,textColor=INK,spaceAfter=5)
SMALL = ParagraphStyle('small',parent=BODY,fontSize=8.1,leading=10.3,spaceAfter=3,textColor=GRAY)
HEAD = ParagraphStyle('head',parent=BODY,fontName=FONT_BOLD,fontSize=11.2,leading=14.0,spaceBefore=8.5,spaceAfter=5,textColor=TEAL)
TITLE = ParagraphStyle('title',parent=BODY,fontName=FONT_BOLD,fontSize=20.0,leading=23,spaceAfter=5)
SUB = ParagraphStyle('subtitle',parent=SMALL,fontSize=9,leading=12,spaceAfter=7)

def p(text,style=BODY): return Paragraph(text, style)
def link(url,label): return f'<link href="{escape(url, {chr(34): "&quot;"})}" color="#1D6C70"><u>{label}</u></link>'
JUNGLE='https://support.junglescout.com/hc/en-us/articles/4413674924311-Historical-Trends-Graph-on-the-Product-Listing-page'
HELIUM='https://kb.helium10.com/hc/en-us/articles/48006601967643-Review-Insights-Analyze-Customer-Feedback-with-Amazon-Data'
DATA='https://amazon-reviews-2023.github.io/'
REV=A['sources']['All_Beauty.jsonl.gz']['url']
META=A['sources']['meta_All_Beauty.jsonl.gz']['url']

# Keep an editable content record alongside the reproducible calculations.
sections = [
('1  The user, the decision, and what already exists', [
    '<b>User and decision.</b> Maya is a small Amazon beauty seller whose product has just received its 20th review. She must decide whether to place another inventory order and continue advertising. Today she relies on the average star rating. Our Streamlit app will estimate the probability of strong review performance over the next year and compare early-review patterns with historical peers. If the outlook is weak, she would defer a large reorder, inspect recurring complaints, and run a smaller test; a stronger outlook would prompt a reorder review using her own margin and sales data.',
    '<b>Existing tools.</b> '+link(JUNGLE,'Jungle Scout Historical Trends')+' shows price, rank, estimated unit sales, and review trends. This helps with market context, but its documented workflow does not establish a first-20-reviews forecast for our defined one-year outcome. '+link(HELIUM,'Helium 10 Review Insights')+' summarizes review topics, sentiment trends, and category comparisons. It helps identify complaints, but its documented output does not estimate our future success label. Our distinction is a fixed early-review cutoff, a testable outcome, and a held-out baseline; these are proposed differences based on the linked documentation.'
]),
('2  Data reality check', [
    '<b>Sources and unit.</b> We loaded McAuley Lab\'s '+link(DATA,"Amazon Reviews 2023")+' '+link(REV,'All_Beauty reviews')+' and '+link(META,'product metadata')+'. The raw review file contains <b>701,528 reviews for 112,565 parent products</b>; metadata contains 112,590 products. Reviews span November 2000 to September 2023. Removing 7,275 exact duplicate records leaves 694,253 reviews. A modeling row is one <b>parent_asin</b> (including its variants), summarized at its 20th distinct review. Requiring 20 reviews and a 365-day observation window before the dataset endpoint leaves <b>5,709 products</b>. Metadata supplies display titles only.',
    '<b>Target distribution.</b> Using the training-derived rule in Section 3, 836 products (14.6%) meet the proxy and 4,873 (85.4%) do not. This is the full eligible cohort; the test set has a 15.5% positive rate.',
    '<b>One random row.</b> Sampling the product table with seed 42 selects <b>B01ETUB7Q2</b>, a men\'s cologne. By September 20, 2018, its first 20 reviews averaged 4.05 stars, 75% were verified purchases, and 846 days had passed since its first review. In the following 365 days, it received 9 reviews averaging 3.78 stars, so <b>is_successful = 0</b>. This row describes one product\'s early signals and later observed review outcome.',
    '<b>Surprise and change of plan.</b> Exact duplicate reviews changed eligibility: the original idea\'s 5,787 examples become 5,709 after cleaning. Also, the median time to review 20 is <b>339 days</b>. We therefore describe this as early in review history, not necessarily early after launch. The revised label rate also reflects a training-only volume threshold.'
]),
('3  Target, metric, and baseline', [
    '<b>Target.</b> <b>is_successful</b> is a derived binary classification column in our product table, not a supplied raw field. It equals 1 if reviews strictly after review 20 and within the next <b>365 days</b> number at least <b>24</b> and average at least <b>4.0 stars</b>; otherwise it is 0. The 24-review cutoff is the training set\'s 75th percentile, with ties included, and is fixed for testing. No later reviews means label 0. This measures review traction and satisfaction, not sales or profit.',
    '<b>Evaluation.</b> Following Assignment 5, we split unique products <b>70/30, seed 42</b> before choosing the volume threshold: <b>3,996 train / 1,713 test</b>, without stratification. Primary metric: <b>balanced accuracy</b>, the average of success recall and non-success recall; it prevents the majority class from dominating the score. We will also report success precision and recall because false positives can encourage costly reorders. Feature fitting and threshold selection will use training cross-validation; this baseline test set is reserved for final model comparison.',
    '<b>No-input baseline, actually run.</b> Always predicting the training majority class (0) gives test <b>balanced accuracy = 0.500</b>, accuracy = <b>84.47%</b>, and success recall = <b>0%</b>. It correctly labels 1,447 negatives and misses all 266 positives. This is the required score to beat; a high raw accuracy alone is not sufficient.'
]),
('4  Predictions before you model', [
    '<b>Three expected inputs.</b> (1) <b>early_rating_mean</b>: satisfaction in the first 20 reviews may persist. (2) <b>days_to_20</b>: faster review accumulation may signal stronger demand. (3) <b>early_text</b>: TF-IDF features from the first 20 review texts may distinguish repeat-purchase praise from defects beyond the star average. Verified-purchase share will be an additional candidate; category is constant in this first version.',
    '<b>Prediction, not a measured result.</b> Before fitting feature-based models, we expect our best model to reach <b>0.65-0.70 balanced accuracy</b>, or <b>15-20 percentage points</b> above the 0.50 baseline. Ratings and review timing should carry signal, but missing sales, advertising, and stockout information should limit performance. We will compare regularized logistic regression with structured-feature tree models; no feature-based model has been trained for this proposal.'
]),
('5  App walkthrough', [
    'Maya uploads the complete first 20 reviews (rating, text, date, verified-purchase flag) for one parent product, or selects a historical demo. The app validates the fields and cutoff, then displays the estimated <b>probability of meeting the review-success proxy</b>, the training cohort\'s 14.3% reference rate, and influential early signals. It will show calibration evidence before treating scores as probabilities. Maya inspects complaints and compares peers before choosing a small test or a reorder review; the app does not calculate order quantities.',
    'In <b>Explore</b>, she filters historical training products by early rating and days to review 20, browses text-based peer groups, and sees each group\'s size and observed success share. She can learn that favorable early stars alone need not imply sustained review volume. These are associations, not evidence that changing reviews causes success. Page 3 sketches both tabs and their flow.'
]),
('6  Risks and team plan', [
    '<b>Main risk.</b> The review proxy may not match the seller\'s business outcome, and products that never reach 20 reviews are excluded. We will state this limit, test alternative label thresholds using training data, and seek seller feedback. To reduce leakage, we exclude helpful votes, price, and metadata rating totals because their cutoff-time values are unavailable. A later chronological check will train only on products whose 365-day outcomes finish before the test cutoff; older 2000-2023 data still limits current-market claims.',
    '<b>Ownership over three weeks.</b> <b>Team lead (me)</b> will do the main implementation: Week 1, cleaning, labels, baseline and features; Week 2, modeling and evaluation; Week 3, Streamlit integration and final report. <b>Other teammates</b> will support prior-tool research (Week 1), exploratory charts (Week 2), and usability testing and proofreading (Week 3). Their individual assignments remain to be confirmed. Everyone reviews the final claims and demo.'
])]

class Sketch(Flowable):
    def __init__(self):
        Flowable.__init__(self); self.width=CW; self.height=628
    def draw(self):
        c=self.canv
        def text(x,y,s,size=9,bold=False,color=INK):
            c.setFillColor(color);c.setFont(FONT_BOLD if bold else FONT_REGULAR,size);c.drawString(x,y,s)
        def wrap(x,y,s,width,size=8.2,leading=10.5,bold=False,color=INK):
            sty=ParagraphStyle('sketch',fontName=FONT_BOLD if bold else FONT_REGULAR,fontSize=size,leading=leading,textColor=color)
            q=Paragraph(s,sty); _,hh=q.wrap(width,1000);q.drawOn(c,x,y-hh);return y-hh
        def box(x,y,w,h,fill=colors.white,stroke=LIGHT,r=4):
            c.setFillColor(fill);c.setStrokeColor(stroke);c.setLineWidth(.7);c.roundRect(x,y,w,h,r,fill=1,stroke=1)
        def rule(x1,y1,x2,y2,color=LIGHT):
            c.setStrokeColor(color);c.setLineWidth(.7);c.line(x1,y1,x2,y2)
        def button(x,y,w,label):
            box(x,y,w,24,fill=TEAL,stroke=TEAL);text(x+10,y+8,label,8.5,True,colors.white)
        def arrow(x,y):
            c.setStrokeColor(TEAL);c.setLineWidth(1.2);c.line(x,y,x,y-12);c.line(x,y-12,x-3,y-8);c.line(x,y-12,x+3,y-8)

        text(0,612,'A. PREDICT  /  Maya brings the first 20 reviews',10.5,True,TEAL)
        box(0,313,CW,284)
        box(0,563,CW,34,fill=PALE)
        text(13,575,'Review Outlook',12,True)
        text(343,576,'Predict',9,True,TEAL);text(407,576,'Explore',9)
        rule(340,569,382,569,TEAL)
        # Input sidebar.
        box(10,326,164,226,fill=PALE)
        text(20,535,'1  Add one parent product',9,True)
        box(20,493,144,29)
        text(28,505,'Upload first_20_reviews.csv',8.1)
        text(20,479,'or choose a historical demo',7.9,color=GRAY)
        box(20,450,144,23);text(27,458,'Demo product                 v',8.0)
        wrap(20,438,'Required: rating, text, date,<br/>verified purchase.<br/>Confirm these are the first 20.',143,8,10.5)
        text(20,388,'20 / 20 valid reviews',8.4,True,TEAL)
        button(20,348,144,'Estimate outlook')
        # Forecast card.
        text(190,535,'2  Review the outlook',9.5,True)
        box(190,436,323,83,fill=PALE)
        text(202,498,'Chance of meeting our 365-day review proxy',8.5,True)
        text(202,462,'35%',28,True,TEAL)
        wrap(282,480,'Training reference: 14.3%<br/>Illustrative forecast only.',215,8.3,11)
        text(202,444,'Proxy: 24+ later reviews AND average rating 4.0+',7.9,color=GRAY)
        wrap(190,420,'<b>Inspect early signals</b><br/>Review pace | average rating | recurring text themes<br/><br/>Calibration and evaluation details [expand]<br/>This is a review outcome, not a sales or profit forecast.',320,8.3,11)
        button(190,328,150,'Compare historical peers')
        arrow(CW/2,306)
        text(0,276,'B. EXPLORE  /  Compare patterns before acting',10.5,True,TEAL)
        box(0,57,CW,204)
        box(0,227,CW,34,fill=PALE)
        text(13,239,'Review Outlook',12,True)
        text(343,240,'Predict',9);text(407,240,'Explore',9,True,TEAL)
        rule(405,233,449,233,TEAL)
        box(10,69,164,146,fill=PALE)
        text(20,199,'3  Filter historical peers',9,True)
        text(20,177,'Early rating:  3.5 to 5.0',8)
        rule(23,167,151,167,GRAY)
        c.setFillColor(TEAL);c.circle(60,167,3,fill=1,stroke=0);c.circle(151,167,3,fill=1,stroke=0)
        text(20,146,'Days to review 20:  0-900',8)
        box(20,112,144,22);text(27,120,'Text peer group: All      v',8)
        wrap(20,101,'Training products only.<br/>Show peer counts with rates.',143,7.8,10)
        # Conceptual scatter, deliberately unlabeled fictional points.
        text(190,199,'Early signals and later outcomes',9.3,True)
        rule(213,111,360,111,GRAY);rule(213,111,213,180,GRAY)
        points=[(226,133),(241,157),(254,125),(269,166),(281,148),(293,136),(309,173),(322,155),(341,164)]
        for idx,(x,y) in enumerate(points):
            c.setFillColor(TEAL if idx%3==0 else GRAY)
            if idx%3==0:c.circle(x,y,3,fill=1,stroke=0)
            else:c.rect(x-2,y-2,4,4,fill=1,stroke=0)
        text(226,97,'Days to review 20',7.4,color=GRAY)
        c.saveState();c.translate(203,122);c.rotate(90);text(0,0,'Early stars',7.4,color=GRAY);c.restoreState()
        wrap(377,180,'<b>Peer group</b><br/>Number of products<br/>Observed success share<br/>Common review themes<br/><br/>Open a product to inspect<br/>early reviews and outcome.',135,8,10.5)
        text(190,77,'Schematic marks only - actual plots use training data.',7.5,color=GRAY)
        wrap(0,39,'<b>4  Next action:</b> Maya checks complaints and her own sales, margin, and stock position, then chooses a smaller test or a reorder review. The app supplies evidence; she makes the inventory decision.',CW,9,12)

def footer(c,doc):
    c.setStrokeColor(LIGHT);c.setLineWidth(.6);c.line(M,35,W-M,35)
    c.setFont(FONT_REGULAR,7.6);c.setFillColor(GRAY)
    c.drawString(M,23,'CS6983  |  Assignment 6 proposal  |  Idea 4')
    c.drawRightString(W-M,23,f'{doc.page} / 3')

story=[p('Early Product Success<br/>from Amazon Reviews',TITLE),
       p('Assignment 6 proposal  |  First 20 reviews to a one-year review-performance outlook',SUB)]

for title,paras in sections[:2]:
    story.append(p(title,HEAD))
    for i,para in enumerate(paras):
        story.append(p(para))
        if title.startswith('2') and i==1:
            img_path=BASE/'results/target_distribution.png'
            iw,ih=PILImage.open(img_path).size
            img=Image(str(img_path),width=CW,height=CW*ih/iw)
            story.extend([img,Spacer(1,4)])

story.append(PageBreak())
for title,paras in sections[2:]:
    story.append(p(title,HEAD))
    for para in paras:story.append(p(para))

story.extend([PageBreak(),p('App sketch',TITLE),
              p('Planned Streamlit layout and flow. Wireframe only; numerical forecast is illustrative.',SUB),Sketch()])

doc=SimpleDocTemplate(str(PDF),pagesize=(W,H),leftMargin=M,rightMargin=M,topMargin=35,bottomMargin=46,
                      title='Early Product Success from Amazon Reviews - Assignment 6 Proposal',
                      author='CS6983 project team',subject='Two-page proposal and one-page Streamlit app sketch')
doc.build(story,onFirstPage=footer,onLaterPages=footer)

import re
md=['# Early Product Success from Amazon Reviews','', 'Assignment 6 proposal - English content source','']
for title,paras in sections:
    md.extend(['## '+title,''])
    for para in paras:
        s=re.sub(r'<link href="([^"]+)"[^>]*><u>(.*?)</u></link>',r'[\2](\1)',para)
        s=s.replace('<b>','**').replace('</b>','**').replace('&gt;','>').replace('&lt;','<').replace('&amp;','&')
        md.extend([s,''])
(BASE/'proposal_content.md').write_text('\n'.join(md))
print(PDF)
