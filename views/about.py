import streamlit as st

st.title("About NeuroVoice")

st.write(
    """
    NeuroVoice is a student-built research prototype exploring how speech and
    language tasks can be analyzed using transcription, linguistic feature
    extraction, and machine-learning models.
    """
)

st.header("Research focus")
st.write(
    """
    The application currently demonstrates two task-specific workflows:
    Cookie Theft picture description (connected speech) and Semantic Verbal
    Fluency (animal naming). The broader research work investigates datasets,
    preprocessing, participant-level evaluation, and the limits of speech-based
    machine-learning experiments.
    """
)

st.header("Current implementation")
st.write(
    """
    The Streamlit application uses Whisper transcription on the application
    server, a four-component transcript ensemble for Cookie Theft, and a
    separate four-feature model for Semantic Verbal Fluency. The optional
    memory activity is separate and is not combined into a weighted score.
    """
)

st.header("Privacy and data handling")
st.markdown(
    """
    - Audio is processed on the NeuroVoice application server, not solely on the participant's device.
    - The transcription pipeline creates temporary files inside a temporary directory; that directory is cleaned up when transcription finishes or raises an error.
    - The Streamlit audio-input widget may retain the uploaded recording for the active session. The app should not store an additional persistent copy of the recording in its own session state.
    - The application does not intentionally write uploaded recordings or transcripts to a project database.
    - The hosting provider may process technical logs and operational data under its own policies.
    - Do not submit names, addresses, medical-record numbers, or other identifying or sensitive health information.
    - Downloaded PDF reports are saved by the participant's browser/device.
    """
)

st.warning(
    "Before using the public demo, review the hosting provider's current privacy and retention policies. "
    "Do not upload identifiable or sensitive health information."
)

st.header("Important limitations")
st.markdown(
    """
    - NeuroVoice is not a medical device and is not clinically validated.
    - Model scores are not disease probabilities, diagnoses, or measures of impairment severity.
    - The stored Cookie Theft transcript–acoustic fusion evaluation is separate from the current transcript-only application inference path.
    - The fluency experiment has dataset-source confounding because Pitt supplies the AD group and WLS supplies the control group.
    - Whisper transcription and the current animal-response parser can introduce errors.
    """
)

st.header("Future research")
st.write(
    """
    Priorities include aligning application code with evaluated model artifacts,
    publishing reproducible participant-level evaluation scripts, testing on
    independent matched datasets, examining calibration and subgroup performance,
    and obtaining appropriate expert and clinical oversight before any clinical
    research or use.
    """
)
