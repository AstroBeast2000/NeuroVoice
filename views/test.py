import __main__
import time
import wave
from io import BytesIO
from pathlib import Path

import streamlit as st


# NEUROVOICE_OPTIONAL_MEMORY_ROUTE
if (
    st.session_state.get("cookie_result") is not None
    and st.session_state.get("fluency_result") is not None
    and not st.session_state.get(
        "memory_choice_complete",
        False,
    )
):
    st.switch_page("views/memory.py")
from src.linguistic_features import LinguisticFeatures
from src.cookie_model import CookieTheftEnsemble
from src.fluency_model_v2 import AnimalFluencyModel
from src.transcription import transcribe_audio_bytes


# NEUROVOICE_OVERALL_WEIGHTING_HELPERS
def _nv_clamp_probability(value):
    """Convert a probability-like value to the range 0.0 to 1.0."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None

    if value != value:
        return None

    # Accept either 0-1 probabilities or 0-100 percentages.
    if 1.0 < value <= 100.0:
        value = value / 100.0

    if not 0.0 <= value <= 1.0:
        return None

    return max(0.0, min(1.0, value))


def _nv_extract_probability_from_value(value):
    """Extract a positive-class probability from common result structures."""
    direct = _nv_clamp_probability(value)
    if direct is not None:
        return direct

    if isinstance(value, dict):
        preferred_keys = (
            "probability",
            "positive_probability",
            "positive_class_probability",
            "ad_probability",
            "risk_probability",
            "model_probability",
            "score",
            "risk_score",
            "confidence",
        )

        normalized = {
            str(key).strip().lower(): item
            for key, item in value.items()
        }

        for key in preferred_keys:
            if key in normalized:
                extracted = _nv_clamp_probability(normalized[key])
                if extracted is not None:
                    return extracted

        for key, item in normalized.items():
            if any(
                token in key
                for token in (
                    "probability",
                    "proba",
                    "risk",
                    "score",
                    "confidence",
                )
            ):
                extracted = _nv_clamp_probability(item)
                if extracted is not None:
                    return extracted

    for attribute in (
        "probability",
        "positive_probability",
        "positive_class_probability",
        "ad_probability",
        "risk_probability",
        "score",
        "risk_score",
        "confidence",
    ):
        if hasattr(value, attribute):
            extracted = _nv_clamp_probability(
                getattr(value, attribute)
            )
            if extracted is not None:
                return extracted

    return None


def _nv_find_task_probability(task_tokens):
    """
    Find a model probability in Streamlit session state.

    A matching session-state path must contain a task token such as
    'cookie' or 'fluency'. Probability-like child values are preferred.
    """
    candidates = []

    def walk(value, path, depth=0):
        if depth > 5:
            return

        path_text = ".".join(path).lower()
        has_task_token = any(
            token in path_text
            for token in task_tokens
        )

        if has_task_token:
            probability = _nv_extract_probability_from_value(value)

            if probability is not None:
                score = 0

                if any(
                    token in path_text
                    for token in (
                        "probability",
                        "proba",
                        "risk",
                        "score",
                        "result",
                        "prediction",
                    )
                ):
                    score += 10

                if "threshold" in path_text:
                    score -= 20

                if "label" in path_text:
                    score -= 10

                candidates.append(
                    (score, len(path), path_text, probability)
                )

        if isinstance(value, dict):
            for key, item in value.items():
                walk(
                    item,
                    path + [str(key)],
                    depth + 1,
                )

        elif isinstance(value, (list, tuple)):
            for index, item in enumerate(value[:20]):
                walk(
                    item,
                    path + [str(index)],
                    depth + 1,
                )

    for key in list(st.session_state.keys()):
        try:
            value = st.session_state[key]
        except Exception:
            continue

        walk(value, [str(key)])

    if not candidates:
        return None, None

    candidates.sort(
        key=lambda item: (
            item[0],
            -item[1],
        ),
        reverse=True,
    )

    _, _, path, probability = candidates[0]
    return probability, path


def _nv_get_memory_result():
    result = st.session_state.get("memory_result")

    if not isinstance(result, dict):
        return None

    recall_percent = result.get("recall_percent")

    try:
        recall_percent = float(recall_percent)
    except (TypeError, ValueError):
        return None

    if not 0.0 <= recall_percent <= 100.0:
        return None

    return result


def _nv_calculate_overall_score():
    """
    Calculate the custom experimental overall screening score.

    Memory completed:
      50% fluency + 30% Cookie Theft + 20% memory-derived score

    Memory skipped:
      60% fluency + 40% Cookie Theft

    Memory-derived score:
      1 - recall percentage
    """
    cookie_probability, cookie_path = _nv_find_task_probability(
        (
            "cookie",
            "picture",
            "description",
        )
    )

    fluency_probability, fluency_path = _nv_find_task_probability(
        (
            "fluency",
            "animal",
            "semantic",
        )
    )

    if cookie_probability is None or fluency_probability is None:
        return {
            "available": False,
            "cookie_probability": cookie_probability,
            "fluency_probability": fluency_probability,
            "cookie_source": cookie_path,
            "fluency_source": fluency_path,
            "memory_result": _nv_get_memory_result(),
            "error": (
                "The Cookie Theft or semantic-fluency probability "
                "could not be found in session state."
            ),
        }

    memory_result = _nv_get_memory_result()

    if memory_result is not None:
        recall_percent = float(
            memory_result["recall_percent"]
        )

        memory_score = max(
            0.0,
            min(
                1.0,
                1.0 - recall_percent / 100.0,
            ),
        )

        overall_score = (
            0.50 * fluency_probability
            + 0.30 * cookie_probability
            + 0.20 * memory_score
        )

        weighting = {
            "fluency": 0.50,
            "cookie": 0.30,
            "memory": 0.20,
        }

        memory_completed = True

    else:
        memory_score = None

        overall_score = (
            0.60 * fluency_probability
            + 0.40 * cookie_probability
        )

        weighting = {
            "fluency": 0.60,
            "cookie": 0.40,
            "memory": 0.00,
        }

        memory_completed = False

    overall_score = max(
        0.0,
        min(1.0, overall_score),
    )

    result = {
        "available": True,
        "overall_score": overall_score,
        "overall_percent": round(
            overall_score * 100.0,
            1,
        ),
        "cookie_probability": cookie_probability,
        "cookie_percent": round(
            cookie_probability * 100.0,
            1,
        ),
        "fluency_probability": fluency_probability,
        "fluency_percent": round(
            fluency_probability * 100.0,
            1,
        ),
        "memory_score": memory_score,
        "memory_percent": (
            round(memory_score * 100.0, 1)
            if memory_score is not None
            else None
        ),
        "memory_completed": memory_completed,
        "memory_result": memory_result,
        "weighting": weighting,
        "cookie_source": cookie_path,
        "fluency_source": fluency_path,
    }

    st.session_state["overall_screening_result"] = result
    st.session_state["overall_screening_score"] = overall_score
    st.session_state["overall_screening_percent"] = result[
        "overall_percent"
    ]

    return result


def _nv_render_overall_results():
    result = _nv_calculate_overall_score()

    if not result["available"]:
        st.warning(
            "The overall screening score could not be calculated "
            "because one or both speech-model probabilities were "
            "not available."
        )
        return

    overall_percent = result["overall_percent"]
    cookie_percent = result["cookie_percent"]
    fluency_percent = result["fluency_percent"]

    if result["memory_completed"]:
        memory_percent = result["memory_percent"]

        weighting_text = (
            "50% semantic fluency + 30% Cookie Theft + "
            "20% memory-derived score"
        )

        memory_text = (
            f"{memory_percent:.1f}% "
            f"(derived from "
            f"{result['memory_result']['recall_percent']}% recall)"
        )
    else:
        weighting_text = (
            "60% semantic fluency + 40% Cookie Theft"
        )
        memory_text = "Not completed"

    st.markdown(
        f"""
        <div style="
            margin-top: 1.2rem;
            margin-bottom: 1.2rem;
            padding: 1.35rem;
            border: 1px solid rgba(148, 163, 184, 0.28);
            border-radius: 18px;
            background:
                linear-gradient(
                    145deg,
                    rgba(15, 23, 42, 0.96),
                    rgba(30, 41, 59, 0.96)
                );
        ">
            <div style="
                color: #94a3b8;
                font-size: 0.82rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            ">
                Experimental combined screening result
            </div>

            <div style="
                margin-top: 0.35rem;
                color: #f8fafc;
                font-size: 2.3rem;
                line-height: 1.05;
                font-weight: 800;
            ">
                {overall_percent:.1f}%
            </div>

            <div style="
                margin-top: 0.45rem;
                color: #cbd5e1;
                font-size: 1rem;
            ">
                Overall model-estimated Alzheimer's screening score
            </div>

            <div style="
                margin-top: 1rem;
                color: #e2e8f0;
                font-size: 0.93rem;
                line-height: 1.65;
            ">
                <strong>Semantic fluency model:</strong>
                {fluency_percent:.1f}%<br>
                <strong>Cookie Theft model:</strong>
                {cookie_percent:.1f}%<br>
                <strong>Memory-derived score:</strong>
                {memory_text}<br>
                <strong>Weighting:</strong>
                {weighting_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "This is a custom experimental screening score. It is not "
        "a diagnosis or a clinically validated probability that a "
        "person has Alzheimer's disease."
    )


