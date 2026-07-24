import html
import random
import re
import time
from typing import Dict, List, Set

import streamlit as st

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Memory Challenge | NeuroVoice",
    page_icon="🧠",
    layout="wide",
)

# NEUROVOICE_DARK_MEMORY_UI_CSS
DARK_MEMORY_UI_CSS = '\n<style>\n/* ==========================================================\n   NeuroVoice dark memory interface\n   ========================================================== */\n\n:root {\n    color-scheme: dark;\n}\n\nhtml,\nbody,\n[data-testid="stAppViewContainer"],\n[data-testid="stAppViewContainer"] > .main,\n.stApp {\n    background:\n        radial-gradient(\n            circle at 12% 8%,\n            rgba(54, 103, 255, 0.20),\n            transparent 28rem\n        ),\n        radial-gradient(\n            circle at 88% 18%,\n            rgba(120, 76, 255, 0.16),\n            transparent 30rem\n        ),\n        #070b14 !important;\n    color: #f7f9ff !important;\n}\n\n/* Hide Streamlit chrome that flashes during timed reruns. */\nheader[data-testid="stHeader"],\n[data-testid="stToolbar"],\n[data-testid="stDecoration"],\n[data-testid="stStatusWidget"],\n[data-testid="stMainMenu"],\n[data-testid="stAppDeployButton"],\n[data-testid="manage-app-button"],\n.stDeployButton,\n#MainMenu,\nfooter {\n    display: none !important;\n    visibility: hidden !important;\n    height: 0 !important;\n    min-height: 0 !important;\n    opacity: 0 !important;\n    pointer-events: none !important;\n}\n\n/* Remove the blank strip normally reserved for the header. */\n[data-testid="stAppViewBlockContainer"],\n.block-container {\n    padding-top: 1.5rem !important;\n}\n\n/* Standard Streamlit text. */\nh1,\nh2,\nh3,\nh4,\nh5,\nh6,\np,\nli,\nlabel,\nspan,\n[data-testid="stMarkdownContainer"] {\n    color: #f7f9ff;\n}\n\n[data-testid="stCaptionContainer"],\n.stCaption,\nsmall {\n    color: #aebbd2 !important;\n}\n\n/* Dark cards and containers. */\ndiv[data-testid="stVerticalBlockBorderWrapper"],\n[data-testid="stForm"],\n.nv-card {\n    background: rgba(14, 21, 36, 0.96) !important;\n    border: 1px solid #2b3852 !important;\n    box-shadow: 0 18px 55px rgba(0, 0, 0, 0.40) !important;\n}\n\n/* Existing memory-page typography. */\n.nv-kicker {\n    color: #79a8ff !important;\n}\n\n.nv-title,\n.nv-memory-title,\n.nv-section-title {\n    color: #ffffff !important;\n    text-shadow: 0 2px 20px rgba(76, 130, 255, 0.18);\n}\n\n.nv-subtitle,\n.nv-memory-subtitle,\n.nv-section-copy {\n    color: #c4cee0 !important;\n}\n\n/* Study board. */\n.nv-word-board {\n    background:\n        radial-gradient(\n            circle at 18% 18%,\n            rgba(65, 105, 225, 0.14),\n            transparent 34%\n        ),\n        linear-gradient(\n            145deg,\n            #0d1423,\n            #111b2d\n        ) !important;\n    border: 1px solid #34445f !important;\n    box-shadow:\n        inset 0 0 0 1px rgba(255, 255, 255, 0.025),\n        0 20px 55px rgba(0, 0, 0, 0.34) !important;\n}\n\n/* Words shown during memorization. */\n.nv-word,\n.nv-scattered-word {\n    background: #17233a !important;\n    border: 1px solid #47618b !important;\n    box-shadow:\n        0 10px 28px rgba(0, 0, 0, 0.36),\n        inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;\n    color: #ffffff !important;\n    opacity: 1 !important;\n    visibility: visible !important;\n    text-shadow: none !important;\n}\n\n/* Timer. */\n.nv-timer,\n.nv-timer-value {\n    background: #152746 !important;\n    border: 1px solid #4169a8 !important;\n    color: #a9c9ff !important;\n}\n\n/* Visual distraction task. */\n.nv-shape-area {\n    background: #0d1525 !important;\n    border: 1px solid #30405d !important;\n}\n\n.nv-shape {\n    background: #17233a !important;\n    border: 1px solid #45608b !important;\n    color: #8fb5ff !important;\n    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.38) !important;\n}\n\n/* Results. */\n.nv-stat {\n    background: #121d31 !important;\n    border: 1px solid #30415f !important;\n}\n\n.nv-stat-label {\n    color: #aebbd2 !important;\n}\n\n.nv-stat-value {\n    color: #ffffff !important;\n}\n\n.nv-note {\n    background: #111f38 !important;\n    border-left-color: #6d9fff !important;\n    color: #cbd7ea !important;\n}\n\n/* Inputs. */\n[data-testid="stTextArea"] textarea,\n[data-testid="stTextInput"] input,\ntextarea,\ninput {\n    background: #101a2b !important;\n    border: 1px solid #3c4f70 !important;\n    color: #ffffff !important;\n    caret-color: #ffffff !important;\n}\n\ntextarea::placeholder,\ninput::placeholder {\n    color: #8493aa !important;\n    opacity: 1 !important;\n}\n\n[data-testid="stTextArea"] textarea:focus,\n[data-testid="stTextInput"] input:focus {\n    border-color: #79a8ff !important;\n    box-shadow: 0 0 0 1px #79a8ff !important;\n}\n\n/* Buttons, including the memory yes/no choice. */\ndiv.stButton > button,\ndiv[data-testid="stButton"] > button,\nbutton[kind="primary"],\nbutton[kind="secondary"] {\n    min-height: 3.15rem !important;\n    border-radius: 13px !important;\n    border: 1px solid #49658f !important;\n    background: #17243a !important;\n    color: #ffffff !important;\n    font-weight: 760 !important;\n    box-shadow: 0 9px 24px rgba(0, 0, 0, 0.26) !important;\n}\n\ndiv.stButton > button:hover,\ndiv[data-testid="stButton"] > button:hover {\n    background: #223653 !important;\n    border-color: #7daaff !important;\n    color: #ffffff !important;\n}\n\ndiv.stButton > button[kind="primary"],\ndiv[data-testid="stButton"] > button[kind="primary"],\nbutton[kind="primary"] {\n    background: linear-gradient(\n        135deg,\n        #356ff0,\n        #694de5\n    ) !important;\n    border-color: #82a9ff !important;\n    color: #ffffff !important;\n}\n\ndiv.stButton > button[kind="primary"]:hover,\nbutton[kind="primary"]:hover {\n    background: linear-gradient(\n        135deg,\n        #477ff7,\n        #795cf0\n    ) !important;\n}\n\n/* Alerts. */\n[data-testid="stAlert"] {\n    background: #121e32 !important;\n    border: 1px solid #344866 !important;\n    color: #eef3ff !important;\n}\n\n/* Progress bars. */\n[data-testid="stProgress"] > div {\n    background: #1a2941 !important;\n}\n\n/* Sidebar remains readable. */\n[data-testid="stSidebar"] {\n    background: #0b111d !important;\n    border-right: 1px solid #27344b !important;\n}\n\n[data-testid="stSidebar"] * {\n    color: #edf3ff !important;\n}\n\n/* Prevent rerun animations from looking like text flashes. */\n.nv-word,\n.nv-scattered-word,\n.nv-word-board,\n.nv-card,\n.nv-timer,\n.nv-timer-value {\n    animation: none !important;\n    transition: none !important;\n}\n\n/* Remove iframe/component outlines occasionally visible during refresh. */\niframe {\n    border: 0 !important;\n}\n\n@media (max-width: 760px) {\n    [data-testid="stAppViewBlockContainer"],\n    .block-container {\n        padding-left: 1rem !important;\n        padding-right: 1rem !important;\n    }\n}\n</style>\n'

