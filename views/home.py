import streamlit as st


st.html(
    """
<style>
.hero {
    margin-top: 2rem;
    padding: 5rem 3.5rem;
    border-radius: 30px;
    background:
        linear-gradient(
            135deg,
            rgba(39, 76, 119, 0.78),
            rgba(67, 44, 143, 0.68)
        );
    border: 1px solid rgba(255, 255, 255, 0.13);
    box-shadow: 0 30px 80px rgba(0, 0, 0, 0.32);
}

.hero-label {
    display: inline-block;
    padding: 0.45rem 0.85rem;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.10);
    border: 1px solid rgba(255, 255, 255, 0.16);
    color: #d2dcff;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.08em;
}

.hero h1 {
    margin: 1.3rem 0 1rem;
    color: white;
    font-size: clamp(3rem, 7vw, 5.6rem);
    line-height: 0.98;
    letter-spacing: -0.06em;
}

.gradient-text {
    background: linear-gradient(
        90deg,
        #86c7ff,
        #ac9cff,
        #6ce1cd
    );
    background-clip: text;
    -webkit-background-clip: text;
    color: transparent;
    -webkit-text-fill-color: transparent;
}

.hero p {
    max-width: 750px;
    color: #cad5e6;
    font-size: 1.15rem;
    line-height: 1.8;
}

.section-heading {
    margin-top: 3.2rem;
    margin-bottom: 1.5rem;
    color: white;
    font-size: 2rem;
    letter-spacing: -0.035em;
}

.feature-card {
    min-height: 220px;
    padding: 2rem;
    border-radius: 22px;
    background: rgba(255, 255, 255, 0.055);
    border: 1px solid rgba(255, 255, 255, 0.10);
}

.feature-card h3 {
    color: white;
    margin-top: 0;
}

.feature-card p {
    color: #adbbcf;
    line-height: 1.7;
}
</style>

<section class="hero">
    <div class="hero-label">
        RESEARCH-BASED LANGUAGE ANALYSIS
    </div>

    <h1>
        Cognitive screening<br>
        through <span class="gradient-text">language.</span>
    </h1>

    <p>
        NeuroVoice combines a Cookie Theft Picture Description Task and the Semantic Verbal Fluency Test to examine complementary patterns in
        connected speech and semantic retrieval.
    </p>
</section>

<h2 class="section-heading">
    One assessment, two language tasks
</h2>
"""
)


left, right = st.columns(2, gap="large")

with left:
    st.html(
        """
<div class="feature-card">
    <h3>01 - Picture Description</h3>
    <p>
        The participant describes a complex visual scene.
        The connected-speech ensemble evaluates vocabulary,
        repetition, information content and language organization.
    </p>
</div>
"""
    )

with right:
    st.html(
        """
<div class="feature-card">
    <h3>02 - Semantic Verbal Fluency Test</h3>
    <p>
        The participant names as many animals as possible.
        The semantic verbal fluency model examines response quantity,
        uniqueness, repetition and lexical diversity.
    </p>
</div>
"""
    )


st.write("")

st.page_link(
    "views/test.py",
    label="Start the two-part assessment",
    use_container_width=True,
)

st.caption(
    "Research prototype only. "
    "NeuroVoice does not provide a medical diagnosis."
)