def _nv_append_overall_to_pdf(story, styles):
    """Append overall weighting and optional memory results to a PDF story."""
    result = _nv_calculate_overall_score()

    if not result["available"]:
        return

    try:
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
    except Exception:
        return

    heading_style = styles.get(
        "Heading2",
        styles["Normal"],
    )
    normal_style = styles.get(
        "BodyText",
        styles["Normal"],
    )

    story.append(Spacer(1, 0.18 * inch))
    story.append(
        Paragraph(
            "Overall Experimental Screening Score",
            heading_style,
        )
    )
    story.append(Spacer(1, 0.08 * inch))

    story.append(
        Paragraph(
            (
                "<b>Overall model-estimated Alzheimer's screening "
                f"score: {result['overall_percent']:.1f}%</b>"
            ),
            normal_style,
        )
    )

    if result["memory_completed"]:
        weighting_text = (
            "50% semantic fluency, 30% Cookie Theft, "
            "20% memory-derived score"
        )
    else:
        weighting_text = (
            "60% semantic fluency, 40% Cookie Theft"
        )

    table_data = [
        ["Component", "Score", "Weight"],
        [
            "Semantic fluency",
            f"{result['fluency_percent']:.1f}%",
            f"{result['weighting']['fluency'] * 100:.0f}%",
        ],
        [
            "Cookie Theft",
            f"{result['cookie_percent']:.1f}%",
            f"{result['weighting']['cookie'] * 100:.0f}%",
        ],
    ]

    if result["memory_completed"]:
        table_data.append(
            [
                "Memory-derived score",
                f"{result['memory_percent']:.1f}%",
                f"{result['weighting']['memory'] * 100:.0f}%",
            ]
        )
    else:
        table_data.append(
            [
                "Memory challenge",
                "Not completed",
                "Not included",
            ]
        )

    score_table = Table(
        table_data,
        colWidths=[
            2.45 * inch,
            1.35 * inch,
            1.25 * inch,
        ],
    )

    score_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#1E293B"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTNAME",
                    (0, 1),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#CBD5E1"),
                ),
                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, -1),
                    colors.HexColor("#F8FAFC"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(Spacer(1, 0.10 * inch))
    story.append(score_table)
    story.append(Spacer(1, 0.10 * inch))

    story.append(
        Paragraph(
            f"<b>Weighting used:</b> {weighting_text}.",
            normal_style,
        )
    )

    memory_result = result.get("memory_result")

    if result["memory_completed"] and isinstance(
        memory_result,
        dict,
    ):
        story.append(Spacer(1, 0.18 * inch))
        story.append(
            Paragraph(
                "Optional Memory Challenge",
                heading_style,
            )
        )
        story.append(Spacer(1, 0.08 * inch))

        correct_count = memory_result.get(
            "correct_count",
            0,
        )
        total_words = memory_result.get(
            "total_words",
            10,
        )
        recall_percent = memory_result.get(
            "recall_percent",
            0,
        )
        repetitions = memory_result.get(
            "repetitions",
            0,
        )
        intrusions = memory_result.get(
            "intrusions",
            [],
        )

        if not isinstance(intrusions, (list, tuple)):
            intrusions = []

        memory_table_data = [
            ["Memory metric", "Result"],
            [
                "Correct recall",
                f"{correct_count}/{total_words}",
            ],
            [
                "Recall percentage",
                f"{recall_percent}%",
            ],
            [
                "Repetitions",
                str(repetitions),
            ],
            [
                "Intrusions",
                str(len(intrusions)),
            ],
        ]

        memory_table = Table(
            memory_table_data,
            colWidths=[
                2.45 * inch,
                2.60 * inch,
            ],
        )

        memory_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#1E293B"),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "FONTNAME",
                        (0, 1),
                        (0, -1),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor("#CBD5E1"),
                    ),
                    (
                        "BACKGROUND",
                        (0, 1),
                        (-1, -1),
                        colors.HexColor("#F8FAFC"),
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                ]
            )
        )

        story.append(memory_table)

        if intrusions:
            escaped_intrusions = ", ".join(
                str(word)
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                for word in intrusions
            )

            story.append(Spacer(1, 0.08 * inch))
            story.append(
                Paragraph(
                    (
                        "<b>Intrusion words:</b> "
                        f"{escaped_intrusions}"
                    ),
                    normal_style,
                )
            )

    story.append(Spacer(1, 0.16 * inch))
    story.append(
        Paragraph(
            (
                "<b>Important:</b> This custom score is experimental. "
                "It is not a diagnosis or a clinically validated "
                "probability that a person has Alzheimer's disease."
            ),
            normal_style,
        )
    )



