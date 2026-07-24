import html
import random
import re
import time
from collections import Counter

import streamlit as st
from streamlit_autorefresh import st_autorefresh


# ============================================================
# CONFIGURATION
# ============================================================

WORD_DISPLAY_SECONDS = 30
DISTRACTION_SECONDS = 30

WORD_BANKS = [
    [
        "apple",
        "river",
        "chair",
        "candle",
        "garden",
        "button",
        "horse",
        "window",
        "pencil",
        "letter",
    ],
    [
        "orange",
        "bridge",
        "table",
        "lantern",
        "forest",
        "pocket",
        "rabbit",
        "mirror",
        "crayon",
        "basket",
    ],
    [
        "banana",
        "ocean",
        "couch",
        "torch",
        "meadow",
        "jacket",
        "turtle",
        "curtain",
        "marker",
        "bottle",
    ],
    [
        "peach",
        "stream",
        "bench",
        "lamp",
        "valley",
        "wallet",
        "donkey",
        "picture",
        "notebook",
        "bucket",
    ],
]

# Safe positions that remain scattered while preventing overlap.
SCATTER_POSITIONS = [
    (6, 8),
    (39, 5),
    (70, 10),
    (20, 28),
    (55, 26),
    (80, 39),
    (5, 51),
    (38, 55),
    (67, 64),
    (23, 75),
    (51, 79),
    (78, 78),
]

SHAPES = [
    "●",
    "■",
    "▲",
    "◆",
    "★",
    "⬟",
]

SHAPE_NAMES = {
    "●": "circle",
    "■": "square",
    "▲": "triangle",
    "◆": "diamond",
    "★": "star",
    "⬟": "hexagon",
}


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_STATE = {
    "memory_stage": "choice",
    "memory_words": [],
    "memory_positions": [],
    "memory_study_started_at": None,
    "memory_distraction_started_at": None,
    "memory_recall_started_at": None,
    "memory_shape_left": None,
    "memory_shape_right": None,
    "memory_shape_answer": None,
    "memory_distraction_attempts": 0,
    "memory_distraction_correct": 0,
    "memory_result": None,
    "memory_choice_complete": False,
    "memory_task_completed": False,
}

for key, default_value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = default_value


