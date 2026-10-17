import streamlit as st
import re
import random
from pypdf import PdfReader

# 스마트폰 반응형 UI 설정
st.set_page_config(
    page_title="🎓 소방시설관리사 2차 실전 암기카드 생성기",
    page_icon="🔥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 모바일 커스텀 CSS
st.markdown('''
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    .main .block-container {
        max-width: 520px !important;
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }
    .flashcard-box {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 2px solid #cbd5e1;
        border-radius: 20px;
        padding: 24px 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08);
        text-align: center;
        min-height: 280px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin-bottom: 15px;
        position: relative;
    }
    .card-type-badge {
        position: absolute;
        top: 14px;
        left: 16px;
        background-color: #dc2626;
        color: white;
        font-size: 0.78rem;
        font-weight: bold;
        padding: 4px 12px;
        border-radius: 12px;
    }
    .card-num-badge {
        position: absolute;
        top: 14px;
        right: 16px;
        color: #64748b;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .q-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #0f172a;
        margin-top: 18px;
        margin-bottom: 12px;
        line-height: 1.55;
        word-break: keep-all;
        text-align: left;
        width: 100%;
    }
    .a-box {
        background-color: #f1f5f9;
        border-left: 4px solid #10b981;
        padding: 14px 16px;
        border-radius: 8px;
        text-align: left;
        width: 100%;
        color: #1e293b;
        font-size: 0.98rem;
        line-height: 1.6;
        margin-top: 10px;
        word-break: keep-all;
        white-space: pre-wrap;
    }
    div.stButton > button {
        width: 100% !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        padding: 12px 0px !important;
        font-size: 0.95rem !important;
    }
</style>
''', unsafe_allow_html=True)

# 관리사 2차 기출문제 파싱 및 자동 생성 알고리즘
def parse_manager_exam_cards(raw_text):
    cards = []
    # 단락 및 조문 분할
    blocks = [b.strip() for b in re.split(r'\n(?=\d+\.|\\([5-13]\\)|[①-⑩]|제\d+조)', raw_text) if b.strip()]
    
    for block in blocks:
        lines = [l.strip() for l in block.split('\n') if l.strip()]
        if not lines:
            continue
            
        header = lines
        body_items = lines[1:] if len(lines) > 1 else []
        item_count = len(body_items)
        
        # 1. 예외 / 면제 / 제외 기준 유형 (다만, ~의 경우 제외)
        if "다만" in block or "제외" in block or "면제" in block:
            match_except = re.findall(r'(다만[^\.\n]+|제외[^\.\n]+|면제[^\.\n]+)', block)
            if match_except:
                cards.append({
                    "type": "📝 [관리사 2차] 설치제외 / 면제기준",
                    "question": f"다음 화재안전기술기준(NFTC) 관련 조문에서 **[설치제외 및 면제(단서) 기준]**을 기술하시오.\n\n📌 **대상 조문:** {header}",
                    "answer": "\n".join(match_except),
                    "original": block
                })
                
        # 2. 설치기준 / 점검항목 서술 유형 (세부 항/호가 나열된 경우)
        if item_count >= 2:
            cards.append({
                "type": "🔥 [관리사 2차] 설치기준 / 세부요건 서술",
                "question": f"다음 소방설비 관련 **[{header}]**에 대한 세부 설치기준({item_count}가지)을 기술하시오.",
                "answer": "\n".join(body_items),
                "original": block
            })
            
        # 3. 수치 및 규격 핵심 요약 유형 (면적, 거리, 높이, 데시벨 등)
        num_matches = re.findall(r'([^\.\n]*?\d+(?:\.\d+)?\s*(?:제곱미터|미터|데시벨|m|㎡|분|초|층|개|℃|kW|MPa|L/min)[^\.\n]*)', block)
        if num_matches and item_count < 2:
            cards.append({
                "type": "🎯 [관리사 2차] 수치 및 기준 단답 암기",
                "question": f"다음 조문의 **[핵심 수치 및 수량 기준]**을 서술하시오.\n\n📌 **조문:** {header}",
                "answer": "\n".join([f"• {m.strip()}" for m in num_matches]),
                "original": block
            })
            
    return cards

# 기본 예시 화재안전기술기준 (자동화재탐지설비)
SAMPLE_NFTC = """1. 자동화재탐지설비의 경계구역 설정기준
① 하나의 경계구역의 면적은 600제곱미터 이하로 하고 한 변의 길이는 50미터 이하로 할 것.
② 해당 특정소방대상물의 출입구에서 그 내부 전체가 보이는 것에 있어서는 한 변의 길이가 50미터 범위 내에서 1,000제곱미터 이하로 할 수 있다.
③ 계단·경사로·엘리베이터 승강로의 경우 수직거리는 45미터 이하마다 하나의 경계구역으로 설정할 것.

2. 수신기 설치기준
① 수신기가 설치된 장소에는 경계구역 투시도를 비치할 것.
② 경보음향은 수신기로부터 1미터 떨어진 위치에서 85데시벨 이상이어야 할 것.
③ 조작스위치는 바닥으로부터 높이 0.8미터 이상 1.5미터 이하의 위치에 설치할 것.

3. 감지기 설치제외 장소
① 천장 또는 반자의 높이가 20미터 이상인 장소. 다만, 환기구 등 유풍구로부터 1.5미터 이상 떨어진 위치에는 설치하여야 한다.
② 부식성 가스가 체류하고 있는 장소.
③ 고온도 및 저온도로서 감지기의 기능이 유지되기 어려운 장소."""

st.title("🎓 소방시설관리사 2차 실전 암기카드 생성기")
st.caption("📜 화재안전기술기준(NFTC) PDF/텍스트를 입력하시면 실제 관리사 2차 기출문제 형식으로 암기 카드를 자동 생성합니다!")

tab_input, tab_cards = st.tabs(["📥 1. PDF / 텍스트 입력", "🎴 2. 관리사 2차 암기카드"])

with tab_input:
    st.subheader("📄 1) 화재안전기준 PDF 업로드")
    uploaded_pdf = st.file_uploader("NFTC / 법령 PDF 파일을 올려주세요:", type=["pdf"])
    
    pdf_text = ""
    if uploaded_pdf is not None:
        try:
            reader = PdfReader(uploaded_pdf)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    pdf_text += extracted + "\n"
            st.success(f"✅ PDF 분석 완료! (총 {len(reader.pages)}페이지 텍스트 추출)")
        except Exception as e:
            st.error(f"❌ PDF 처리 오류: {e}")

    st.write("---")
    st.subheader("📝 2) 조문 텍스트 직접 입력 / 수정")
    
    default_val = pdf_text if pdf_text else SAMPLE_NFTC
    input_text = st.text_area("암기할 조문 내용:", value=default_val, height=220)
        
    if st.button("🚀 관리사 2차 기출 암기카드 생성하기", type="primary"):
        if not input_text.strip():
            st.warning("⚠️ 암기할 텍스트를 입력하거나 PDF를 올려주세요!")
        else:
            cards = parse_manager_exam_cards(input_text)
            st.session_state.generated_cards = cards
            st.session_state.card_idx = 0
            st.session_state.is_flipped = False
            st.session_state.known_set = set()
            st.success(f"✨ 실제 관리사 2차 패턴의 암기카드 {len(cards)}개가 생성되었습니다! [🎴 2. 관리사 2차 암기카드] 탭에서 학습하세요.")

cards = st.session_state.get("generated_cards", [])
if not cards and input_text.strip():
    st.session_state.generated_cards = parse_manager_exam_cards(input_text)
    cards = st.session_state.generated_cards

if "card_idx" not in st.session_state:
    st.session_state.card_idx = 0
if "is_flipped" not in st.session_state:
    st.session_state.is_flipped = False
if "known_set" not in st.session_state:
    st.session_state.known_set = set()

with tab_cards:
    if not cards:
        st.info("👈 먼저 [📥 1. PDF / 텍스트 입력] 탭에서 내용을 넣고 생성 버튼을 눌러주세요.")
    else:
        total_c = len(cards)
        curr_idx = st.session_state.card_idx % total_c
        curr_card = cards[curr_idx]

        known_cnt = len(st.session_state.known_set)
        prog_val = min(1.0, known_cnt / total_c)
        st.progress(prog_val)
        st.caption(f"📊 암기 진도율: {total_c}개 중 {known_cnt}개 완료 ({int(prog_val*100)}%)")

        if not st.session_state.is_flipped:
            st.markdown(f'''
            <div class="flashcard-box">
                <div class="card-type-badge">{curr_card['type']}</div>
                <div class="card-num-badge">{curr_idx + 1} / {total_c}</div>
                <div class="q-title">{curr_card['question']}</div>
                <div style="color: #94a3b8; font-size: 0.82rem; margin-top: 15px;">👆 아래 [🔄 정답 및 모범답안 보기] 버튼을 누르세요</div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
            <div class="flashcard-box" style="border-color: #10b981; background: #ffffff;">
                <div class="card-type-badge" style="background-color: #10b981;">모범답안 & 원문 해설</div>
                <div class="card-num-badge">{curr_idx + 1} / {total_c}</div>
                <div class="a-box"><b>[모범 답안]:</b>\n{curr_card['answer']}</div>
            </div>
            ''', unsafe_allow_html=True)

        col_flip, col_know = st.columns(2)
        with col_flip:
            if st.button("🔄 정답 및 모범답안 보기", type="primary"):
                st.session_state.is_flipped = not st.session_state.is_flipped
                st.rerun()
        with col_know:
            is_k = curr_idx in st.session_state.known_set
            if st.button("👍 암기완료!" if is_k else "👍 암기했어요"):
                if is_k:
                    st.session_state.known_set.remove(curr_idx)
                else:
                    st.session_state.known_set.add(curr_idx)
                st.rerun()

        st.write("")
        col_prev, col_rand, col_next = st.columns(3)
        with col_prev:
            if st.button("👈 이전"):
                st.session_state.card_idx = (st.session_state.card_idx - 1) % total_c
                st.session_state.is_flipped = False
                st.rerun()
        with col_rand:
            if st.button("🎲 섞기"):
                st.session_state.card_idx = random.randint(0, total_c - 1)
                st.session_state.is_flipped = False
                st.rerun()
        with col_next:
            if st.button("👉 다음"):
                st.session_state.card_idx = (st.session_state.card_idx + 1) % total_c
                st.session_state.is_flipped = False
                st.rerun()
