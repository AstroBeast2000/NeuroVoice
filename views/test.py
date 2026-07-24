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

import __main__
import time
import wave
from io import BytesIO
from pathlib import Path

import streamlit as st

from src.linguistic_features import LinguisticFeatures
from src.cookie_model import CookieTheftEnsemble
from src.fluency_model_v2 import AnimalFluencyModel
from src.transcription import transcribe_audio_bytes


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



