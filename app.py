import streamlit as st
import random

# 스마트폰 반응형 UI 설정
st.set_page_config(
    page_title="🎓 소방시설관리사 2차 실기 주관식 암기장",
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
        min-height: 300px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin-bottom: 15px;
        position: relative;
    }
    .card-badge {
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
    .card-num {
        position: absolute;
        top: 14px;
        right: 16px;
        color: #64748b;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .q-title {
        font-size: 1.12rem;
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
    .tip-box {
        background-color: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 10px 12px;
        border-radius: 6px;
        text-align: left;
        width: 100%;
        color: #991b1b;
        font-size: 0.88rem;
        margin-top: 10px;
        line-height: 1.5;
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

# 관리사 2차 실제 기출 엄선 주관식 문제 DB
REAL_MANAGER_CARDS = [
    {
        "id": 1,
        "subject": "점검실무행정",
        "category": "제연설비",
        "question": "화재예방, 소방시설 설치·유지 및 안전관리에 관한 법령상 '제연설비를 설치하여야 하는 특정소방대상물' 6가지를 기술하시오.",
        "answer": "① 문화 및 집회시설, 종교시설, 운동시설로서 무대부의 바닥면적이 200㎡ 이상인 것 또는 영화상영관으로서 수용인원이 100명 이상인 것\n② 지하가(터널 제외)로서 연면적 1,000㎡ 이상인 것\n③ 운수시설, 복합건축물로서 연면적 5,000㎡ 이상인 것\n④ 근린생활시설, 판매시설, 업무시설, 숙박시설, 위락시설, 다중이용업소의 영업장으로서 지하층의 바닥면적 합계가 1,000㎡ 이상인 것\n⑤ 지하층을 제외한 층수가 11층 이상인 특정소방대상물\n⑥ 휴게소로서 지하층 바닥면적 합계가 1,000㎡ 이상인 것",
        "tip": "📌 관리사 2차 단골 출제 항목으로 대상물 구분 및 바닥면적 수치(200㎡, 1,000㎡, 5,000㎡) 암기가 핵심입니다."
    },
    {
        "id": 2,
        "subject": "점검실무행정",
        "category": "제연설비",
        "question": "제연설비의 화재안전기술기준(NFTC 501)에 따라 제연설비 설치대상 중 배출구·공기유입구 설치 및 배출량 산정에서 이를 제외할 수 있는 장소 3가지를 기술하시오.",
        "answer": "① 화장실·욕실·사우나·주방·창고\n② 복도·계단실 및 부속실을 제연하는 경우 당해 복도·계단실 및 부속실\n③ 사람이 거주하지 않거나 가연성 물질이 존재하지 않는 통로 및 피트 공간",
        "tip": "📌 단서 조항 및 설치제외 장소 문제는 2차 실기 시험의 필수 암기 패턴입니다."
    },
    {
        "id": 3,
        "subject": "점검실무행정",
        "category": "소방펌프",
        "question": "소방시설관리사가 건물의 소방펌프를 점검한 결과 에어락(Air Lock) 현상이라고 판단하였다. 에어락 현상의 원인과 이에 대한 적절한 대책 5가지를 기술하시오.",
        "answer": "1. 에어락(Air Lock) 원인: 펌프 흡입측 배관에 공기가 고여 펌프의 가압 송수 기능이 마비되는 현상\n2. 적절한 대책:\n① 흡입배관의 편사부관(편심 레듀샤)을 사용하여 상부 평탄 배관 형성\n② 펌프 흡입 배관을 수조 쪽으로 1/100 이상의 올림경사로 설치\n③ 물올림장치의 신속한 수위 보충 및 물올림관 공기 빼기 밸브 작동\n④ 후드밸브 기능 점검 및 이물질 제거\n⑤ 펌프 에어 빼기 밸브(Air Vent)를 개방하여 내부 공기 완전 배출",
        "tip": "📌 점검 실무 및 고장 진단 기출 문제로 현장 대책 5가지를 명확히 기술해야 합니다."
    },
    {
        "id": 4,
        "subject": "점검실무행정",
        "category": "자탐설비",
        "question": "P형 수신기에 연결된 지구경종이 화재 신호 발생 시에도 작동되지 않는 경우, 그 원인 5가지를 기술하시오.",
        "answer": "① 수신기 내 지구경종 출력 단자의 출력 전압 미발생 (수신기 기판 고장)\n② 수신기 경종 정지 스위치가 눌려진 상태 (작동 정지)\n③ 지구경종 음향장치 자체의 코일 단선 또는 구조적 고장\n④ 수신기에서 지구경종까지의 단자대 연결 배선 단선 또는 접촉 불량\n⑤ 지구경종용 퓨즈 단선 또는 예비전원 결선 불량",
        "tip": "📌 수신기 및 경보 설비 고장 원인 분석 문제로 관리사 2차의 대표적 단답형 문제입니다."
    },
    {
        "id": 5,
        "subject": "설계 및 시공",
        "category": "스프링클러",
        "question": "스프링클러소화설비에서 저압건식밸브 2차측 설정압력이 낮을 경우 얻을 수 있는 장점 4가지를 기술하시오.",
        "answer": "① 화재 발생 시 2차측 압축공기의 신속한 배출로 헤드 방수 지연시간 단축\n② 압축공기 충전을 위한 공기압축기(Compressor)의 용량 및 소모 전력 절감\n③ 배관 내 높은 공기압력으로 인한 밸브 및 배관 접속부의 누설(Leak) 위험 감소\n④ 건식밸브 오작동 시 배관 수격작용(Water Hammering) 충격 완화",
        "tip": "📌 건식 스프링클러설비의 구조와 작동 원리를 묻는 2차 설계·시공 핵심 문제입니다."
    },
    {
        "id": 6,
        "subject": "점검실무행정",
        "category": "종합정밀점검",
        "question": "다중이용업소의 종합정밀점검 시 '가스누설경보기'에 대한 주요 점검항목 5가지를 기술하시오.",
        "answer": "① 가스누설경보기의 설치 위치 및 적정성 여부 (가스 비중에 따른 높이)\n② 전원 표시등의 점등 상태 및 예비전원의 정상 작동 여부\n③ 가스 탐지부의 오염, 훼손 및 감지 기능 작동 여부\n④ 경보음량의 적정성 (1m 거리에서 70dB 이상, 주보안경종 85dB 이상)\n⑤ 차단밸브 연동 상태 및 가스 차단장치의 정상 작동 여부",
        "tip": "📌 종합정밀점검표에 기반한 점검항목 서술 문제입니다."
    },
    {
        "id": 7,
        "subject": "점검실무행정",
        "category": "가스계소화설비",
        "question": "이산화탄소 소화설비의 종합정밀점검 시 '전원 및 배선'에 대한 점검항목 5가지를 기술하시오.",
        "answer": "① 상용전원 및 예비전원의 자동 절환 작동 상태\n② 비상전원의 용량 적정성 (20분 이상 작동 자급전원)\n③ 제어반 및 수신기 간 배선의 개별 배선 및 내화·내열성 여부\n④ 감지기 회로의 도통시험 및 절연저항 상태 적정 여부\n⑤ 솔레노이드 밸브(기동장치) 기동 배선의 단선 감시 상태",
        "tip": "📌 가스계 소화설비 전원·배선 점검항목 5가지 서술형입니다."
    },
    {
        "id": 8,
        "subject": "설계 및 시공",
        "category": "자탐설비",
        "question": "자동화재탐지설비의 광전식분리형감지기 설치기준 6가지를 기술하시오.",
        "answer": "① 감지기와 광원축은 벽면으로부터 0.6m 이상 떨어진 위치에 설치할 것\n② 감지기의 광원축 높이는 천장 등 높이의 80% 이상일 것\n③ 감지기의 광원축 길이는 공칭감시거리 범위 이내일 것\n④ 송광부와 수광부는 뒷벽으로부터 1m 이내 위치에 설치할 것\n⑤ 광원축에 햇빛이 직접 비치지 아니하는 장소에 설치할 것\n⑥ 송광부와 수광부는 설치 벽면에 견고하게 고정할 것",
        "tip": "📌 감지기 세부 설치기준 6가지를 묻는 관리사 2차 서술 기출입니다."
    }
]

# 세션 상태 관리
if "card_idx" not in st.session_state:
    st.session_state.card_idx = 0
if "is_flipped" not in st.session_state:
    st.session_state.is_flipped = False
if "known_set" not in st.session_state:
    st.session_state.known_set = set()
if "selected_subject" not in st.session_state:
    st.session_state.selected_subject = "전체보기"

st.title("🎓 소방시설관리사 2차 실기 주관식 암기장")
st.caption("🔥 기출 소스 분석 기반 100% 실전 2차 주관식 서술형·단답형 모범답안 암기 앱")

tab_app, tab_custom = st.tabs(["🎴 관리사 2차 기출 암기장", "➕ 사용자 정의 조문 입력"])

with tab_app:
    subjects = ["전체보기", "점검실무행정", "설계 및 시공"]
    subj_choice = st.selectbox("📚 과목 선택:", subjects, index=subjects.index(st.session_state.selected_subject))
    
    if subj_choice != st.session_state.selected_subject:
        st.session_state.selected_subject = subj_choice
        st.session_state.card_idx = 0
        st.session_state.is_flipped = False
        st.rerun()

    active_cards = REAL_MANAGER_CARDS if subj_choice == "전체보기" else [c for c in REAL_MANAGER_CARDS if c["subject"] == subj_choice]
    
    total_c = len(active_cards)
    curr_idx = st.session_state.card_idx % total_c
    curr_card = active_cards[curr_idx]

    # 진도율
    known_cnt = len([c for c in active_cards if c["id"] in st.session_state.known_set])
    prog_val = min(1.0, known_cnt / total_c)
    st.progress(prog_val)
    st.caption(f"📊 암기 진도율: {total_c}개 중 {known_cnt}개 암기 완료 ({int(prog_val*100)}%)")

    # 카드 표시
    if not st.session_state.is_flipped:
        st.markdown(f'''
        <div class="flashcard-box">
            <div class="card-badge">[{curr_card['subject']}] {curr_card['category']}</div>
            <div class="card-num">{curr_idx + 1} / {total_c}</div>
            <div class="q-title"><b>Q.</b> {curr_card['question']}</div>
            <div style="color: #94a3b8; font-size: 0.82rem; margin-top: 15px;">👆 아래 [🔄 답안 및 해설 보기]를 누르세요</div>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
        <div class="flashcard-box" style="border-color: #10b981; background: #ffffff;">
            <div class="card-badge" style="background-color: #10b981;">모범답안 & 핵심 요약</div>
            <div class="card-num">{curr_idx + 1} / {total_c}</div>
            <div class="a-box"><b>[모범 답안]:</b>\n{curr_card['answer']}</div>
            <div class="tip-box">{curr_card['tip']}</div>
        </div>
        ''', unsafe_allow_html=True)

    col_flip, col_know = st.columns(2)
    with col_flip:
        if st.button("🔄 답안 및 해설 보기", type="primary"):
            st.session_state.is_flipped = not st.session_state.is_flipped
            st.rerun()
    with col_know:
        is_k = curr_card['id'] in st.session_state.known_set
        if st.button("👍 암기완료!" if is_k else "👍 암기했어요"):
            if is_k:
                st.session_state.known_set.remove(curr_card['id'])
            else:
                st.session_state.known_set.add(curr_card['id'])
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

with tab_custom:
    st.subheader("➕ 나만의 2차 주관식 암기 카드 추가하기")
    st.caption("질문과 모범답안을 직접 입력하여 정밀 암기 카드를 추가할 수 있습니다.")
    
    c_subj = st.selectbox("과목:", ["점검실무행정", "설계 및 시공"])
    c_cat = st.text_input("설비 카테고리 (예: 제연설비, 수신기):", "화재안전기술기준")
    c_q = st.text_area("주관식 질문 (Q):", placeholder="예: 자동화재탐지설비의 경계구역 설정기준 3가지를 기술하시오.")
    c_a = st.text_area("모범 답안 (A):", placeholder="① 하나의 경계구역 면적은 600㎡ 이하...\n② 한 변의 길이는 50m 이하...")
    c_tip = st.text_input("출제 팁 / 메모:", "📌 핵심 수치 및 요건 숙지")
    
    if st.button("✨ 카드로 추가하기"):
        if c_q.strip() and c_a.strip():
            new_card = {
                "id": len(REAL_MANAGER_CARDS) + 1,
                "subject": c_subj,
                "category": c_cat,
                "question": c_q,
                "answer": c_a,
                "tip": c_tip
            }
            REAL_MANAGER_CARDS.append(new_card)
            st.success("🎉 새로운 주관식 암기카드가 정상 등록되었습니다!")
        else:
            st.warning("⚠️ 질문과 답안을 모두 입력해 주세요.")
