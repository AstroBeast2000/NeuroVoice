import streamlit as st


st.html(
    """
<style>
.page-label {
    display: inline-block;
    margin-top: 1rem;
    padding: 0.42rem 0.85rem;
    border-radius: 999px;
    background: rgba(112, 132, 255, 0.13);
    border: 1px solid rgba(112, 132, 255, 0.28);
    color: #c3cdff;
    font-size: 0.8rem;
    font-weight: 750;
    letter-spacing: 0.08em;
}

.page-title {
    color: white;
    margin-top: 1.15rem;
    margin-bottom: 0.9rem;
    font-size: clamp(3rem, 6vw, 4.9rem);
    line-height: 1;
    letter-spacing: -0.055em;
}

.page-subtitle {
    max-width: 850px;
    color: #b3c0d2;
    font-size: 1.1rem;
    line-height: 1.8;
    margin-bottom: 2.8rem;
}

.step-card {
    min-height: 250px;
    padding: 1.9rem;
    border-radius: 22px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.09);
}

.step-number {
    color: #91a7ff;
    font-size: 0.83rem;
    font-weight: 800;
    letter-spacing: 0.1em;
}

.step-card h3 {
    color: white;
    margin-top: 0.8rem;
    margin-bottom: 0.7rem;
}

.step-card p {
    color: #adbbce;
    line-height: 1.72;
}

.info-card {
    padding: 2rem;
    border-radius: 22px;
    background: rgba(255, 255, 255, 0.045);
    border: 1px solid rgba(255, 255, 255, 0.08);
    margin-bottom: 1rem;
}

.info-card h3 {
    color: white;
    margin-top: 0;
}

.info-card p,
.info-card li {
    color: #b5c1d2;
    line-height: 1.75;
}

.result-card {
    min-height: 235px;
    padding: 1.8rem;
    border-radius: 22px;
    background:
        linear-gradient(
            145deg,
            rgba(86, 109, 255, 0.12),
            rgba(125, 85, 233, 0.08)
        );
    border: 1px solid rgba(132, 151, 255, 0.18);
}

.result-card h3 {
    color: white;
    margin-top: 0;
}

.result-card p {
    color: #b6c3d5;
    line-height: 1.72;
}

.section-title {
    color: white;
    margin-top: 3rem;
    margin-bottom: 0.6rem;
    font-size: 2rem;
    letter-spacing: -0.035em;
}

.section-intro {
    max-width: 860px;
    color: #9fadc1;
    line-height: 1.75;
    margin-bottom: 1.5rem;
}
</style>

<div class="page-label">HOW IT WORKS</div>

<h1 class="page-title">
    From language task<br>
    to research output.
</h1>

<p class="page-subtitle">
    NeuroVoice uses two different language tasks because cognitive change
    can affect more than one part of communication. Picture description
    measures connected speech, while semantic verbal fluency measures rapid semantic
    retrieval. Each response is analyzed by its own task-specific model,
    and the outputs are displayed together without being presented as a
    clinical diagnosis.
</p>
"""
)


columns = st.columns(4, gap="medium")

steps = [
    (
        "STEP 01",
        "Complete the Cookie Theft Picture Description Task",
        (
            "The participant describes everything happening in a complex "
            "visual scene. This produces connected speech containing sentence "
            "structure, vocabulary, pronouns, repetition, information units, "
            "hesitations and organizational patterns."
        ),
    ),
    (
        "STEP 02",
        "Complete the semantic verbal fluency task",
        (
            "The participant names as many animals as possible. This task "
            "tests how quickly words can be retrieved from one semantic "
            "category and allows the system to measure total responses, "
            "unique responses, repetitions and lexical diversity."
        ),
    ),
    (
        "STEP 03",
        "Process each response separately",
        (
            "The picture-description transcript is sent through a four-model "
            "ensemble. The animal list is converted into numerical fluency "
            "features and passed into a separate logistic-regression pipeline."
        ),
    ),
    (
        "STEP 04",
        "Review the task-level results",
        (
            "The website compares each model score with its saved validation "
            "threshold. It then reports whether neither, one or both tasks "
            "were flagged, while keeping the two scores separate."
        ),
    ),
]

for column, step in zip(columns, steps):
    label, title, description = step

    with column:
        st.html(
            f"""
<div class="step-card">
    <div class="step-number">{label}</div>
    <h3>{title}</h3>
    <p>{description}</p>
</div>
"""
        )


st.html(
    """
<h2 class="section-title">Why use two different tasks?</h2>

<p class="section-intro">
    The tasks examine different language abilities. A person may perform
    differently on connected speech than on rapid category retrieval, so
    one task should not automatically replace the other.
</p>
"""
)

left, right = st.columns(2, gap="large")