# NEUROVOICE_MEMORY_RESULTS_ROUTE
# Returning from the optional memory task must preserve the completed
# speech assessment and open the final-results phase instead of Step 1.
_returning_from_memory = bool(
    st.session_state.pop("return_to_final_results", False)
)

if _returning_from_memory:
    # Different versions of the assessment page have used different
    # names for the current-step field. Update only keys that exist.
    _results_step_keys = (
        "test_step",
        "current_step",
        "assessment_step",
        "screening_step",
        "workflow_step",
        "active_step",
        "step",
    )

    for _step_key in _results_step_keys:
        if _step_key in st.session_state:
            _current_value = st.session_state[_step_key]

            if isinstance(_current_value, int):
                st.session_state[_step_key] = 3
            elif isinstance(_current_value, str):
                _normalized_value = _current_value.strip().lower()

                if _normalized_value.isdigit():
                    st.session_state[_step_key] = "3"
                else:
                    st.session_state[_step_key] = "results"

    # Explicit route flags used by the final-results renderer.
    st.session_state["show_final_results"] = True
    st.session_state["assessment_complete"] = True
    st.session_state["memory_completed"] = bool(
        st.session_state.get("memory_result")
    )


# NEUROVOICE_DARK_MEMORY_UI_CSS
DARK_MEMORY_UI_CSS = '\n<style>\n/* ==========================================================\n   NeuroVoice dark memory interface\n   ========================================================== */\n\n:root {\n    color-scheme: dark;\n}\n\nhtml,\nbody,\n[data-testid="stAppViewContainer"],\n[data-testid="stAppViewContainer"] > .main,\n.stApp {\n    background:\n        radial-gradient(\n            circle at 12% 8%,\n            rgba(54, 103, 255, 0.20),\n            transparent 28rem\n        ),\n        radial-gradient(\n            circle at 88% 18%,\n            rgba(120, 76, 255, 0.16),\n            transparent 30rem\n        ),\n        #070b14 !important;\n    color: #f7f9ff !important;\n}\n\n/* Hide Streamlit chrome that flashes during timed reruns. */\nheader[data-testid="stHeader"],\n[data-testid="stToolbar"],\n[data-testid="stDecoration"],\n[data-testid="stStatusWidget"],\n[data-testid="stMainMenu"],\n[data-testid="stAppDeployButton"],\n[data-testid="manage-app-button"],\n.stDeployButton,\n#MainMenu,\nfooter {\n    display: none !important;\n    visibility: hidden !important;\n    height: 0 !important;\n    min-height: 0 !important;\n    opacity: 0 !important;\n    pointer-events: none !important;\n}\n\n/* Remove the blank strip normally reserved for the header. */\n[data-testid="stAppViewBlockContainer"],\n.block-container {\n    padding-top: 1.5rem !important;\n}\n\n/* Standard Streamlit text. */\nh1,\nh2,\nh3,\nh4,\nh5,\nh6,\np,\nli,\nlabel,\nspan,\n[data-testid="stMarkdownContainer"] {\n    color: #f7f9ff;\n}\n\n[data-testid="stCaptionContainer"],\n.stCaption,\nsmall {\n    color: #aebbd2 !important;\n}\n\n/* Dark cards and containers. */\ndiv[data-testid="stVerticalBlockBorderWrapper"],\n[data-testid="stForm"],\n.nv-card {\n    background: rgba(14, 21, 36, 0.96) !important;\n    border: 1px solid #2b3852 !important;\n    box-shadow: 0 18px 55px rgba(0, 0, 0, 0.40) !important;\n}\n\n/* Existing memory-page typography. */\n.nv-kicker {\n    color: #79a8ff !important;\n}\n\n.nv-title,\n.nv-memory-title,\n.nv-section-title {\n    color: #ffffff !important;\n    text-shadow: 0 2px 20px rgba(76, 130, 255, 0.18);\n}\n\n.nv-subtitle,\n.nv-memory-subtitle,\n.nv-section-copy {\n    color: #c4cee0 !important;\n}\n\n/* Study board. */\n.nv-word-board {\n    background:\n        radial-gradient(\n            circle at 18% 18%,\n            rgba(65, 105, 225, 0.14),\n            transparent 34%\n        ),\n        linear-gradient(\n            145deg,\n            #0d1423,\n            #111b2d\n        ) !important;\n    border: 1px solid #34445f !important;\n    box-shadow:\n        inset 0 0 0 1px rgba(255, 255, 255, 0.025),\n        0 20px 55px rgba(0, 0, 0, 0.34) !important;\n}\n\n/* Words shown during memorization. */\n.nv-word,\n.nv-scattered-word {\n    background: #17233a !important;\n    border: 1px solid #47618b !important;\n    box-shadow:\n        0 10px 28px rgba(0, 0, 0, 0.36),\n        inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;\n    color: #ffffff !important;\n    opacity: 1 !important;\n    visibility: visible !important;\n    text-shadow: none !important;\n}\n\n/* Timer. */\n.nv-timer,\n.nv-timer-value {\n    background: #152746 !important;\n    border: 1px solid #4169a8 !important;\n    color: #a9c9ff !important;\n}\n\n/* Visual distraction task. */\n.nv-shape-area {\n    background: #0d1525 !important;\n    border: 1px solid #30405d !important;\n}\n\n.nv-shape {\n    background: #17233a !important;\n    border: 1px solid #45608b !important;\n    color: #8fb5ff !important;\n    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.38) !important;\n}\n\n/* Results. */\n.nv-stat {\n    background: #121d31 !important;\n    border: 1px solid #30415f !important;\n}\n\n.nv-stat-label {\n    color: #aebbd2 !important;\n}\n\n.nv-stat-value {\n    color: #ffffff !important;\n}\n\n.nv-note {\n    background: #111f38 !important;\n    border-left-color: #6d9fff !important;\n    color: #cbd7ea !important;\n}\n\n/* Inputs. */\n[data-testid="stTextArea"] textarea,\n[data-testid="stTextInput"] input,\ntextarea,\ninput {\n    background: #101a2b !important;\n    border: 1px solid #3c4f70 !important;\n    color: #ffffff !important;\n    caret-color: #ffffff !important;\n}\n\ntextarea::placeholder,\ninput::placeholder {\n    color: #8493aa !important;\n    opacity: 1 !important;\n}\n\n[data-testid="stTextArea"] textarea:focus,\n[data-testid="stTextInput"] input:focus {\n    border-color: #79a8ff !important;\n    box-shadow: 0 0 0 1px #79a8ff !important;\n}\n\n/* Buttons, including the memory yes/no choice. */\ndiv.stButton > button,\ndiv[data-testid="stButton"] > button,\nbutton[kind="primary"],\nbutton[kind="secondary"] {\n    min-height: 3.15rem !important;\n    border-radius: 13px !important;\n    border: 1px solid #49658f !important;\n    background: #17243a !important;\n    color: #ffffff !important;\n    font-weight: 760 !important;\n    box-shadow: 0 9px 24px rgba(0, 0, 0, 0.26) !important;\n}\n\ndiv.stButton > button:hover,\ndiv[data-testid="stButton"] > button:hover {\n    background: #223653 !important;\n    border-color: #7daaff !important;\n    color: #ffffff !important;\n}\n\ndiv.stButton > button[kind="primary"],\ndiv[data-testid="stButton"] > button[kind="primary"],\nbutton[kind="primary"] {\n    background: linear-gradient(\n        135deg,\n        #356ff0,\n        #694de5\n    ) !important;\n    border-color: #82a9ff !important;\n    color: #ffffff !important;\n}\n\ndiv.stButton > button[kind="primary"]:hover,\nbutton[kind="primary"]:hover {\n    background: linear-gradient(\n        135deg,\n        #477ff7,\n        #795cf0\n    ) !important;\n}\n\n/* Alerts. */\n[data-testid="stAlert"] {\n    background: #121e32 !important;\n    border: 1px solid #344866 !important;\n    color: #eef3ff !important;\n}\n\n/* Progress bars. */\n[data-testid="stProgress"] > div {\n    background: #1a2941 !important;\n}\n\n/* Sidebar remains readable. */\n[data-testid="stSidebar"] {\n    background: #0b111d !important;\n    border-right: 1px solid #27344b !important;\n}\n\n[data-testid="stSidebar"] * {\n    color: #edf3ff !important;\n}\n\n/* Prevent rerun animations from looking like text flashes. */\n.nv-word,\n.nv-scattered-word,\n.nv-word-board,\n.nv-card,\n.nv-timer,\n.nv-timer-value {\n    animation: none !important;\n    transition: none !important;\n}\n\n/* Remove iframe/component outlines occasionally visible during refresh. */\niframe {\n    border: 0 !important;\n}\n\n@media (max-width: 760px) {\n    [data-testid="stAppViewBlockContainer"],\n    .block-container {\n        padding-left: 1rem !important;\n        padding-right: 1rem !important;\n    }\n}\n</style>\n'