# ============================================================
# PAGE STYLING
# ============================================================

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1050px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .nv-memory-hero {
        padding: 2rem;
        border: 1px solid rgba(110, 231, 217, 0.24);
        border-radius: 24px;
        background:
            radial-gradient(
                circle at top right,
                rgba(73, 214, 204, 0.13),
                transparent 38%
            ),
            linear-gradient(
                145deg,
                rgba(37, 63, 89, 0.18),
                rgba(21, 33, 48, 0.08)
            );
        margin-bottom: 1.35rem;
    }

    .nv-memory-kicker {
        color: #55d9cc;
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.55rem;
    }

    .nv-memory-title {
        font-size: clamp(2rem, 5vw, 3.25rem);
        font-weight: 800;
        letter-spacing: -0.04em;
        line-height: 1.05;
        margin: 0;
    }

    .nv-memory-subtitle {
        margin-top: 0.8rem;
        max-width: 760px;
        font-size: 1.05rem;
        line-height: 1.65;
        opacity: 0.82;
    }

    .nv-step-row {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.8rem;
        margin: 1.25rem 0;
    }

    .nv-step-card {
        padding: 1rem;
        border-radius: 16px;
        border: 1px solid rgba(125, 160, 190, 0.19);
        background: rgba(80, 115, 145, 0.07);
    }

    .nv-step-number {
        width: 30px;
        height: 30px;
        border-radius: 999px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: rgba(76, 220, 207, 0.16);
        color: #55d9cc;
        font-weight: 800;
        margin-bottom: 0.55rem;
    }

    .nv-step-title {
        font-weight: 750;
        margin-bottom: 0.25rem;
    }

    .nv-step-description {
        font-size: 0.9rem;
        opacity: 0.72;
        line-height: 1.45;
    }

    .nv-timer-panel {
        padding: 1.1rem 1.25rem;
        border-radius: 18px;
        border: 1px solid rgba(76, 220, 207, 0.25);
        background: rgba(76, 220, 207, 0.075);
        margin-bottom: 1rem;
    }

    .nv-timer-row {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        align-items: center;
    }

    .nv-timer-label {
        font-weight: 700;
    }

    .nv-timer-value {
        color: #55d9cc;
        font-size: 1.5rem;
        font-weight: 850;
        font-variant-numeric: tabular-nums;
    }

    .nv-word-board {
        position: relative;
        width: 100%;
        height: 570px;
        overflow: hidden;
        border-radius: 28px;
        border: 1px solid rgba(110, 231, 217, 0.25);
        background:
            radial-gradient(
                circle at 18% 22%,
                rgba(94, 234, 212, 0.12),
                transparent 23%
            ),
            radial-gradient(
                circle at 80% 72%,
                rgba(96, 165, 250, 0.13),
                transparent 27%
            ),
            linear-gradient(
                150deg,
                rgba(15, 35, 49, 0.96),
                rgba(20, 31, 48, 0.93)
            );
        box-shadow:
            inset 0 0 70px rgba(0, 0, 0, 0.13);
    }

    .nv-board-decoration {
        position: absolute;
        border-radius: 999px;
        border: 1px solid rgba(100, 220, 210, 0.11);
    }

    .nv-decoration-one {
        width: 180px;
        height: 180px;
        left: -55px;
        top: -65px;
    }

    .nv-decoration-two {
        width: 250px;
        height: 250px;
        right: -100px;
        bottom: -120px;
    }

    .nv-scattered-word {
        position: absolute;
        display: inline-flex;
        justify-content: center;
        align-items: center;
        min-width: 105px;
        padding: 0.7rem 1rem;
        border-radius: 14px;
        border: 1px solid rgba(168, 245, 237, 0.30);
        background: rgba(19, 43, 59, 0.91);
        color: #ecfffd;
        font-size: clamp(1.02rem, 2.2vw, 1.36rem);
        font-weight: 780;
        letter-spacing: 0.01em;
        box-shadow:
            0 9px 26px rgba(0, 0, 0, 0.19),
            inset 0 1px rgba(255, 255, 255, 0.05);
        transform: translate(-50%, -50%);
        user-select: none;
    }

    .nv-distraction-board {
        min-height: 390px;
        border-radius: 26px;
        border: 1px solid rgba(110, 231, 217, 0.23);
        background:
            radial-gradient(
                circle at 50% 10%,
                rgba(76, 220, 207, 0.12),
                transparent 35%
            ),
            rgba(26, 42, 57, 0.19);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        margin-bottom: 1rem;
    }

    .nv-shape-instruction {
        text-align: center;
        font-size: 1.05rem;
        opacity: 0.8;
        margin-bottom: 1.3rem;
    }

    .nv-shape-row {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: clamp(2.2rem, 10vw, 7rem);
        width: 100%;
    }

    .nv-shape {
        width: clamp(120px, 22vw, 190px);
        height: clamp(120px, 22vw, 190px);
        border-radius: 28px;
        border: 1px solid rgba(137, 242, 231, 0.26);
        background: rgba(73, 126, 153, 0.10);
        color: #65dfd2;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: clamp(4.5rem, 12vw, 8rem);
        line-height: 1;
        text-shadow: 0 0 24px rgba(88, 228, 214, 0.22);
    }

    .nv-versus {
        font-weight: 850;
        opacity: 0.4;
        letter-spacing: 0.12em;
    }

    .nv-result-panel {
        padding: 1.5rem;
        border-radius: 22px;
        border: 1px solid rgba(110, 231, 217, 0.22);
        background: rgba(45, 78, 99, 0.10);
        margin: 1rem 0;
    }

    .nv-result-number {
        color: #59ddd0;
        font-size: clamp(2.5rem, 8vw, 4.4rem);
        font-weight: 850;
        line-height: 1;
    }

    .nv-word-chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin-top: 0.75rem;
    }

    .nv-word-chip {
        padding: 0.45rem 0.75rem;
        border-radius: 999px;
        border: 1px solid rgba(109, 230, 218, 0.22);
        background: rgba(77, 211, 199, 0.08);
        font-weight: 650;
    }

    div[data-testid="stButton"] > button {
        min-height: 3rem;
        border-radius: 13px;
        font-weight: 700;
    }

    div[data-testid="stTextArea"] textarea {
        min-height: 155px;
        border-radius: 16px;
        font-size: 1.05rem;
        line-height: 1.6;
    }

    @media (max-width: 700px) {
        .nv-step-row {
            grid-template-columns: 1fr;
        }

        .nv-word-board {
            height: 620px;
        }

        .nv-scattered-word {
            min-width: 84px;
            padding: 0.55rem 0.7rem;
            font-size: 0.95rem;
        }

        .nv-shape-row {
            gap: 1rem;
        }

        .nv-versus {
            font-size: 0.8rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def reset_memory_game(go_to_choice: bool = True) -> None:
    next_stage = "choice" if go_to_choice else "instructions"

    st.session_state.memory_stage = next_stage
    st.session_state.memory_words = []
    st.session_state.memory_positions = []
    st.session_state.memory_study_started_at = None
    st.session_state.memory_distraction_started_at = None
    st.session_state.memory_recall_started_at = None
    st.session_state.memory_shape_left = None
    st.session_state.memory_shape_right = None
    st.session_state.memory_shape_answer = None
    st.session_state.memory_distraction_attempts = 0
    st.session_state.memory_distraction_correct = 0
    st.session_state.memory_result = None
    st.session_state.memory_task_completed = False


def start_memory_game() -> None:
    chosen_words = random.choice(WORD_BANKS).copy()
    random.shuffle(chosen_words)

    positions = random.sample(
        SCATTER_POSITIONS,
        len(chosen_words),
    )

    st.session_state.memory_words = chosen_words
    st.session_state.memory_positions = positions
    st.session_state.memory_stage = "instructions"
    st.session_state.memory_result = None
    st.session_state.memory_task_completed = False


def begin_study() -> None:
    st.session_state.memory_study_started_at = time.time()
    st.session_state.memory_stage = "study"


def create_shape_question() -> None:
    left_shape = random.choice(SHAPES)

    should_match = random.random() < 0.5

    if should_match:
        right_shape = left_shape
    else:
        right_shape = random.choice(
            [
                shape
                for shape in SHAPES
                if shape != left_shape
            ]
        )

    st.session_state.memory_shape_left = left_shape
    st.session_state.memory_shape_right = right_shape
    st.session_state.memory_shape_answer = should_match


def begin_distraction() -> None:
    st.session_state.memory_distraction_started_at = time.time()
    st.session_state.memory_stage = "distraction"
    create_shape_question()


def answer_shape(user_says_same: bool) -> None:
    correct_answer = bool(
        st.session_state.memory_shape_answer
    )

    st.session_state.memory_distraction_attempts += 1

    if user_says_same == correct_answer:
        st.session_state.memory_distraction_correct += 1

    create_shape_question()


def begin_recall() -> None:
    st.session_state.memory_recall_started_at = time.time()
    st.session_state.memory_stage = "recall"


def normalize_token(token: str) -> str:
    cleaned = re.sub(
        r"[^a-z']",
        "",
        str(token).lower(),
    )

    singular_map = {
        "apples": "apple",
        "rivers": "river",
        "chairs": "chair",
        "candles": "candle",
        "gardens": "garden",
        "buttons": "button",
        "horses": "horse",
        "windows": "window",
        "pencils": "pencil",
        "letters": "letter",
        "oranges": "orange",
        "bridges": "bridge",
        "tables": "table",
        "lanterns": "lantern",
        "forests": "forest",
        "pockets": "pocket",
        "rabbits": "rabbit",
        "mirrors": "mirror",
        "crayons": "crayon",
        "baskets": "basket",
        "bananas": "banana",
        "oceans": "ocean",
        "couches": "couch",
        "torches": "torch",
        "meadows": "meadow",
        "jackets": "jacket",
        "turtles": "turtle",
        "curtains": "curtain",
        "markers": "marker",
        "bottles": "bottle",
        "peaches": "peach",
        "streams": "stream",
        "benches": "bench",
        "lamps": "lamp",
        "valleys": "valley",
        "wallets": "wallet",
        "donkeys": "donkey",
        "pictures": "picture",
        "notebooks": "notebook",
        "buckets": "bucket",
    }

    return singular_map.get(cleaned, cleaned)


def score_recall(response_text: str) -> dict:
    tokens = [
        normalize_token(token)
        for token in re.findall(
            r"[A-Za-z']+",
            response_text,
        )
    ]

    tokens = [
        token
        for token in tokens
        if token
    ]

    token_counts = Counter(tokens)

    targets = list(
        st.session_state.memory_words
    )

    target_set = set(targets)

    correct_words = [
        word
        for word in targets
        if token_counts[word] > 0
    ]

    missed_words = [
        word
        for word in targets
        if token_counts[word] == 0
    ]

    repeated_words = {
        word: count - 1
        for word, count in token_counts.items()
        if word in target_set and count > 1
    }

    intrusion_words = [
        token
        for token in tokens
        if token not in target_set
    ]

    unique_intrusions = list(
        dict.fromkeys(intrusion_words)
    )

    recall_seconds = 0.0

    if st.session_state.memory_recall_started_at:
        recall_seconds = max(
            0.0,
            time.time()
            - st.session_state.memory_recall_started_at,
        )

    result = {
        "correct_count": len(correct_words),
        "total_words": len(targets),
        "correct_words": correct_words,
        "missed_words": missed_words,
        "repeated_words": repeated_words,
        "repetition_count": sum(
            repeated_words.values()
        ),
        "intrusion_words": intrusion_words,
        "unique_intrusions": unique_intrusions,
        "intrusion_count": len(intrusion_words),
        "response_text": response_text,
        "response_tokens": tokens,
        "recall_seconds": recall_seconds,
        "distraction_attempts": int(
            st.session_state.memory_distraction_attempts
        ),
        "distraction_correct": int(
            st.session_state.memory_distraction_correct
        ),
    }

    st.session_state.memory_result = result
    st.session_state.memory_task_completed = True
    st.session_state.memory_choice_complete = True
    st.session_state.memory_stage = "complete"


def render_word_board() -> None:
    word_elements = []

    for word, position in zip(
        st.session_state.memory_words,
        st.session_state.memory_positions,
    ):
        x_position, y_position = position

        safe_word = html.escape(
            word.title()
        )

        word_elements.append(
            f"""
            <div
                class="nv-scattered-word"
                style="
                    left: {x_position}%;
                    top: {y_position}%;
                "
            >
                {safe_word}
            </div>
            """
        )

    board_html = f"""
    <div class="nv-word-board">
        <div
            class="
                nv-board-decoration
                nv-decoration-one
            "
        ></div>

        <div
            class="
                nv-board-decoration
                nv-decoration-two
            "
        ></div>

        {''.join(word_elements)}
    </div>
    """

    st.markdown(
        board_html,
        unsafe_allow_html=True,
    )


def render_chips(words: list[str]) -> str:
    if not words:
        return (
            '<span style="opacity:0.7;">None</span>'
        )

    chips = "".join(
        (
            '<span class="nv-word-chip">'
            + html.escape(word.title())
            + "</span>"
        )
        for word in words
    )

    return (
        '<div class="nv-word-chip-row">'
        + chips
        + "</div>"
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <section class="nv-memory-hero">
        <div class="nv-memory-kicker">
            Optional cognitive activity
        </div>

        <h1 class="nv-memory-title">
            Memory Challenge
        </h1>

        <div class="nv-memory-subtitle">
            Study ten scattered words, complete a quick visual
            attention game, and then recall as many words as you can.
            The activity takes about two minutes.
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CHOICE SCREEN
# ============================================================

if st.session_state.memory_stage == "choice":
    st.success(
        "Your two main speech activities are complete."
    )

    st.markdown(
        """
        <div class="nv-step-row">
            <div class="nv-step-card">
                <div class="nv-step-number">1</div>
                <div class="nv-step-title">
                    Study
                </div>
                <div class="nv-step-description">
                    Ten words appear in different locations for
                    30 seconds.
                </div>
            </div>

            <div class="nv-step-card">
                <div class="nv-step-number">2</div>
                <div class="nv-step-title">
                    Focus
                </div>
                <div class="nv-step-description">
                    Complete a fast 30-second visual matching game.
                </div>
            </div>

            <div class="nv-step-card">
                <div class="nv-step-number">3</div>
                <div class="nv-step-title">
                    Recall
                </div>
                <div class="nv-step-description">
                    Enter every word that you remember in any order.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "You can complete the optional memory activity or continue "
        "directly to your existing speech-model results."
    )

    memory_column, results_column = st.columns(2)

    with memory_column:
        if st.button(
            "Start Optional Memory Challenge",
            type="primary",
            use_container_width=True,
        ):
            start_memory_game()
            st.rerun()

    with results_column:
        if st.button(
            "View Results Now",
            use_container_width=True,
        ):
            st.session_state.memory_choice_complete = True
            st.session_state.memory_task_completed = False

            try:
                st.switch_page("views/test.py")
            except Exception:
                st.query_params["show_results"] = "1"
                st.rerun()


# ============================================================
# INSTRUCTION SCREEN
# ============================================================

elif st.session_state.memory_stage == "instructions":
    st.subheader("Before you begin")

    st.markdown(
        """
        Ten everyday words will be scattered across the next screen.

        - You will have **30 seconds** to study them.
        - The words will remain in fixed positions.
        - Do not write them down or take a screenshot.
        - The words disappear automatically.
        - You will then complete a **30-second visual game**.
        - After the visual game, enter every word you remember.
        - Word order and screen location do not matter.
        """
    )

    st.warning(
        "The study screen cannot be reopened after the words disappear."
    )

    first_column, second_column = st.columns([2, 1])

    with first_column:
        if st.button(
            "I Am Ready — Show the Words",
            type="primary",
            use_container_width=True,
        ):
            begin_study()
            st.rerun()

    with second_column:
        if st.button(
            "Cancel",
            use_container_width=True,
        ):
            reset_memory_game(go_to_choice=True)
            st.rerun()


# ============================================================
# STUDY SCREEN
# ============================================================

elif st.session_state.memory_stage == "study":
    if not st.session_state.memory_study_started_at:
        begin_study()
        st.rerun()

    elapsed_seconds = (
        time.time()
        - st.session_state.memory_study_started_at
    )

    remaining_seconds = max(
        0,
        WORD_DISPLAY_SECONDS - int(elapsed_seconds),
    )

    if remaining_seconds <= 0:
        begin_distraction()
        st.rerun()

    st_autorefresh(
        interval=500,
        limit=None,
        key="memory_study_refresh",
    )

    progress_value = min(
        1.0,
        elapsed_seconds / WORD_DISPLAY_SECONDS,
    )

    st.markdown(
        f"""
        <div class="nv-timer-panel">
            <div class="nv-timer-row">
                <div>
                    <div class="nv-timer-label">
                        Study every word
                    </div>
                    <div style="opacity:0.7;">
                        Their locations do not matter.
                    </div>
                </div>

                <div class="nv-timer-value">
                    {remaining_seconds}s
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.progress(progress_value)

    render_word_board()

    st.caption(
        "The words will disappear automatically when the timer reaches zero."
    )


# ============================================================
# DISTRACTION SCREEN
# ============================================================

elif st.session_state.memory_stage == "distraction":
    if not st.session_state.memory_distraction_started_at:
        begin_distraction()
        st.rerun()

    elapsed_seconds = (
        time.time()
        - st.session_state.memory_distraction_started_at
    )

    remaining_seconds = max(
        0,
        DISTRACTION_SECONDS - int(elapsed_seconds),
    )

    if remaining_seconds <= 0:
        begin_recall()
        st.rerun()

    if (
        st.session_state.memory_shape_left is None
        or st.session_state.memory_shape_right is None
    ):
        create_shape_question()
        st.rerun()

    st_autorefresh(
        interval=500,
        limit=None,
        key="memory_distraction_refresh",
    )

    attempts = int(
        st.session_state.memory_distraction_attempts
    )

    st.markdown(
        f"""
        <div class="nv-timer-panel">
            <div class="nv-timer-row">
                <div>
                    <div class="nv-timer-label">
                        Visual Focus Challenge
                    </div>
                    <div style="opacity:0.7;">
                        Decide whether the two shapes match.
                    </div>
                </div>

                <div class="nv-timer-value">
                    {remaining_seconds}s
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.progress(
        min(
            1.0,
            elapsed_seconds / DISTRACTION_SECONDS,
        )
    )

    left_shape = html.escape(
        st.session_state.memory_shape_left
    )

    right_shape = html.escape(
        st.session_state.memory_shape_right
    )

    st.markdown(
        f"""
        <div class="nv-distraction-board">
            <div class="nv-shape-instruction">
                Are these shapes the same or different?
            </div>

            <div class="nv-shape-row">
                <div
                    class="nv-shape"
                    aria-label="{html.escape(
                        SHAPE_NAMES[
                            st.session_state.memory_shape_left
                        ]
                    )}"
                >
                    {left_shape}
                </div>

                <div class="nv-versus">
                    VS
                </div>

                <div
                    class="nv-shape"
                    aria-label="{html.escape(
                        SHAPE_NAMES[
                            st.session_state.memory_shape_right
                        ]
                    )}"
                >
                    {right_shape}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    same_column, different_column = st.columns(2)

    with same_column:
        if st.button(
            "Same Shape",
            type="primary",
            use_container_width=True,
        ):
            answer_shape(True)
            st.rerun()

    with different_column:
        if st.button(
            "Different Shapes",
            use_container_width=True,
        ):
            answer_shape(False)
            st.rerun()

    st.caption(
        f"Questions answered: {attempts} · Keep going until time expires."
    )


# ============================================================
# RECALL SCREEN
# ============================================================

elif st.session_state.memory_stage == "recall":
    st.success(
        "The attention activity is complete."
    )

    st.subheader("Which words do you remember?")

    st.write(
        "Enter every word you remember from the scattered-word screen. "
        "Use spaces, commas, or separate lines. Order does not matter."
    )

    recall_response = st.text_area(
        "Remembered words",
        key="memory_recall_response",
        placeholder=(
            "Type the remembered words here..."
        ),
        height=180,
    )

    st.caption(
        "Do not guess based on the distraction-game shapes. "
        "Only enter words from the original study screen."
    )

    submit_column, restart_column = st.columns([2, 1])

    with submit_column:
        if st.button(
            "Submit Memory Response",
            type="primary",
            use_container_width=True,
        ):
            if not recall_response.strip():
                st.error(
                    "Enter at least one remembered word before submitting."
                )
            else:
                score_recall(recall_response)
                st.rerun()

    with restart_column:
        if st.button(
            "Restart Memory Game",
            use_container_width=True,
        ):
            reset_memory_game(go_to_choice=False)

            if "memory_recall_response" in st.session_state:
                del st.session_state[
                    "memory_recall_response"
                ]

            start_memory_game()
            st.rerun()


# ============================================================
# COMPLETION SCREEN
# ============================================================

elif st.session_state.memory_stage == "complete":
    result = st.session_state.memory_result

    if not result:
        reset_memory_game(go_to_choice=True)
        st.rerun()

    st.success(
        "Memory challenge complete."
    )

    correct_count = int(
        result["correct_count"]
    )

    total_words = int(
        result["total_words"]
    )

    st.markdown(
        f"""
        <div class="nv-result-panel">
            <div style="opacity:0.72; font-weight:700;">
                Words correctly recalled
            </div>

            <div class="nv-result-number">
                {correct_count} of {total_words}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    first_metric, second_metric, third_metric = st.columns(3)

    with first_metric:
        st.metric(
            "Correct words",
            correct_count,
        )

    with second_metric:
        st.metric(
            "Repeated entries",
            int(result["repetition_count"]),
        )

    with third_metric:
        st.metric(
            "Non-list entries",
            int(result["intrusion_count"]),
        )

    with st.expander(
        "Review memory activity details",
        expanded=False,
    ):
        st.markdown("**Correctly recalled**")

        st.markdown(
            render_chips(
                result["correct_words"]
            ),
            unsafe_allow_html=True,
        )

        st.markdown("**Words not recalled**")

        st.markdown(
            render_chips(
                result["missed_words"]
            ),
            unsafe_allow_html=True,
        )

        if result["unique_intrusions"]:
            st.markdown("**Non-list words entered**")

            st.markdown(
                render_chips(
                    result["unique_intrusions"]
                ),
                unsafe_allow_html=True,
            )

        st.write(
            "**Visual-game questions answered:** "
            f"{result['distraction_attempts']}"
        )

        st.write(
            "**Visual-game correct answers:** "
            f"{result['distraction_correct']}"
        )

    st.info(
        "This memory activity is stored as an optional supporting "
        "measurement. It does not alter the two trained speech-model "
        "scores."
    )

    results_column, replay_column = st.columns([2, 1])

    with results_column:
        if st.button(
            "Continue to Full Results",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.memory_choice_complete = True
            st.session_state.memory_task_completed = True

            try:
                st.switch_page("views/test.py")
            except Exception:
                st.query_params["show_results"] = "1"
                st.rerun()

    with replay_column:
        if st.button(
            "Play Again",
            use_container_width=True,
        ):
            if "memory_recall_response" in st.session_state:
                del st.session_state[
                    "memory_recall_response"
                ]

            reset_memory_game(go_to_choice=False)
            start_memory_game()
            st.rerun()