with left:
    st.html(
        """
<div class="info-card">
    <h3>Picture Description</h3>

    <p>
        Picture description produces natural connected speech. Instead of
        answering a single factual question, the participant must identify
        important parts of a scene, organize them into a coherent explanation
        and select words and sentence structures in real time.
    </p>

    <p>The current model examines signals including:</p>

    <ul>
        <li>word and character patterns;</li>
        <li>vocabulary diversity;</li>
        <li>repetition and adjacent repeated words;</li>
        <li>filler words and vague language;</li>
        <li>pronoun use;</li>
        <li>scene-specific information units;</li>
        <li>sentence length and transcript length;</li>
        <li>combined transcript patterns;</li>
        <li>recording duration and energy;</li>
        <li>voiced speech and silence measurements;</li>
        <li>spectral, MFCC and chroma acoustic features;</li>
        <li>fusion of transcript and acoustic probabilities.</li>
    </ul>
</div>
"""
    )

with right:
    st.html(
        """
<div class="info-card">
    <h3>Semantic Verbal Fluency Test</h3>

    <p>
        The Semantic Verbal Fluency Test is a timed semantic-retrieval task in which participants name animals. The participant
        must repeatedly search one category, avoid unnecessary repetition
        and continue producing valid examples as the most obvious animals
        are exhausted.
    </p>

    <p>The current model uses four cleaned features:</p>

    <ul>
        <li>total valid animal responses;</li>
        <li>number of unique animal responses;</li>
        <li>number of repeated responses;</li>
        <li>type-token ratio, or unique responses divided by total responses.</li>
    </ul>

    <p>
        These features are standardized inside the saved model pipeline before
        the classification score is produced.
    </p>
</div>
"""
    )


st.html(
    """
<h2 class="section-title">How the picture-description model works</h2>

<p class="section-intro">
    The picture-description system is an ensemble rather than one single
    classifier. Four models produce separate outputs, and those outputs are
    combined using validation-selected weights.
</p>
"""
)

picture_columns = st.columns(4, gap="medium")

picture_models = [
    (
        "Word TF-IDF",
        (
            "Examines informative words and short word sequences. It captures "
            "which terms appear and how strongly they resemble patterns found "
            "in the training data."
        ),
    ),
    (
        "Character TF-IDF",
        (
            "Examines smaller character patterns. This can capture spelling, "
            "word fragments and stylistic patterns that may be missed by a "
            "word-only representation."
        ),
    ),
    (
        "Linguistic Features",
        (
            "Uses 26 manually defined transcript measurements such as length, "
            "repetition, fillers, vague words, pronouns and picture-content units."
        ),
    ),
    (
        "Combined Model",
        (
            "Combines word, character and linguistic information in a single "
            "pipeline, allowing broader transcript patterns to influence the score."
        ),
    ),
]

for column, model_info in zip(picture_columns, picture_models):
    title, description = model_info

    with column:
        st.html(
            f"""
<div class="result-card">
    <h3>{title}</h3>
    <p>{description}</p>
</div>
"""
        )


st.write("")

st.info(
    """
The transcript and acoustic probabilities are combined by the trained stacking model.
0.15, 0.05 and 0.35. The final ensemble output is compared with a decision
threshold of 0.61.
"""
)


st.html(
    """
<h2 class="section-title">How the semantic verbal fluency model works</h2>
"""
)

st.html(
    """
<div class="info-card">
    <h3>Feature extraction and prediction</h3>

    <p>
        The participant response is normalized and converted into the same
        four measurements used when the model was trained. These values are
        placed in the exact saved feature order and sent into a pipeline
        containing median imputation, standard scaling and logistic regression.
    </p>

    <p>
        The model returns a score for the positive class. That score is compared
        with the saved threshold of 0.52. A score at or above the threshold is
        considered flagged by the research model.
    </p>

    <p>
        The model was developed using Pitt AD participants and WLS controls.
        Because diagnosis and dataset source are connected in that development
        sample, external validation on better-matched participants is required.
    </p>
</div>
"""
)


st.html(
    """
<h2 class="section-title">What happens on the Results page?</h2>

<p class="section-intro">
    The Results section displays both task outputs side by side. It does not
    average them into one medical probability.
</p>
"""
)

result_left, result_middle, result_right = st.columns(3, gap="large")

with result_left:
    st.html(
        """
<div class="result-card">
    <h3>Neither task flagged</h3>
    <p>
        Both task scores are below their task-specific thresholds. This means
        neither model flagged the submitted responses. It does not prove the
        absence of cognitive impairment.
    </p>
</div>
"""
    )

with result_middle:
    st.html(
        """
<div class="result-card">
    <h3>One task flagged</h3>
    <p>
        One task score is above its threshold and the other is below. Because
        the tasks measure different language abilities, the results should be
        reviewed separately.
    </p>
</div>
"""
    )

with result_right:
    st.html(
        """
<div class="result-card">
    <h3>Both tasks flagged</h3>
    <p>
        Both task-specific models flagged their respective responses. This is
        still a research output and is not sufficient for a clinical conclusion.
    </p>
</div>
"""
    )


st.html(
    """
<h2 class="section-title">What the output does not mean</h2>
"""
)

st.warning(
    """
A model score is not the probability that a person has Alzheimer's disease.
The website does not diagnose Alzheimer's disease, dementia, MCI, Parkinson's
disease or another condition. The thresholds were selected during model
development and require additional external and clinical validation.
"""
)

