import streamlit as st

st.title("About NeuroVoice")

st.write(
    """
NeuroVoice is a student-built research prototype exploring how language tasks
and machine learning can be used to study patterns associated with cognitive
impairment.
"""
)

st.header("Why this project exists")

st.write(
    """
Changes in language can appear in connected speech, word retrieval, repetition,
and semantic fluency. This project investigates whether those patterns can be
measured using carefully processed participant-only speech and transcripts.
"""
)

st.header("Current stage")

st.write(
    """
Two trained task-specific models are connected to a working Streamlit research
website. The app records speech, transcribes it using Whisper, analyzes each task
with a separate model, explains the results, and generates a downloadable PDF
report.
"""
)

st.header("Next development")

st.write(
    """
Future work includes external validation, evaluation on larger and more diverse
participant groups, stronger calibration, improved transcription testing, and
more rigorous comparison with clinically validated cognitive assessments.
"""
)

st.header("Long-term goal")

st.write(
    """
Build a more rigorous multimodal cognitive-language research platform using
matched participants, carefully controlled datasets, and clinically appropriate
validation.
"""
)

st.header("Privacy and data handling")

st.markdown(
    """
- Recordings are used temporarily for transcription and model analysis.
- NeuroVoice does not intentionally retain participant recordings after processing.
- Temporary audio files created by the transcription pipeline are deleted after the transcription attempt finishes.
- Recordings and transcripts are not used to retrain the models through this website.
- Users should not include names, addresses, medical-record numbers, or other identifying information in their responses.
- The hosting provider may maintain technical logs under its own policies.
- Downloaded reports remain on the user's device.
"""
)

st.header("Important note")

st.warning(
    """
NeuroVoice is not a medical device and does not provide a diagnosis. Its outputs
are experimental research results intended for educational and research
demonstration only.
"""
)
