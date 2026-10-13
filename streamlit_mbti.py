"""A lightweight MBTI-style preference explorer built with Streamlit.

Run locally with:
    streamlit run streamlit_mbti.py

This is an informal self-reflection activity, not an official or validated
personality assessment.
"""

import math
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="MBTI 성향 탐색기",
    page_icon="🧭",
    layout="centered",
)

st.markdown(
    """
    <style>
    div[data-testid="stButton"] button {
        border-radius: 14px;
        transition: transform 120ms ease, box-shadow 120ms ease;
    }
    div.st-key-card_option_0 button,
    div.st-key-card_option_1 button {
        min-height: 126px !important;
        height: 100% !important;
        padding: 22px !important;
        text-align: left !important;
        white-space: normal !important;
        justify-content: flex-start !important;
        align-items: center !important;
        font-size: 1.08rem !important;
        line-height: 1.55 !important;
        border-radius: 18px !important;
        box-shadow: 0 3px 12px rgba(31, 41, 55, 0.07);
    }
    div.st-key-card_option_0 button:hover,
    div.st-key-card_option_1 button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(31, 41, 55, 0.12);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Each dimension has three balanced, situational questions. The first option
# maps to the first letter shown in the axis; the second maps to the second.
QUESTIONS = [
    {
        "id": "ei_1",
        "axis": "에너지 방향",
        "pair": ("I", "E"),
        "prompt": "사람들과 시간을 보낸 뒤, 나는 보통 어떻게 회복하나요?",
        "options": [
            ("I", "혼자 조용히 쉬며 에너지를 되찾는다"),
            ("E", "가까운 사람과 이야기를 나누며 활력을 얻는다"),
        ],
    },
    {
        "id": "ei_2",
        "axis": "에너지 방향",
        "pair": ("I", "E"),
        "prompt": "새로운 문제를 생각할 때 나는 어떻게 시작하나요?",
        "options": [
            ("I", "먼저 혼자 생각을 정리한 뒤 의견을 나눈다"),
            ("E", "누군가와 이야기하며 생각을 발전시킨다"),
        ],
    },
    {
        "id": "ei_3",
        "axis": "에너지 방향",
        "pair": ("I", "E"),
        "prompt": "모임에서 나는 어떤 편인가요?",
        "options": [
            ("I", "분위기를 살피다가 생각이 정리되면 참여한다"),
            ("E", "대화에 먼저 참여하며 생각을 바로 표현한다"),
        ],
    },
    {
        "id": "sn_1",
        "axis": "정보 인식",
        "pair": ("S", "N"),
        "prompt": "새로운 도구를 배울 때 더 도움이 되는 것은 무엇인가요?",
        "options": [
            ("S", "구체적인 예시와 단계별 사용법"),
            ("N", "작동 원리와 전체 구조에 대한 설명"),
        ],
    },
    {
        "id": "sn_2",
        "axis": "정보 인식",
        "pair": ("S", "N"),
        "prompt": "새로운 과제를 맡으면 어디에 먼저 관심이 가나요?",
        "options": [
            ("S", "지금 확인할 수 있는 조건과 세부 사항"),
            ("N", "앞으로 확장할 수 있는 가능성과 방향"),
        ],
    },
    {
        "id": "sn_3",
        "axis": "정보 인식",
        "pair": ("S", "N"),
        "prompt": "어떤 일을 설명할 때 나는 주로 무엇을 말하나요?",
        "options": [
            ("S", "실제로 있었던 일과 구체적인 사례"),
            ("N", "그 일에서 발견한 의미와 반복되는 패턴"),
        ],
    },
    {
        "id": "tf_1",
        "axis": "판단 기준",
        "pair": ("T", "F"),
        "prompt": "두 가지 안 중 하나를 선택해야 할 때 더 먼저 보는 것은 무엇인가요?",
        "options": [
            ("T", "기준의 일관성과 논리적 근거"),
            ("F", "관련된 사람에게 미칠 영향과 중요하게 여기는 가치"),
        ],
    },
    {
        "id": "tf_2",
        "axis": "판단 기준",
        "pair": ("T", "F"),
        "prompt": "팀원에게 개선점을 전달할 때 나는 보통 어떻게 하나요?",
        "options": [
            ("T", "고칠 점을 명확하고 직접적으로 말한다"),
            ("F", "상대의 상황을 고려해 전달 방식과 순서를 조절한다"),
        ],
    },
    {
        "id": "tf_3",
        "axis": "판단 기준",
        "pair": ("T", "F"),
        "prompt": "팀 내 의견이 갈리면 무엇을 먼저 확인하나요?",
        "options": [
            ("T", "어떤 주장이 근거와 논리에 더 잘 맞는지"),
            ("F", "각 선택이 사람들에게 어떤 영향을 주는지"),
        ],
    },
    {
        "id": "jp_1",
        "axis": "생활 방식",
        "pair": ("J", "P"),
        "prompt": "프로젝트를 시작할 때 나는 어떻게 하는 편인가요?",
        "options": [
            ("J", "주요 일정과 단계를 정해두면 마음이 편하다"),
            ("P", "목표를 정한 뒤 진행하면서 방법을 조정하는 편이 편하다"),
        ],
    },
    {
        "id": "jp_2",
        "axis": "생활 방식",
        "pair": ("J", "P"),
        "prompt": "약속이나 여행 계획을 세울 때 더 선호하는 것은 무엇인가요?",
        "options": [
            ("J", "장소와 시간을 미리 정해두는 것"),
            ("P", "큰 틀만 정하고 상황에 따라 선택하는 것"),
        ],
    },
    {
        "id": "jp_3",
        "axis": "생활 방식",
        "pair": ("J", "P"),
        "prompt": "여러 작업이 남아 있을 때 나는 어떻게 하는 편인가요?",
        "options": [
            ("J", "하나를 마무리한 뒤 다음 작업으로 넘어간다"),
            ("P", "상황에 따라 여러 작업을 오가며 진행한다"),
        ],
    },
]


LETTER_GUIDE = {
    "I": "혼자 생각을 정리하고, 조용한 환경에서 에너지를 회복하는 쪽으로 답했어요.",
    "E": "대화와 상호작용을 통해 생각을 발전시키고, 사람들과 함께할 때 활력을 얻는 쪽으로 답했어요.",
    "S": "구체적인 정보와 실제 사례, 확인 가능한 세부 사항에 주목하는 쪽으로 답했어요.",
    "N": "전체 구조와 의미, 앞으로의 가능성과 패턴에 주목하는 쪽으로 답했어요.",
    "T": "일관된 기준과 논리, 근거를 중심으로 판단하는 쪽으로 답했어요.",
    "F": "사람에게 미치는 영향과 관계, 중요하게 여기는 가치를 함께 고려하는 쪽으로 답했어요.",
    "J": "일정을 정리하고 계획을 세워 차근차근 마무리하는 쪽으로 답했어요.",
    "P": "상황에 따라 선택지를 열어두고 진행 중에 조정하는 쪽으로 답했어요.",
}


def initialize_state():
    if "current_index" not in st.session_state:
        st.session_state.current_index = 0
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "completed" not in st.session_state:
        st.session_state.completed = False


def restart_test():
    for question in QUESTIONS:
        st.session_state.pop(f"choice_{question['id']}", None)
    st.session_state.current_index = 0
    st.session_state.answers = {}
    st.session_state.completed = False


def calculate_results(answers):
    results = []
    mbti = []

    for start in range(0, len(QUESTIONS), 3):
        group = QUESTIONS[start : start + 3]
        first, second = group[0]["pair"]
        counts = {first: 0, second: 0}
        for question in group:
            counts[answers[question["id"]]] += 1

        winner = first if counts[first] > counts[second] else second
        winner_count = counts[winner]
        mbti.append(winner)
        results.append(
            {
                "axis": group[0]["axis"],
                "pair": group[0]["pair"],
                "winner": winner,
                "count": winner_count,
                "total": len(group),
                # This is answer consistency, not a validated measure of
                # personality strength.
                "consistency": winner_count / len(group) * 100,
            }
        )

    return "".join(mbti), results


def make_radar_svg(results):
    """Build a dependency-free SVG radar chart of within-axis answer agreement."""
    width, height = 500, 500
    cx, cy, radius = 250, 250, 145
    angles = [-math.pi / 2, 0, math.pi / 2, math.pi]

    def point(value, angle):
        scaled_radius = radius * value / 100
        return (
            cx + scaled_radius * math.cos(angle),
            cy + scaled_radius * math.sin(angle),
        )

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        'role="img" aria-label="네 가지 성향 차원의 응답 일치율 방사형 그래프">',
        '<rect width="100%" height="100%" rx="18" fill="#ffffff"/>',
    ]

    # Four diamond-shaped guide rings.
    for level in (25, 50, 75, 100):
        coords = [point(level, angle) for angle in angles]
        points = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
        svg.append(
            f'<polygon points="{points}" fill="none" stroke="#e5e7eb" stroke-width="1"/>'
        )
        top_x, top_y = point(level, angles[0])
        svg.append(
            f'<text x="{top_x + 5:.1f}" y="{top_y + 4:.1f}" '
            'font-size="10" fill="#9ca3af">'
            f"{level}</text>"
        )

    for angle in angles:
        x, y = point(100, angle)
        svg.append(
            f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" '
            'stroke="#d1d5db" stroke-width="1"/>'
        )

    values = [item["consistency"] for item in results]
    coords = [point(value, angle) for value, angle in zip(values, angles)]
    polygon_points = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
    svg.append(
        f'<polygon points="{polygon_points}" fill="#8b5cf6" fill-opacity="0.22" '
        'stroke="#7c3aed" stroke-width="3" stroke-linejoin="round"/>'
    )
    for (x, y), value in zip(coords, values):
        svg.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#7c3aed" '
            'stroke="#ffffff" stroke-width="2">'
            f'<title>{value:.0f}%</title></circle>'
        )

    # Labels sit outside the four chart vertices.
    labels = [
        (250, 28, "middle", 46),
        (465, 246, "end", 266),
        (250, 455, "middle", 473),
        (35, 246, "start", 266),
    ]
    for item, (x, y, anchor, sub_y) in zip(results, labels):
        svg.append(
            f'<text x="{x}" y="{y}" text-anchor="{anchor}" '
            'font-family="sans-serif" font-size="13" font-weight="700" fill="#374151">'
            f'{item["axis"]}</text>'
        )
        svg.append(
            f'<text x="{x}" y="{sub_y}" text-anchor="{anchor}" '
            'font-family="sans-serif" font-size="11" fill="#6b7280">'
            f'{item["winner"]} · {item["count"]}/{item["total"]} 응답</text>'
        )

    svg.append("</svg>")
    return "".join(svg)


def show_result():
    mbti, results = calculate_results(st.session_state.answers)

    st.progress(1.0, text="모든 문항에 답했어요")
    st.title(f"당신의 응답 경향은 **{mbti}**")
    st.write(
        "아래 설명은 이번 답변에서 더 많이 선택한 방향을 요약한 거예요. "
        "사람의 성격을 확정하거나 평가하는 결과는 아닙니다."
    )

    st.subheader("네 가지 차원별 응답 경향")
    for item in results:
        st.markdown(f"**{item['axis']} · {item['winner']}**")
        st.write(LETTER_GUIDE[item["winner"]])

    st.subheader("차원별 응답 일치율")
    st.caption(
        "방사형 그래프는 각 차원에서 결과 글자와 같은 방향을 고른 문항의 비율입니다. "
        "성향의 강도나 공식 검사 점수를 뜻하지 않습니다."
    )
    components.html(make_radar_svg(results), height=510, scrolling=False)

    metric_cols = st.columns(4)
    for col, item in zip(metric_cols, results):
        col.metric(
            label=f"{item['axis']} ({item['pair'][0]}/{item['pair'][1]})",
            value=item["winner"],
            delta=f"{item['count']}/{item['total']} 문항 일치",
            delta_color="off",
        )

    st.info("이 페이지는 수업·자기 탐색을 위한 간이 활동이며, 공식 MBTI 검사나 심리 진단이 아닙니다.")
    if st.button("🔄 다시 하기", use_container_width=True, key="restart_result"):
        restart_test()
        st.rerun()


initialize_state()

st.title("🧭 MBTI 성향 탐색기")
st.write("상황을 읽고, 나에게 조금 더 가까운 선택지를 골라보세요.")
st.caption("총 12문항 · 네 차원별 3문항 · 정답은 없어요")

if st.session_state.completed:
    show_result()
else:
    current_index = st.session_state.current_index
    question = QUESTIONS[current_index]
    widget_key = f"choice_{question['id']}"

    selected_code = st.session_state.answers.get(question["id"])
    answered_count = len(st.session_state.answers)
    st.progress(answered_count / len(QUESTIONS), text=f"응답 진행률 · {answered_count}/{len(QUESTIONS)}")
    st.caption(f"문항 {current_index + 1} / {len(QUESTIONS)} · {question['axis']} ({question['pair'][0]} / {question['pair'][1]})")
    st.subheader(question["prompt"])

    st.caption("두 선택지 중 나에게 조금 더 가까운 카드를 눌러주세요.")
    card_cols = st.columns(2, gap="medium")
    for option_index, (letter, option_text) in enumerate(question["options"]):
        is_selected = selected_code == letter
        with card_cols[option_index]:
            st.markdown(f"**선택지 {chr(65 + option_index)}**")
            if st.button(
                f"{'✓  선택됨  ·  ' if is_selected else '＋  '}{option_text}",
                key=f"card_option_{option_index}",
                type="primary" if is_selected else "secondary",
                use_container_width=True,
            ):
                st.session_state.answers[question["id"]] = letter
                st.rerun()

    st.divider()
    previous_col, next_col = st.columns(2)
    with previous_col:
        previous_clicked = st.button(
            "← 이전",
            disabled=current_index == 0,
            use_container_width=True,
            key="previous_question",
        )
    with next_col:
        is_last = current_index == len(QUESTIONS) - 1
        next_clicked = st.button(
            "결과 보기 ✨" if is_last else "다음 →",
            disabled=selected_code is None,
            use_container_width=True,
            type="primary",
            key="next_question",
        )

    if previous_clicked:
        st.session_state.current_index -= 1
        st.rerun()
    if next_clicked:
        if is_last:
            st.session_state.completed = True
        else:
            st.session_state.current_index += 1
        st.rerun()

    if selected_code is None:
        st.caption("다음 문항으로 가려면 선택지를 먼저 골라주세요.")

    st.markdown(" ")
    if st.button("처음부터 다시 하기", key="restart_quiz", use_container_width=True):
        restart_test()
        st.rerun()