# NEUROVOICE_DARK_MEMORY_UI
st.markdown(
    DARK_MEMORY_UI_CSS,
    unsafe_allow_html=True,
)



__main__.LinguisticFeatures = LinguisticFeatures

BASE_DIR = Path(__file__).resolve().parents[1]
COOKIE_IMAGE = BASE_DIR / "assets" / "cookie_theft.png"


@st.cache_resource
def load_cookie_model():
    return CookieTheftEnsemble()


@st.cache_resource
def load_fluency_model():
    return AnimalFluencyModel()


def initialize_state():
    defaults = {
        "assessment_stage": "intro",
        "cookie_audio_bytes": None,
        "cookie_audio_duration": None,
        "cookie_transcript": None,
        "cookie_result": None,
        "fluency_audio_bytes": None,
        "fluency_audio_duration": None,
        "fluency_transcript": None,
        "fluency_result": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_assessment():
    for key in list(st.session_state.keys()):
        if key.startswith("cookie_") or key.startswith("fluency_"):
            del st.session_state[key]
    st.session_state.assessment_stage = "intro"
    st.rerun()


def run_countdown(next_stage: str, instruction: str):
    st.subheader(instruction)
    placeholder = st.empty()
    for value in (3, 2, 1):
        placeholder.markdown(
            f"<div style='font-size:5rem;font-weight:800;text-align:center'>{value}</div>",
            unsafe_allow_html=True,
        )
        time.sleep(1)
    placeholder.markdown(
        "<div style='font-size:3rem;font-weight:800;text-align:center'>Begin</div>",
        unsafe_allow_html=True,
    )
    time.sleep(0.6)
    st.session_state.assessment_stage = next_stage
    st.rerun()


def wav_duration(audio_bytes: bytes) -> float | None:
    try:
        with wave.open(BytesIO(audio_bytes), "rb") as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            return frames / float(rate)
    except (wave.Error, EOFError, ZeroDivisionError):
        return None


def show_progress(step: int):
    st.progress(step / 3)
    st.caption(f"Step {step} of 3")


def serializable_result(result: dict) -> dict:
    cleaned = {}
    for key, value in result.items():
        if hasattr(value, "item"):
            value = value.item()
        elif isinstance(value, (list, tuple)):
            value = [
                item.item() if hasattr(item, "item") else item
                for item in value
            ]
        cleaned[key] = value
    return cleaned


initialize_state()

PIPELINE_VERSION = "transcription-v3"

if st.session_state.get("pipeline_version") != PIPELINE_VERSION:
    for key in (
        "cookie_audio_bytes",
        "cookie_audio_duration",
        "cookie_transcript",
        "cookie_result",
        "fluency_audio_bytes",
        "fluency_audio_duration",
        "fluency_transcript",
        "fluency_result",
    ):
        st.session_state.pop(key, None)

    st.session_state.pipeline_version = PIPELINE_VERSION
    st.session_state.assessment_stage = "intro"

stage = st.session_state.assessment_stage

st.markdown("""
<style>
[data-testid="stAudioInput"] button {
    min-height: 110px !important;
    min-width: 110px !important;
    border-radius: 55px !important;
    font-size: 2rem !important;
}
[data-testid="stAudioInput"] {
    padding: 1.5rem;
    border: 2px solid rgba(120,120,120,0.35);
    border-radius: 18px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.title("NeuroVoice Language Assessment")
st.caption(
    "Complete the tasks in order. Audio is transcribed locally with the same "
    "memory-optimized Whisper method used during dataset preparation."
)


def create_results_pdf(
    cookie_result: dict,
    fluency_result: dict,
    cookie_transcript: str,
    fluency_transcript: str,
) -> bytes:
    from datetime import datetime
    from io import BytesIO
    from xml.sax.saxutils import escape

    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.lib import colors

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.65 * inch,
        rightMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="NeuroVoice Assessment Report",
        author="NeuroVoice",
    )

    styles = getSampleStyleSheet()
    story = []

    def safe(value) -> str:
        return escape("" if value is None else str(value))

    def status(result: dict) -> str:
        return (
            "Flagged by research model"
            if bool(result.get("flagged"))
            else "Not flagged by research model"
        )

    cookie_score = float(cookie_result.get("score", 0))
    cookie_threshold = float(cookie_result.get("threshold", 0))
    fluency_score = float(fluency_result.get("score", 0))
    fluency_threshold = float(fluency_result.get("threshold", 0))

    cookie_flagged = bool(cookie_result.get("flagged"))
    fluency_flagged = bool(fluency_result.get("flagged"))
    flagged_count = int(cookie_flagged) + int(fluency_flagged)

    if flagged_count == 0:
        summary = (
            "Neither task crossed its task-specific decision threshold."
        )
    elif flagged_count == 1:
        summary = (
            "One task crossed its task-specific decision threshold."
        )
    else:
        summary = (
            "Both tasks crossed their task-specific decision thresholds."
        )

    story.append(
        Paragraph(
            "NeuroVoice Language Assessment Report",
            styles["Title"],
        )
    )

    story.append(
        Paragraph(
            safe(
                datetime.now().strftime(
                    "Generated %B %d, %Y at %I:%M %p"
                )
            ),
            styles["Normal"],
        )
    )

    story.append(Spacer(1, 14))

    story.append(
        Paragraph(
            "Overall summary",
            styles["Heading2"],
        )
    )

    story.append(
        Paragraph(
            safe(summary),
            styles["BodyText"],
        )
    )

    story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            (
                "<b>Research-use notice:</b> These scores are experimental "
                "model outputs. They are not a diagnosis, clinical screening "
                "result, disease probability, or measurement of disease "
                "severity. The two task scores should not be averaged."
            ),
            styles["BodyText"],
        )
    )

    story.append(Spacer(1, 14))

    story.append(
        Paragraph(
            "Cookie Theft Picture Description Task",
            styles["Heading2"],
        )
    )

    cookie_table = Table(
        [
            ["Measure", "Result"],
            ["Model score", f"{cookie_score:.3f}"],
            ["Decision threshold", f"{cookie_threshold:.2f}"],
            ["Status", status(cookie_result)],
            [
                "Threshold difference",
                (
                    f"{cookie_score - cookie_threshold:.3f}"
                    if cookie_score >= cookie_threshold
                    else f"-{cookie_threshold - cookie_score:.3f}"
                ),
            ],
        ],
        colWidths=[2.4 * inch, 4.2 * inch],
    )

    cookie_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(cookie_table)
    story.append(Spacer(1, 10))

    story.append(
        Paragraph(
            "<b>Generated transcript</b>",
            styles["BodyText"],
        )
    )

    story.append(
        Paragraph(
            safe(cookie_transcript),
            styles["BodyText"],
        )
    )

    individual_scores = cookie_result.get(
        "individual_scores",
        {},
    )

    if individual_scores:
        story.append(Spacer(1, 10))
        story.append(
            Paragraph(
                "Component-model scores",
                styles["Heading3"],
            )
        )

        component_rows = [["Component", "Score"]]

        for name, value in individual_scores.items():
            component_rows.append(
                [
                    safe(name.replace("_", " ").title()),
                    f"{float(value):.3f}",
                ]
            )

        component_table = Table(
            component_rows,
            colWidths=[4.8 * inch, 1.8 * inch],
        )

        component_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        story.append(component_table)

    story.append(Spacer(1, 16))

    story.append(
        Paragraph(
            "Semantic Verbal Fluency Test",
            styles["Heading2"],
        )
    )

    features = fluency_result.get("features", {})

    fluency_rows = [
        ["Measure", "Result"],
        ["Model score", f"{fluency_score:.3f}"],
        ["Decision threshold", f"{fluency_threshold:.2f}"],
        ["Status", status(fluency_result)],
        [
            "Animal-name items",
            str(int(features.get("clean_total_items", 0))),
        ],
        [
            "Unique animal names",
            str(int(features.get("clean_unique_items", 0))),
        ],
        [
            "Repeated names",
            str(int(features.get("clean_repetition_count", 0))),
        ],
        [
            "Unique-name ratio",
            f'{float(features.get("clean_type_token_ratio", 0)):.1%}',
        ],
    ]

    fluency_table = Table(
        fluency_rows,
        colWidths=[2.4 * inch, 4.2 * inch],
    )

    fluency_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(fluency_table)
    story.append(Spacer(1, 10))

    story.append(
        Paragraph(
            "<b>Generated transcript</b>",
            styles["BodyText"],
        )
    )

    story.append(
        Paragraph(
            safe(fluency_transcript),
            styles["BodyText"],
        )
    )

    limitation = fluency_result.get("limitation")

    if limitation:
        story.append(Spacer(1, 10))
        story.append(
            Paragraph(
                "<b>Research limitation</b>",
                styles["BodyText"],
            )
        )
        story.append(
            Paragraph(
                safe(limitation),
                styles["BodyText"],
            )
        )

    story.append(Spacer(1, 16))

    story.append(
        Paragraph(
            "Interpretation guidance",
            styles["Heading2"],
        )
    )

    guidance = [
        "A score above a task's threshold causes that task to be flagged.",
        "The score is not a percentage chance of disease.",
        "A higher score does not necessarily indicate greater impairment.",
        "Recording and transcription accuracy can affect the result.",
        "The models require external validation before clinical use.",
    ]

    for item in guidance:
        story.append(
            Paragraph(
                "? " + safe(item),
                styles["BodyText"],
            )
        )


    # NEUROVOICE_OVERALL_WEIGHTING_PDF
    _nv_append_overall_to_pdf(story, styles)

    document.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


if stage == "intro":
    show_progress(0)
    st.header("Two-part assessment")
    st.write(
        """
        You will complete the **Cookie Theft Picture Description Task** followed by
        the **Semantic Verbal Fluency Test**. Tasks cannot be skipped.

        The website records your voice, transcribes it automatically, runs the
        corresponding research model, and then displays both task results.
        """
    )
    st.warning(
        "Research prototype only. This assessment does not provide a medical diagnosis."
    )
    if st.button("Take the test", type="primary", use_container_width=True):
        st.session_state.assessment_stage = "cookie_instructions"
        st.rerun()

elif stage == "cookie_instructions":
    show_progress(1)
    st.header("Cookie Theft Picture Description Task")

    if COOKIE_IMAGE.exists():
        st.image(str(COOKIE_IMAGE), width=650)
    else:
        st.error(
            "Cookie Theft image not found. Place your authorized image at "
            "`assets/cookie_theft.png`."
        )
        st.stop()

    st.write(
        """
        Look carefully at the picture. Describe everything you see happening,
        using complete sentences. Speak continuously for about **40 seconds**.
        """
    )

    if st.button(
        "Start Cookie Theft task",
        type="primary",
        use_container_width=True,
    ):
        st.session_state.assessment_stage = "cookie_record"
        st.rerun()

elif stage == "cookie_countdown":
    show_progress(1)
    if COOKIE_IMAGE.exists():
        st.image(str(COOKIE_IMAGE), width=650)
    run_countdown(
        "cookie_record",
        "Get ready to describe the picture",
    )

elif stage == "cookie_record":
    show_progress(1)
    st.header("Record your picture description")
    if COOKIE_IMAGE.exists():
        st.image(str(COOKIE_IMAGE), width=650)

    st.info(
        "Record one response of approximately 40 seconds. "
        "The browser recorder must be stopped manually."
    )

    st.markdown("""
<div style="padding:18px;border:2px solid #888;border-radius:16px;text-align:center;margin:16px 0;">
<div style="font-size:28px;font-weight:800;">Click the microphone below to start recording</div>
<div style="font-size:18px;margin-top:8px;">When you are finished, click the stop button. Speak for about 40 seconds.</div>
</div>
""", unsafe_allow_html=True)

    cookie_audio = st.audio_input(
        "Record the Cookie Theft description",
        sample_rate=16000,
        key="cookie_audio_widget",
    )

    if cookie_audio is not None:
        audio_bytes = cookie_audio.getvalue()
        duration = wav_duration(audio_bytes)
        st.audio(audio_bytes)

        if duration is not None:
            st.metric("Recording length", f"{duration:.1f} seconds")

        if duration is not None and duration < 30:
            st.error("The response is too short. Record for about 40 seconds.")
        elif duration is not None and duration > 55:
            st.error("The response is too long. Record for about 40 seconds.")
        elif st.button(
            "Transcribe and analyze Part 1",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.cookie_audio_bytes = audio_bytes
            st.session_state.cookie_audio_duration = duration
            with st.spinner("Transcribing and analyzing the Cookie Theft response..."):
                transcript = transcribe_audio_bytes(
                    audio_bytes,
                    task_name="cookie",
                )
                result = load_cookie_model().predict(transcript)

            st.session_state.cookie_transcript = transcript
            st.session_state.cookie_result = result
            st.session_state.assessment_stage = "fluency_instructions"
            st.rerun()

elif stage == "fluency_instructions":
    show_progress(2)
    st.header("Semantic Verbal Fluency Test")
    st.write(
        """
        **Name as many different animals as you can. Record your response for at least 60 seconds.**
        Do not describe the animalsâ€”only say their names. Keep going until the
        recording is finished.
        """
    )

    with st.expander("Part 1 completed"):
        st.write(st.session_state.cookie_transcript)
        st.caption(
            f"Cookie Theft score: "
            f"{st.session_state.cookie_result['score']:.3f} | "
            f"Threshold: {st.session_state.cookie_result['threshold']:.2f}"
        )

    if st.button(
        "Start Semantic Verbal Fluency Test",
        type="primary",
        use_container_width=True,
    ):
        st.session_state.assessment_stage = "fluency_record"
        st.rerun()

elif stage == "fluency_countdown":
    show_progress(2)
    run_countdown(
        "fluency_record",
        "Get ready to name animals",
    )

elif stage == "fluency_record":
    show_progress(2)
    st.header("Record the Semantic Verbal Fluency Test")
    st.info(
        "Name as many different animals as you can. Record your response for at least 60 seconds. "
        "The browser recorder must be stopped manually."
    )

    st.markdown("""
<div style="padding:18px;border:2px solid #888;border-radius:16px;text-align:center;margin:16px 0;">
<div style="font-size:28px;font-weight:800;">Click the microphone below to start recording</div>
<div style="font-size:18px;margin-top:8px;">Name as many different animals as you can. Click stop when you are finished.</div>
</div>
""", unsafe_allow_html=True)

    fluency_audio = st.audio_input(
        "Record the animal-naming response",
        sample_rate=16000,
        key="fluency_audio_widget",
    )

    if fluency_audio is not None:
        audio_bytes = fluency_audio.getvalue()
        duration = wav_duration(audio_bytes)
        st.audio(audio_bytes)

        if duration is not None:
            st.metric("Recording length", f"{duration:.1f} seconds")

        if duration is not None and duration < 60:
            st.error("The response is too short. Record for at least 60 seconds.")
        elif duration is not None and duration > 80:
            st.error("The response is too long. Record for approximately one minute.")
        elif st.button(
            "Transcribe and analyze Part 2",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.fluency_audio_bytes = audio_bytes
            st.session_state.fluency_audio_duration = duration
            with st.spinner("Transcribing and analyzing the fluency response..."):
                transcript = transcribe_audio_bytes(
                    audio_bytes,
                    task_name="fluency",
                )
                result = load_fluency_model().predict(transcript)

            st.session_state.fluency_transcript = transcript
            st.session_state.fluency_result = result
            st.session_state.assessment_stage = "results"
            st.rerun()

elif stage == "results":
    show_progress(3)
    st.header("Assessment results")

    cookie_result = serializable_result(
        st.session_state.cookie_result
    )
    fluency_result = serializable_result(
        st.session_state.fluency_result
    )

    def show_task_status(
        result: dict,
        task_name: str,
    ) -> None:
        score = float(result["score"])
        threshold = float(result["threshold"])
        difference = score - threshold
        flagged = bool(result["flagged"])

        if flagged:
            st.warning(
                f"**{task_name} was flagged by its research model.**"
            )
            st.write(
                f"The model score was **{score:.3f}**, which is "
                f"**{abs(difference):.3f} above** the decision "
                f"threshold of **{threshold:.2f}**."
            )
        else:
            st.success(
                f"**{task_name} was not flagged by its research model.**"
            )
            st.write(
                f"The model score was **{score:.3f}**, which is "
                f"**{abs(difference):.3f} below** the decision "
                f"threshold of **{threshold:.2f}**."
            )

        st.caption(
            "A higher score means the response more closely matched "
            "patterns associated with the model's flagged class. "
            "It does not measure disease severity."
        )

    cookie_flagged = bool(cookie_result["flagged"])
    fluency_flagged = bool(fluency_result["flagged"])

    flagged_count = int(cookie_flagged) + int(
        fluency_flagged
    )

    st.subheader("Overall summary")

    if flagged_count == 0:
        st.success(
            "Neither task crossed its task-specific decision threshold."
        )
        st.write(
            "The two research models did not flag the recorded responses. "
            "This does not rule out cognitive or neurological conditions."
        )

    elif flagged_count == 1:
        st.warning(
            "One of the two tasks crossed its task-specific decision threshold."
        )
        st.write(
            "The tasks measure different aspects of language. A flag on one "
            "task should be interpreted separately from the other task."
        )

    else:
        st.warning(
            "Both tasks crossed their task-specific decision thresholds."
        )
        st.write(
            "Both research models identified response patterns resembling "
            "their flagged training classes. This is not a diagnosis and "
            "does not establish that the participant has Alzheimer's disease."
        )

    st.info(
        "These results are experimental research outputs. They are not a "
        "medical diagnosis, clinical screening result, or disease probability. "
        "The two scores are not averaged because the models were trained for "
        "different language tasks."
    )

    st.divider()

    first, second = st.columns(2)

    with first:
        st.subheader(
            "Cookie Theft Picture Description Task"
        )

        show_task_status(
            cookie_result,
            "The Cookie Theft Picture Description Task",
        )

        st.markdown("#### What this task examines")

        st.write(
            "This task examines connected speech, including vocabulary, "
            "sentence construction, information content, and linguistic "
            "patterns found in the picture description."
        )

        individual_scores = cookie_result.get(
            "individual_scores",
            {},
        )

        if individual_scores:
            with st.expander(
                "View component-model scores"
            ):
                component_names = {
                    "word_tfidf_svm": (
                        "Word-pattern model"
                    ),
                    "char_tfidf_svm": (
                        "Character-pattern model"
                    ),
                    "linguistic_logreg": (
                        "Linguistic-feature model"
                    ),
                    "word_char_linguistic_logreg": (
                        "Combined language model"
                    ),
                }

                for key, value in individual_scores.items():
                    label = component_names.get(
                        key,
                        key.replace("_", " ").title(),
                    )

                    st.metric(
                        label,
                        f"{float(value):.3f}",
                    )

        with st.expander(
            "View generated transcript"
        ):
            st.write(
                st.session_state.cookie_transcript
            )

        with st.expander(
            "View complete technical output"
        ):
            st.json(cookie_result)

    with second:
        st.subheader(
            "Semantic Verbal Fluency Test"
        )

        show_task_status(
            fluency_result,
            "The Semantic Verbal Fluency Test",
        )

        st.markdown("#### What this task examines")

        st.write(
            "This task examines semantic retrieval: how efficiently the "
            "participant retrieves different animal names from memory while "
            "avoiding unnecessary repetitions."
        )

        features = fluency_result.get(
            "features",
            {},
        )

        if features:
            st.markdown(
                "#### Response characteristics"
            )

            total_items = int(
                features.get(
                    "clean_total_items",
                    0,
                )
            )

            unique_items = int(
                features.get(
                    "clean_unique_items",
                    0,
                )
            )

            repetitions = int(
                features.get(
                    "clean_repetition_count",
                    0,
                )
            )

            type_token_ratio = float(
                features.get(
                    "clean_type_token_ratio",
                    0,
                )
            )

            metric_one, metric_two = st.columns(2)

            with metric_one:
                st.metric(
                    "Animal names spoken",
                    total_items,
                )

                st.metric(
                    "Repeated names",
                    repetitions,
                )

            with metric_two:
                st.metric(
                    "Unique animal names",
                    unique_items,
                )

                st.metric(
                    "Unique-name ratio",
                    f"{type_token_ratio:.2%}",
                )

            st.caption(
                "The unique-name ratio is the number of unique animal names "
                "divided by the total number of recognized items. Repetitions "
                "lower this ratio."
            )

        limitation = fluency_result.get(
            "limitation"
        )

        if limitation:
            st.warning(
                "Important validation limitation: "
                + str(limitation)
            )

        with st.expander(
            "View generated transcript"
        ):
            st.write(
                st.session_state.fluency_transcript
            )

        with st.expander(
            "View complete technical output"
        ):
            st.json(fluency_result)

    st.divider()

    st.subheader("How to interpret these results")

    st.write(
        """
        - A **score above the threshold** causes that task to be flagged.
        - The score is a model output, not a percentage chance of disease.
        - A score farther above the threshold does not necessarily indicate
          more severe impairment.
        - Transcription accuracy directly affects both model results.
        - Results should only be considered alongside qualified clinical
          evaluation and validated cognitive testing.
        """
    )


    pdf_report = create_results_pdf(
        cookie_result=cookie_result,
        fluency_result=fluency_result,
        cookie_transcript=st.session_state.cookie_transcript,
        fluency_transcript=st.session_state.fluency_transcript,
    )

    # NEUROVOICE_OVERALL_WEIGHTING_RESULTS
    _nv_render_overall_results()

    st.download_button(
        label="Download PDF report",
        data=pdf_report,
        file_name="NeuroVoice_Assessment_Report.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True,
    )

    st.caption(
        "The PDF contains both transcripts, model scores, thresholds, "
        "fluency features, interpretation guidance, and the research-use notice."
    )

    if st.button(
        "Take the assessment again",
        type="primary",
        use_container_width=True,
    ):
        reset_assessment()