# NEUROVOICE_DARK_MEMORY_UI
st.markdown(
    DARK_MEMORY_UI_CSS,
    unsafe_allow_html=True,
)



# ============================================================
# CONSTANTS
# ============================================================

STUDY_SECONDS = 30
DISTRACTION_SECONDS = 30

WORD_BANKS: List[List[str]] = [
    [
        "Notebook",
        "Donkey",
        "Peach",
        "Wallet",
        "Picture",
        "Stream",
        "Bench",
        "Lamp",
        "Valley",
        "Bucket",
    ],
    [
        "Garden",
        "Pencil",
        "Window",
        "Rabbit",
        "Orange",
        "Bridge",
        "Jacket",
        "Candle",
        "Forest",
        "Bottle",
    ],
    [
        "Blanket",
        "Horse",
        "Cherry",
        "Camera",
        "River",
        "Chair",
        "Mirror",
        "Mountain",
        "Basket",
        "Clock",
    ],
]

WORD_POSITIONS = [
    (8, 12),
    (38, 8),
    (70, 13),
    (20, 34),
    (53, 31),
    (80, 42),
    (7, 60),
    (36, 64),
    (66, 70),
    (22, 82),
]

SHAPES = ["●", "■", "▲", "◆", "★", "⬟"]


# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(38, 114, 255, 0.10),
                transparent 30%
            ),
            radial-gradient(
                circle at 90% 20%,
                rgba(117, 78, 255, 0.08),
                transparent 28%
            ),
            #f7f9fc;
    }

    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e8edf5;
    }

    .block-container {
        max-width: 1120px;
        padding-top: 2.2rem;
        padding-bottom: 4rem;
    }

    .nv-kicker {
        color: #3267d6;
        font-size: 0.84rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        margin-bottom: 0.4rem;
        text-transform: uppercase;
    }

    .nv-title {
        color: #15223b;
        font-size: clamp(2.2rem, 5vw, 4rem);
        font-weight: 850;
        letter-spacing: -0.045em;
        line-height: 1.03;
        margin: 0;
    }

    .nv-subtitle {
        color: #5d6a80;
        font-size: 1.08rem;
        line-height: 1.65;
        margin-top: 1rem;
        max-width: 760px;
    }

    .nv-card {
        background: rgba(255, 255, 255, 0.96);
        border: 1px solid #e4eaf3;
        border-radius: 24px;
        box-shadow: 0 16px 45px rgba(28, 48, 84, 0.08);
        margin-top: 1.5rem;
        padding: 1.6rem;
    }

    .nv-section-title {
        color: #17243d;
        font-size: 1.45rem;
        font-weight: 800;
        margin-bottom: 0.35rem;
    }

    .nv-section-copy {
        color: #68758b;
        font-size: 1rem;
        line-height: 1.55;
    }

    .nv-timer {
        align-items: center;
        background: #edf3ff;
        border: 1px solid #d6e3ff;
        border-radius: 999px;
        color: #285fc5;
        display: inline-flex;
        font-size: 1rem;
        font-weight: 800;
        gap: 0.45rem;
        margin-top: 1rem;
        padding: 0.55rem 0.95rem;
    }

    .nv-word-board {
        background:
            linear-gradient(
                145deg,
                rgba(245, 248, 255, 0.98),
                rgba(255, 255, 255, 0.98)
            );
        border: 1px solid #dfe7f3;
        border-radius: 24px;
        box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.7);
        height: 510px;
        margin-top: 1.25rem;
        overflow: hidden;
        position: relative;
        width: 100%;
    }

    .nv-word {
        align-items: center;
        background: #ffffff;
        border: 1px solid #dce5f3;
        border-radius: 14px;
        box-shadow: 0 8px 22px rgba(42, 64, 101, 0.10);
        color: #1c2c48;
        display: inline-flex;
        font-size: clamp(0.92rem, 1.8vw, 1.18rem);
        font-weight: 780;
        justify-content: center;
        min-width: 92px;
        padding: 0.75rem 1rem;
        position: absolute;
        transform: translate(-50%, -50%);
        white-space: nowrap;
    }

    .nv-shape-area {
        align-items: center;
        background: linear-gradient(145deg, #f8faff, #ffffff);
        border: 1px solid #dfe7f3;
        border-radius: 22px;
        display: flex;
        gap: 3rem;
        justify-content: center;
        margin: 1.4rem 0 1rem;
        min-height: 245px;
        padding: 2rem;
    }

    .nv-shape {
        align-items: center;
        background: #ffffff;
        border: 1px solid #dfe7f3;
        border-radius: 22px;
        box-shadow: 0 10px 28px rgba(37, 58, 94, 0.10);
        color: #3767cf;
        display: flex;
        font-size: clamp(4rem, 10vw, 7rem);
        height: 165px;
        justify-content: center;
        width: 165px;
    }

    .nv-stat-grid {
        display: grid;
        gap: 1rem;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        margin-top: 1.4rem;
    }

    .nv-stat {
        background: #f8faff;
        border: 1px solid #e1e8f3;
        border-radius: 18px;
        padding: 1.2rem;
    }

    .nv-stat-label {
        color: #6c788c;
        font-size: 0.83rem;
        font-weight: 750;
        text-transform: uppercase;
    }

    .nv-stat-value {
        color: #182743;
        font-size: 2rem;
        font-weight: 850;
        margin-top: 0.25rem;
    }

    .nv-word-list {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin-top: 0.8rem;
    }

    .nv-chip-good {
        background: #eaf8ef;
        border: 1px solid #c5ebd2;
        border-radius: 999px;
        color: #217642;
        font-weight: 700;
        padding: 0.45rem 0.75rem;
    }

    .nv-chip-missed {
        background: #f3f5f8;
        border: 1px solid #e0e5ec;
        border-radius: 999px;
        color: #6d7786;
        font-weight: 700;
        padding: 0.45rem 0.75rem;
    }

    .nv-note {
        background: #f1f5ff;
        border-left: 4px solid #4774d9;
        border-radius: 10px;
        color: #4e5f7a;
        line-height: 1.55;
        margin-top: 1.2rem;
        padding: 1rem 1.1rem;
    }

    div.stButton > button {
        border-radius: 12px;
        font-weight: 750;
        min-height: 3rem;
    }

    @media (max-width: 760px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .nv-word-board {
            height: 560px;
        }

        .nv-word {
            min-width: 74px;
            padding: 0.55rem 0.7rem;
        }

        .nv-shape-area {
            gap: 1rem;
        }

        .nv-shape {
            font-size: 4rem;
            height: 125px;
            width: 125px;
        }

        .nv-stat-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# STATE HELPERS
# ============================================================

def initialize_state() -> None:
    defaults = {
        "memory_phase": "intro",
        "memory_words": [],
        "memory_positions": [],
        "memory_study_started": None,
        "memory_distraction_started": None,
        "memory_shape_left": "",
        "memory_shape_right": "",
        "memory_shape_same": False,
        "memory_shape_question": 0,
        "memory_shape_correct": 0,
        "memory_shape_total": 0,
        "memory_shape_answered": False,
        "memory_recall_text": "",
        "memory_result": None,
        "memory_choice_complete": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_memory_test() -> None:
    keys = [
        "memory_phase",
        "memory_words",
        "memory_positions",
        "memory_study_started",
        "memory_distraction_started",
        "memory_shape_left",
        "memory_shape_right",
        "memory_shape_same",
        "memory_shape_question",
        "memory_shape_correct",
        "memory_shape_total",
        "memory_shape_answered",
        "memory_recall_text",
        "memory_result",
        "memory_choice_complete",
    ]

    for key in keys:
        st.session_state.pop(key, None)

    initialize_state()


def begin_study() -> None:
    words = random.choice(WORD_BANKS).copy()
    positions = WORD_POSITIONS.copy()

    random.shuffle(words)
    random.shuffle(positions)

    st.session_state.memory_words = words
    st.session_state.memory_positions = positions
    st.session_state.memory_study_started = time.time()
    st.session_state.memory_phase = "study"


def create_shape_question() -> None:
    left_shape = random.choice(SHAPES)
    same = random.choice([True, False])

    if same:
        right_shape = left_shape
    else:
        right_shape = random.choice(
            [shape for shape in SHAPES if shape != left_shape]
        )

    st.session_state.memory_shape_left = left_shape
    st.session_state.memory_shape_right = right_shape
    st.session_state.memory_shape_same = same
    st.session_state.memory_shape_question += 1
    st.session_state.memory_shape_answered = False


def begin_distraction() -> None:
    st.session_state.memory_phase = "distraction"
    st.session_state.memory_distraction_started = time.time()
    st.session_state.memory_shape_correct = 0
    st.session_state.memory_shape_total = 0
    st.session_state.memory_shape_question = 0
    create_shape_question()


def submit_shape_answer(answer_same: bool) -> None:
    if st.session_state.memory_shape_answered:
        return

    st.session_state.memory_shape_answered = True
    st.session_state.memory_shape_total += 1

    if answer_same == st.session_state.memory_shape_same:
        st.session_state.memory_shape_correct += 1

    create_shape_question()


def normalize_word(word: str) -> str:
    return re.sub(r"[^a-z]", "", word.lower())


def parse_recalled_words(text: str) -> List[str]:
    raw_words = re.findall(r"[A-Za-z]+", text)
    return [
        normalize_word(word)
        for word in raw_words
        if normalize_word(word)
    ]


def calculate_results(recall_text: str) -> Dict:
    target_words = st.session_state.memory_words

    target_map = {
        normalize_word(word): word
        for word in target_words
    }

    recalled_sequence = parse_recalled_words(recall_text)
    recalled_unique: Set[str] = set(recalled_sequence)

    correct_normalized = [
        word
        for word in target_map
        if word in recalled_unique
    ]

    correct_words = [
        target_map[word]
        for word in correct_normalized
    ]

    missed_words = [
        target_map[word]
        for word in target_map
        if word not in recalled_unique
    ]

    intrusions = sorted(
        {
            word
            for word in recalled_unique
            if word not in target_map
        }
    )

    repetitions = max(
        0,
        len(recalled_sequence) - len(recalled_unique),
    )

    correct_count = len(correct_words)
    recall_percent = round(
        correct_count / len(target_words) * 100
    )

    if correct_count >= 8:
        descriptive_band = "Strong recall"
    elif correct_count >= 5:
        descriptive_band = "Moderate recall"
    else:
        descriptive_band = "Low recall"

    return {
        "correct_count": correct_count,
        "total_words": len(target_words),
        "recall_percent": recall_percent,
        "correct_words": correct_words,
        "missed_words": missed_words,
        "intrusions": intrusions,
        "repetitions": repetitions,
        "descriptive_band": descriptive_band,
        "distraction_correct": (
            st.session_state.memory_shape_correct
        ),
        "distraction_total": (
            st.session_state.memory_shape_total
        ),
    }


def auto_refresh(key: str) -> None:
    if st_autorefresh is not None:
        st_autorefresh(
            interval=1000,
            limit=None,
            key=key,
        )



# ============================================================
# HEADER
# ============================================================

initialize_state()

# Do not render the large page header during timed phases.
# Streamlit reruns once per second for the timers, so rendering
# this header during those phases makes it visibly flash.
if st.session_state.memory_phase not in {"study", "distraction"}:
    st.markdown(
        """
        <div class="nv-kicker">Optional cognitive activity</div>
        <h1 class="nv-title">Memory Challenge</h1>
        <div class="nv-subtitle">
            Study ten words, complete a brief visual-attention
            activity, and then recall as many of the original words
            as possible. This activity takes about two minutes.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# INTRO PHASE
# ============================================================

if st.session_state.memory_phase == "intro":
    st.markdown(
        """
        <div class="nv-card">
            <div class="nv-section-title">Before you begin</div>
            <div class="nv-section-copy">
                Ten words will appear in different locations for
                30 seconds. Study the words themselves; their
                locations do not matter. Afterward, you will
                complete a short visual task before recalling
                the words.
            </div>
            <div class="nv-note">
                Do not write the words down or take a screenshot.
                The activity is intended to measure unaided recall.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 1])

    with left:
        if st.button(
            "Begin memory challenge",
            type="primary",
            use_container_width=True,
        ):
            begin_study()
            st.rerun()

    with right:
        if st.button(
            "Skip optional activity",
            use_container_width=True,
        ):
            st.session_state.memory_choice_complete = True
            st.session_state.memory_result = None

            try:
                st.switch_page("views/test.py")
            except Exception:
                st.info(
                    "The optional activity was skipped. "
                    "Use the Take Test page to view your results."
                )


# ============================================================
# STUDY PHASE
# ============================================================

elif st.session_state.memory_phase == "study":
    auto_refresh("memory_study_refresh")

    elapsed = time.time() - st.session_state.memory_study_started
    remaining = max(
        0,
        STUDY_SECONDS - int(elapsed),
    )

    if remaining <= 0:
        begin_distraction()
        st.rerun()

    st.markdown(
        f"""
        <div class="nv-card">
            <div class="nv-section-title">Study every word</div>
            <div class="nv-section-copy">
                Focus on remembering the words. Their locations
                do not matter.
            </div>
            <div class="nv-timer">
                Time remaining: {remaining} seconds
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    word_html = []

    for word, position in zip(
        st.session_state.memory_words,
        st.session_state.memory_positions,
    ):
        left, top = position

        word_html.append(
            (
                '<div class="nv-word" '
                f'style="left:{left}%; top:{top}%;">'
                f'{html.escape(word)}'
                "</div>"
            )
        )

    board_html = (
        '<div class="nv-word-board">'
        + "".join(word_html)
        + "</div>"
    )

    st.markdown(
        board_html,
        unsafe_allow_html=True,
    )

    st.caption(
        "The words will disappear automatically when the timer "
        "reaches zero."
    )


# ============================================================
# DISTRACTION PHASE
# ============================================================

elif st.session_state.memory_phase == "distraction":
    auto_refresh("memory_distraction_refresh")

    elapsed = (
        time.time()
        - st.session_state.memory_distraction_started
    )

    remaining = max(
        0,
        DISTRACTION_SECONDS - int(elapsed),
    )

    if remaining <= 0:
        st.session_state.memory_phase = "recall"
        st.rerun()

    st.markdown(
        f"""
        <div class="nv-card">
            <div class="nv-section-title">
                Visual attention activity
            </div>
            <div class="nv-section-copy">
                Decide whether the two shapes are the same or
                different.
            </div>
            <div class="nv-timer">
                Time remaining: {remaining} seconds
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left_shape = html.escape(
        st.session_state.memory_shape_left
    )

    right_shape = html.escape(
        st.session_state.memory_shape_right
    )

    st.markdown(
        f"""
        <div class="nv-shape-area">
            <div class="nv-shape">{left_shape}</div>
            <div class="nv-shape">{right_shape}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    same_column, different_column = st.columns(2)

    with same_column:
        if st.button(
            "Same",
            type="primary",
            use_container_width=True,
        ):
            submit_shape_answer(True)
            st.rerun()

    with different_column:
        if st.button(
            "Different",
            use_container_width=True,
        ):
            submit_shape_answer(False)
            st.rerun()

    st.caption(
        "Responses completed: "
        f"{st.session_state.memory_shape_total}"
    )


# ============================================================
# RECALL PHASE
# ============================================================

elif st.session_state.memory_phase == "recall":
    st.markdown(
        """
        <div class="nv-card">
            <div class="nv-section-title">
                Recall the original words
            </div>
            <div class="nv-section-copy">
                Enter every word you remember from the original
                list. Separate words with spaces, commas, or new
                lines. Do not guess based on the visual shapes.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    recall_text = st.text_area(
        "Words you remember",
        key="memory_recall_text",
        height=180,
        placeholder=(
            "Type all remembered words here..."
        ),
    )

    if st.button(
        "Submit recalled words",
        type="primary",
        use_container_width=True,
    ):
        if not recall_text.strip():
            st.warning(
                "Enter the words you remember before submitting."
            )
        else:
            result = calculate_results(recall_text)

            st.session_state.memory_result = result
            st.session_state.memory_choice_complete = True
            st.session_state.memory_phase = "results"
            st.rerun()


# ============================================================
# RESULTS PHASE
# ============================================================

elif st.session_state.memory_phase == "results":
    result = st.session_state.memory_result

    if not result:
        st.session_state.memory_phase = "intro"
        st.rerun()

    st.markdown(
        """
        <div class="nv-card">
            <div class="nv-section-title">
                Memory activity results
            </div>
            <div class="nv-section-copy">
                These values describe performance on this optional
                activity. They are not a diagnosis.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    stat_html = f"""
    <div class="nv-stat-grid">
        <div class="nv-stat">
            <div class="nv-stat-label">Correct words</div>
            <div class="nv-stat-value">
                {result["correct_count"]}/{result["total_words"]}
            </div>
        </div>
        <div class="nv-stat">
            <div class="nv-stat-label">Recall percentage</div>
            <div class="nv-stat-value">
                {result["recall_percent"]}%
            </div>
        </div>
        <div class="nv-stat">
            <div class="nv-stat-label">Repetitions</div>
            <div class="nv-stat-value">
                {result["repetitions"]}
            </div>
        </div>
        <div class="nv-stat">
            <div class="nv-stat-label">Extra words</div>
            <div class="nv-stat-value">
                {len(result["intrusions"])}
            </div>
        </div>
    </div>
    """

    st.markdown(
        stat_html,
        unsafe_allow_html=True,
    )

    st.subheader(result["descriptive_band"])

    st.markdown("**Correctly recalled**")

    correct_chips = "".join(
        (
            '<span class="nv-chip-good">'
            f'{html.escape(word)}'
            "</span>"
        )
        for word in result["correct_words"]
    )

    if not correct_chips:
        correct_chips = (
            '<span class="nv-chip-missed">None</span>'
        )

    st.markdown(
        f'<div class="nv-word-list">{correct_chips}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("**Missed words**")

    missed_chips = "".join(
        (
            '<span class="nv-chip-missed">'
            f'{html.escape(word)}'
            "</span>"
        )
        for word in result["missed_words"]
    )

    if not missed_chips:
        missed_chips = (
            '<span class="nv-chip-good">None</span>'
        )

    st.markdown(
        f'<div class="nv-word-list">{missed_chips}</div>',
        unsafe_allow_html=True,
    )

    if result["intrusions"]:
        st.markdown("**Words not in the original list**")
        st.write(", ".join(result["intrusions"]))

    if result["distraction_total"] > 0:
        st.caption(
            "Visual-task accuracy: "
            f'{result["distraction_correct"]}/'
            f'{result["distraction_total"]}'
        )

    st.markdown(
        """
        <div class="nv-note">
            This optional task provides a descriptive memory
            measurement. It should not be interpreted as an
            Alzheimer's probability or clinical conclusion.
        </div>
        """,
        unsafe_allow_html=True,
    )

    results_column, restart_column = st.columns(2)

    with results_column:
        if st.button(
            "Continue to full results",
            type="primary",
            use_container_width=True,
        ):
            # NEUROVOICE_RETURN_TO_RESULTS
            st.session_state["return_to_final_results"] = True
            st.session_state["memory_choice_complete"] = True
            try:
                st.switch_page("views/test.py")
            except Exception:
                st.info(
                    "Return to the Take Test page to view the "
                    "completed assessment results."
                )

    with restart_column:
        if st.button(
            "Repeat memory activity",
            use_container_width=True,
        ):
            reset_memory_test()
            st.rerun()