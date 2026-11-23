import streamlit as st


st.markdown(
    """
    <style>
    .nv-kicker { color: #aab9ff; font-weight: 800; letter-spacing: .12em; }
    .nv-title { color: white; font-size: clamp(2.6rem, 6vw, 4.5rem); line-height: 1.02; letter-spacing: -.05em; }
    .nv-copy { color: #b9c6d8; max-width: 850px; line-height: 1.75; font-size: 1.05rem; }
    .nv-card { background: rgba(255,255,255,.045); border: 1px solid rgba(255,255,255,.10); border-radius: 18px; padding: 1.35rem; min-height: 170px; }
    .nv-card h3 { color: white; margin-top: 0; }
    .nv-card p { color: #b9c6d8; line-height: 1.65; }
    </style>
    <div class="nv-kicker">HOW IT WORKS</div>
    <h1 class="nv-title">From speech to<br>research output.</h1>
    <p class="nv-copy">
      NeuroVoice uses two separate language tasks. The Cookie Theft task captures
      connected speech; Semantic Verbal Fluency examines animal-category word retrieval.
      Each task has its own model and output. The optional memory activity remains
      separate and is not combined into a weighted score.
    </p>
    """,
    unsafe_allow_html=True,
)

st.header("Application pipeline")
st.graphviz_chart(
    '''
    digraph neurovoice {
      rankdir=TB;
      graph [bgcolor="transparent", nodesep="0.35", ranksep="0.45"];
      node [shape=box, style="rounded,filled", fillcolor="#17243a", fontcolor="white", color="#8298d6", fontname="Arial"];
      edge [color="#9baedb", arrowsize="0.8"];
      audio [label="Audio input"];
      ffmpeg [label="FFmpeg: mono, 16-kHz audio"];
      whisper [label="Whisper transcription on server"];
      split [label="Task-specific transcript"];
      cookie [label="Cookie Theft: four text models\nweighted ensemble"];
      fluency [label="Fluency: four lexical/count features\nsaved classifier"];
      cresult [label="Cookie Theft result"];
      fresult [label="Fluency result"];
      report [label="Separate outputs and PDF report"];
      memory [label="Optional memory activity\n(separate descriptive result)", style="rounded,dashed,filled"];
      audio -> ffmpeg -> whisper -> split;
      split -> cookie -> cresult -> report;
      split -> fluency -> fresult -> report;
      memory -> report [style=dashed, label="not combined"];
    }
    ''',
    use_container_width=True,
)

st.header("Task 1 — Cookie Theft Picture Description")
left, right = st.columns([1, 1.25], gap="large")
with left:
    st.image("assets/cookie_theft.png", caption="Cookie Theft picture-description prompt", use_container_width=True)
with right:
    st.markdown(
        """
        The participant describes the scene. The application transcribes the recording
        with Whisper and passes the transcript to four text-based components:

        - word-level TF-IDF + linear SVM;
        - character-level TF-IDF + linear SVM;
        - engineered linguistic features + logistic regression;
        - combined word/character/linguistic representation.

        The component probabilities are combined using weights stored in the model
        configuration. The current app inference path does **not** load an acoustic
        classifier; audio is used for transcription.
        """
    )

st.header("Task 2 — Semantic Verbal Fluency")
st.markdown(
    """
    The participant names animals. The transcript is converted into four features:
    total alphabetic tokens, unique tokens, repeated tokens, and type-token ratio.
    The saved classifier processes these features using the same feature order used
    during model development.
    """
)
st.warning(
    "The current parser does not independently check whether every recognized word is an animal. "
    "Whisper transcription errors and non-animal words can therefore affect the features."
)

st.header("How to interpret the outputs")
a, b, c = st.columns(3, gap="medium")
with a:
    st.markdown(
        """<div class="nv-card"><h3>Below threshold</h3><p>The task-specific model score is below its saved research threshold. This does not rule out cognitive impairment or disease.</p></div>""",
        unsafe_allow_html=True,
    )
with b:
    st.markdown(
        """<div class="nv-card"><h3>Above threshold</h3><p>The task-specific model score is at or above its saved research threshold. This is not a diagnosis or a disease probability.</p></div>""",
        unsafe_allow_html=True,
    )
with c:
    st.markdown(
        """<div class="nv-card"><h3>Separate tasks</h3><p>The two task outputs are not averaged. They measure different language behaviors and have different development datasets.</p></div>""",
        unsafe_allow_html=True,
    )

st.error(
    "NeuroVoice is an experimental research prototype, not a medical device. "
    "Its outputs must not be used for diagnosis, clinical screening, or health-care decisions."
)
