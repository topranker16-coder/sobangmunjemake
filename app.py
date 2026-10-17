import streamlit as st
import json
import re
import random
from pypdf import PdfReader
import google.generativeai as genai

# 스마트폰 반응형 UI 설정
st.set_page_config(
    page_title="🎓 소방시설관리사 2차 AI 맞춤형 암기장",
    page_icon="🔥",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS 스타일링
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
        min-height: 300px;
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
        font-size: 1.1rem;
        font-weight: 800;
        color: #0f172a;
        margin-top: 22px;
        margin-bottom: 12px;
        line-height: 1.6;
        text-align: left;
        width: 100%;
        white-space: pre-wrap;
        word-break: keep-all;
    }
    .a-box {
        background-color: #f1f5f9;
        border-left: 5px solid #10b981;
        padding: 16px;
        border-radius: 10px;
        text-align: left;
        width: 100%;
        color: #0f172a;
        font-size: 0.98rem;
        line-height: 1.65;
        margin-top: 10px;
        white-space: pre-wrap;
        word-break: keep-all;
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

# --- 사이드바 AI 설정 ---
st.sidebar.title("🤖 AI 샤프 문제 생성 설정")
st.sidebar.caption("Google AI Studio에서 무료 Gemini API Key를 발급받아 입력하시면, 최신 법령/기술기준 PDF를 넣었을 때 AI가 샤프하게 관리사 2차 문제를 자동 추출합니다!")

api_key = st.sidebar.text_input("Gemini API Key 입력:", type="password")

if api_key:
    st.sidebar.success("⚡ AI 엔진 활성화 완료!")
else:
    st.sidebar.info("💡 API Key가 없으면 기본 규칙 파서가 작동합니다.")

# AI 문제 생성 함수 (Gemini API 기반)
def generate_cards_with_ai(text_content, key):
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        너는 대한민국 소방시설관리사 2차 실기시험(점검실무행정, 설계및시공) 전문 출제위원이다.
        아래 제공된 [화재안전기술기준/소방법령 텍스트]를 정밀 분석하여, 실제 2차 주관식 시험 스타일에 맞는 암기 문제와 모범답안 목록을 JSON 형식으로 작성해라.

        [출제 지침]:
        1. 단순 숫자 뚫기나 부칙 시행일 같은 무의미한 문장은 절대 제외한다.
        2. 주요 출제 유형:
           - 유형 1: 세부 설치기준/점검항목 N가지 서술
           - 유형 2: 단서 조항(다만, 제외, 면제) 서술
           - 유형 3: 핵심 수치 및 기준 단답 서술
        3. 답안은 실제 시험에서 채점하기 용이하도록 '①, ②, ③' 번호목차 형태로 명확하고 깔끔하게 작성한다.
        4. 결과는 반드시 아래 JSON 배열 포맷으로만 응답해라 (다른 설명 금지):

        [
          {{
            "type": "🔥 [관리사 2차] 세부 설치기준 서술",
            "question": "질문 내용...",
            "answer": "① 모범답안 1\n② 모범답안 2..."
          }}
        ]

        [화재안전기술기준/소방법령 텍스트]:
        {text_content[:6000]}
        """
        
        response = model.generate_content(prompt)
        res_text = response.text
        
        # JSON 추출
        json_match = re.search(r'\\[.*\\]', res_text, re.DOTALL)
        if json_match:
            cards = json.loads(json_match.group(0))
            return cards
        else:
            st.error("AI 응답을 JSON으로 해석하지 못했습니다. 다시 시도해주세요.")
            return None
    except Exception as e:
        st.error(f"AI 문제 생성 중 오류가 발생했습니다: {e}")
        return None

# 일반 규칙 기반 백업 파서
def parse_fallback_cards(raw_text):
    cards = []
    lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
    
    current_title = "화재안전기술기준 핵심 조문"
    body_acc = []
    
    for line in lines:
        if any(line.startswith(p) for p in ["제", "1.", "2.", "3.", "4.", "5.", "①", "②", "③"]):
            if body_acc and len(body_acc) >= 2:
                cards.append({
                    "type": "🔥 [관리사 2차] 세부 기준 서술",
                    "question": f"다음 **[{current_title}]**의 세부 기준을 기술하시오.",
                    "answer": "\n".join(body_acc)
                })
            current_title = line
            body_acc = []
        else:
            body_acc.append(f"• {line}")
            
    if body_acc and len(body_acc) >= 2:
        cards.append({
            "type": "🔥 [관리사 2차] 세부 기준 서술",
            "question": f"다음 **[{current_title}]**의 세부 기준을 기술하시오.",
            "answer": "\n".join(body_acc)
        })
        
    return cards if cards else [{
        "type": "🎯 [관리사 2차] 주요 조문 암기",
        "question": "입력된 조문의 주요 내용을 기술하시오.",
        "answer": raw_text[:300]
    }]

st.title("🎓 소방시설관리사 2차 AI 스마트 암기장")
st.caption("📜 최신 화재안전기술기준(NFTC) PDF/텍스트를 입력하시면 AI가 샤프하게 관리사 2차 주관식 문제를 자동 생성합니다!")

tab_input, tab_cards = st.tabs(["📥 1. 최신 법령/PDF 입력", "🎴 2. AI 샤프 암기카드"])

with tab_input:
    st.subheader("📄 1) 최신 화재안전기준 PDF 업로드")
    uploaded_pdf = st.file_uploader("개정된 NFTC / 법령 PDF 파일:", type=["pdf"])
    
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
    input_text = st.text_area("암기할 조문 내용을 입력하세요:", value=pdf_text, height=220, placeholder="최신 법령 조문을 복사해서 붙여넣으세요...")
        
    if st.button("🚀 AI 샤프 문제 생성 시작하기", type="primary"):
        if not input_text.strip():
            st.warning("⚠️ 암기할 텍스트를 입력하거나 PDF를 업로드해 주세요!")
        else:
            with st.spinner("🤖 AI가 최신 법령 맥락을 분석하여 샤프한 관리사 2차 문제를 생성 중입니다..."):
                if api_key:
                    cards = generate_cards_with_ai(input_text, api_key)
                else:
                    cards = parse_fallback_cards(input_text)
                    st.info("💡 Gemini API Key를 입력하시면 AI가 훨씬 정교하게 문제를 생성합니다.")
                
                if cards:
                    st.session_state.ai_generated_cards = cards
                    st.session_state.card_idx = 0
                    st.session_state.is_flipped = False
                    st.session_state.known_set = set()
                    st.success(f"✨ 샤프한 관리사 2차 문제 {len(cards)}개가 성공적으로 생성되었습니다!")

cards = st.session_state.get("ai_generated_cards", [])

if "card_idx" not in st.session_state:
    st.session_state.card_idx = 0
if "is_flipped" not in st.session_state:
    st.session_state.is_flipped = False
if "known_set" not in st.session_state:
    st.session_state.known_set = set()

with tab_cards:
    if not cards:
        st.info("👈 [📥 1. 최신 법령/PDF 입력] 탭에서 최신 기준을 넣고 [🚀 AI 샤프 문제 생성 시작하기] 버튼을 눌러주세요.")
    else:
        total_c = len(cards)
        curr_idx = st.session_state.card_idx % total_c
        curr_card = cards[curr_idx]

        known_cnt = len(st.session_state.known_set)
        prog_val = min(1.0, known_cnt / total_c)
        st.progress(prog_val)
        st.caption(f"📊 암기 진도율: {total_c}개 중 {known_cnt}개 암기 완료 ({int(prog_val*100)}%)")

        if not st.session_state.is_flipped:
            st.markdown(f'''
            <div class="flashcard-box">
                <div class="card-type-badge">{curr_card.get('type', '관리사 2차')}</div>
                <div class="card-num-badge">{curr_idx + 1} / {total_c}</div>
                <div class="q-title"><b>Q.</b> {curr_card.get('question', '')}</div>
                <div style="color: #94a3b8; font-size: 0.82rem; margin-top: 15px;">👆 아래 [🔄 모범답안 보기] 버튼을 누르세요</div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
            <div class="flashcard-box" style="border-color: #10b981; background: #ffffff;">
                <div class="card-type-badge" style="background-color: #10b981;">AI 모범답안</div>
                <div class="card-num-badge">{curr_idx + 1} / {total_c}</div>
                <div class="a-box"><b>[모범 답안]:</b>\n{curr_card.get('answer', '')}</div>
            </div>
            ''', unsafe_allow_html=True)

        col_flip, col_know = st.columns(2)
        with col_flip:
            if st.button("🔄 모범답안 보기", type="primary"):
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
