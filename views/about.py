import streamlit as st


st.html(
    """
<style>
.about-hero {
    margin-top: 1rem;
    padding: 3.5rem;
    border-radius: 28px;
    background:
        linear-gradient(
            135deg,
            rgba(34, 68, 108, 0.78),
            rgba(67, 45, 139, 0.66)
        );
    border: 1px solid rgba(255, 255, 255, 0.11);
}

.about-hero h1 {
    color: white;
    font-size: clamp(3rem, 7vw, 5rem);
    letter-spacing: -0.055em;
    line-height: 1;
    margin: 0 0 1rem;
}

.about-hero p {
    max-width: 760px;
    color: #c5d1e2;
    font-size: 1.1rem;
    line-height: 1.75;
}

.about-card {
    min-height: 210px;
    padding: 1.8rem;
    border-radius: 22px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.09);
}

.about-card h3 {
    color: white;
}

.about-card p {
    color: #adbbce;
    line-height: 1.7;
}
</style>

<section class="about-hero">
    <h1>About NeuroVoice</h1>

    <p>
        NeuroVoice is a student-built research prototype exploring how
        language tasks and machine learning can be used to study patterns
        associated with cognitive impairment.
    </p>
</section>
"""
)


st.markdown("## Why this project exists")

st.write(
    """
Changes in language can appear in connected speech, word retrieval, repetition,
and semantic fluency. This project investigates whether those patterns can be
measured using carefully processed participant-only speech and transcripts.
"""
)


left, middle, right = st.columns(3, gap="large")

with left:
    st.html(
        """
<div class="about-card">
    <h3>Current stage</h3>
    <p>
        Two trained task-specific models are connected to a working
        Streamlit research website.
    </p>
</div>
"""
    )

with middle:
    st.html(
        """
<div class="about-card">
    <h3>Next development</h3>
    <p>
        Add audio recording, automatic transcription, stronger interface
        design and external validation.
    </p>
</div>
"""
    )

with right:
    st.html(
        """
<div class="about-card">
    <h3>Long-term goal</h3>
    <p>
        Build a more rigorous multimodal cognitive-language research
        platform using matched participants and clinically appropriate validation.
    </p>
</div>
"""
    )


st.markdown("## Important note")

st.warning(
    """
NeuroVoice is not a medical device and does not provide a diagnosis.
Its outputs are intended for educational and research demonstration only.
"""
)

st.divider()
st.header("Privacy and data handling")

st.markdown(
    """
NeuroVoice processes audio recordings to generate transcripts and research-model results.

- Recordings are used temporarily for transcription and analysis.
- NeuroVoice does not intentionally save participant recordings after processing.
- Recordings and transcripts are not used to train the models through this website.
- Users should not submit names, addresses, medical-record numbers, or other identifying information.
- Temporary files may exist briefly while the server processes a recording.
- The hosting provider may maintain technical logs under its own policies.
- Downloaded reports remain on the user's device and are the user's responsibility.

NeuroVoice is an experimental research and educational project. Its results are not a medical diagnosis, clinical screening result, disease probability, or substitute for evaluation by a qualified healthcare professional.
"""
)
