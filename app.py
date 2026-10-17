import streamlit as st
import re
import random
from pypdf import PdfReader

# 스마트폰 반응형 UI 설정
st.set_page_config(
    page_title="🔥 소방시설관리사 기출패턴 자동 암기카드 생성기",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 모바일 커스텀 CSS 스타일링
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
        background-color: #ef4444;
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
        margin-top: 15px;
        margin-bottom: 12px;
        line-height: 1.5;
        word-break: keep-all;
    }
    .a-box {
        background-color: #f1f5f9;
        border-left: 4px solid #10b981;
        padding: 12px 15px;
        border-radius: 8px;
        text-align: left;
        width: 100%;
        color: #1e293b;
        font-weight: bold;
        font-size: 1.05rem;
        margin-top: 10px;
        word-break: keep-all;
    }
    .orig-box {
        background-color: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 10px 12px;
        border-radius: 8px;
        text-align: left;
        width: 100%;
        color: #7f1d1d;
        font-size: 0.88rem;
        margin-top: 10px;
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

# 기본 예시 화재안전기술기준 (NFTC 201)
SAMPLE_NFTC = """1. 하나의 경계구역의 면적은 600제곱미터 이하로 하고 한 변의 길이는 50미터 이하로 할 것. 다만, 해당 특정소방대상물의 출입구에서 그 내부 전체가 보이는 것에 있어서는 한 변의 길이가 50미터 범위 내에서 1,000제곱미터 이하로 할 수 있다.
2. 계단·경사로·엘리베이터 승강로·리프트·수식배관 피트·덕트 피트 등의 경우 수직거리는 45미터 이하마다 하나의 경계구역으로 설정할 것.
3. 자동화재탐지설비의 감지기는 천장 또는 반자의 실내에 면하는 부분에 설치하고, 환기구 등 유풍구로부터 1.5미터 이상 떨어진 위치에 설치할 것.
4. 광전식 분리형 감지기의 감지기와 광원축은 벽면으로부터 0.6미터 이상 떨어진 위치에 설치할 것.
5. 수신기 설치기준: 수신기가 설치된 장소에는 경계구역 투시도를 비치하고, 경보음향은 1미터 떨어진 위치에서 85데시벨 이상이어야 하며, 조작스위치는 바닥으로부터 높이 0.8미터 이상 1.5미터 이하의 위치에 설치할 것."""

# 관리사 기출 패턴 자동 생성 알고리즘
def generate_cards_from_text(raw_text):
    lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
    cards = []
    
    for idx, line in enumerate(lines):
        # 1. 수치 괄호 채우기 패턴 (숫자 + 단위 자동 탐지)
        num_matches = list(re.finditer(r'(\d+(?:\.\d+)?\s*(?:제곱미터|미터|데시벨|m|㎡|분|초|층|개|℃|kW|MPa|Pa|%|L/min|l/min))', line))
        
        if num_matches:
            blanked_line = line
            answers = []
            for i, match in enumerate(num_matches):
                val = match.group(1)
                answers.append(f"({i+1}) {val}")
                blanked_line = blanked_line.replace(val, f" (  [{i+1}]  ) ", 1)
            
            cards.append({
                "type": "📌 [기출패턴 1] 핵심수치 괄호 채우기",
                "question": f"다음 화재안전기준 조문의 빈칸 ( [ 1 ], [ 2 ] ... )에 들어갈 올바른 수치/단위를 답하시오.\n\n\"{blanked_line}\"",
                "answer": " / ".join(answers),
                "original": line
            })
            
        # 2. 설치기준 / 점검항목 패턴
        if any(kw in line for kw in ["설치기준", "점검", "조건", "면제", "제외"]):
            q_title = line.split(':') if ':' in line else f"조문 #{idx+1} 핵심 요건"
            cards.append({
                "type": "📝 [기출패턴 2] 설치기준 / 점검항목 단답형",
                "question": f"[{q_title}]에 관련된 국가화재안전기술기준의 세부 규정 내용을 기술하시오.",
                "answer": line,
                "original": line
            })
            
        # 3. O/X 약점 유도 패턴
        if "이하" in line or "이상" in line:
            fake_line = line
            if "이하" in line:
                fake_line = fake_line.replace("이하", "이상", 1)
            elif "이상" in line:
                fake_line = fake_line.replace("이상", "이하", 1)
                
            cards.append({
                "type": "⭕❌ [기출패턴 3] O/X 약점 검증 퀴즈",
                "question": f"다음 지문의 O / X 여부를 판단하시오.\n\n\"{fake_line}\"",
                "answer": "❌ (오답 지문임)\n\n올바른 조문 원문: " + line,
                "original": line
            })
            
    return cards

st.title("🎓 소방시설관리사 기출패턴 암기카드 생성기")
st.caption("📜 법령/기술기준 텍스트를 직접 입력하거나 PDF 파일을 업로드하면 기출 스타일 암기 카드를 자동 생성합니다!")

tab_input, tab_cards, tab_quiz = st.tabs(["📥 1. 텍스트/PDF 업로드", "🎴 2. 기출 암기 플래시카드", "📝 3. 실전 퀴즈 테스트"])

with tab_input:
    st.subheader("📄 1) PDF 파일 업로드 (선택사항)")
    uploaded_pdf = st.file_uploader("화재안전기술기준 / 법령 PDF 파일을 올려주세요:", type=["pdf"])
    
    pdf_text = ""
    if uploaded_pdf is not None:
        try:
            reader = PdfReader(uploaded_pdf)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    pdf_text += extracted + "\n"
            st.success(f"✅ PDF 파일 분석 완료! (총 {len(reader.pages)}페이지에서 텍스트를 성공적으로 추출했습니다.)")
        except Exception as e:
            st.error(f"❌ PDF 파일 처리 중 오류가 발생했습니다: {e}")

    st.write("---")
    st.subheader("📝 2) 텍스트 직접 입력 / 수정")
    
    use_sample = st.checkbox("💡 예시 화재안전기술기준(자동화재탐지설비) 텍스트 불러오기", value=False if pdf_text else True)
    
    default_val = pdf_text if pdf_text else (SAMPLE_NFTC if use_sample else "")
    
    input_text = st.text_area("암기할 조문 텍스트 (PDF 내용이 자동 입력되거나 직접 수정할 수 있습니다):", value=default_val, height=220)
        
    if st.button("🚀 기출패턴 암기카드 생성하기", type="primary"):
        if not input_text.strip():
            st.warning("⚠️ 암기할 텍스트를 입력하거나 PDF 파일을 업로드해 주세요!")
        else:
            cards = generate_cards_from_text(input_text)
            st.session_state.generated_cards = cards
            st.session_state.card_idx = 0
            st.session_state.is_flipped = False
            st.session_state.known_set = set()
            st.success(f"✨ 총 {len(cards)}개의 기출패턴 암기카드가 생성되었습니다! [🎴 2. 기출 암기 플래시카드] 탭에서 확인해 보세요.")

cards = st.session_state.get("generated_cards", [])

if not cards and input_text.strip():
    st.session_state.generated_cards = generate_cards_from_text(input_text)
    cards = st.session_state.generated_cards

if "card_idx" not in st.session_state:
    st.session_state.card_idx = 0
if "is_flipped" not in st.session_state:
    st.session_state.is_flipped = False
if "known_set" not in st.session_state:
    st.session_state.known_set = set()

with tab_cards:
    if not cards:
        st.info("👈 먼저 [📥 1. 텍스트/PDF 업로드] 탭에서 PDF를 업로드하거나 텍스트를 입력하고 생성 버튼을 눌러주세요.")
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
                <div class="card-type-badge">{curr_card['type']}</div>
                <div class="card-num-badge">{curr_idx + 1} / {total_c}</div>
                <div class="q-title">{curr_card['question']}</div>
                <div style="color: #94a3b8; font-size: 0.82rem; margin-top: 10px;">👆 아래 [🔄 정답 / 원문 보기] 버튼을 누르세요</div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
            <div class="flashcard-box" style="border-color: #10b981; background: #ffffff;">
                <div class="card-type-badge" style="background-color: #10b981;">정답 및 원문 해설</div>
                <div class="card-num-badge">{curr_idx + 1} / {total_c}</div>
                <div class="a-box"><b>[정답]:</b> {curr_card['answer']}</div>
                <div class="orig-box"><b>[원문 조문]:</b> {curr_card['original']}</div>
            </div>
            ''', unsafe_allow_html=True)

        col_flip, col_know = st.columns(2)
        with col_flip:
            if st.button("🔄 정답 / 원문 보기", type="primary"):
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

with tab_quiz:
    if not cards:
        st.info("👈 먼저 [📥 1. 텍스트/PDF 업로드] 탭에서 PDF를 업로드하거나 텍스트를 입력해 주세요.")
    else:
        st.subheader("📝 생성된 카드로 실전 테스트")
        quiz_idx = st.session_state.get("quiz_idx", 0) % len(cards)
        q_card = cards[quiz_idx]
        
        st.markdown(f"**[문제 {quiz_idx + 1}]** {q_card['type']}")
        st.info(q_card['question'])
        
        user_ans = st.text_input("내가 생각하는 정답을 입력해 보세요:", key=f"user_ans_{quiz_idx}")
        
        if st.button("🎯 정답 확인하기"):
            st.success(f"**[정답]:** {q_card['answer']}")
            st.caption(f"**[원문]:** {q_card['original']}")
            
        if st.button("➡️ 다음 문제 풀기"):
            st.session_state.quiz_idx = quiz_idx + 1
            st.rerun()