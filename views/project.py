import streamlit as st
from pathlib import Path
import pandas as pd

st.title("Research & Data")
st.caption(
    "A research prototype for studying language patterns associated with cognitive impairment. "
    "This system is not a diagnosis or a medical device."
)

overview_tab, data_tab, models_tab, results_tab, limits_tab = st.tabs(
    ["Project Overview", "Datasets", "Models", "Results & Charts", "Limitations"]
)

BASE_DIR = Path(__file__).resolve().parents[1]
PICTURE_CHARTS = BASE_DIR / "assets" / "charts" / "picture"
FLUENCY_CHARTS = BASE_DIR / "assets" / "charts" / "fluency"
PICTURE_DATA = BASE_DIR / "assets" / "data" / "picture"
FLUENCY_DATA = BASE_DIR / "assets" / "data" / "fluency"

with overview_tab:
    st.header("Project overview")
    st.write(
        """
        NeuroVoice analyzes language produced during two established cognitive-language tasks.
        The **Cookie Theft Picture Description Task** evaluates connected speech, while the
        **Semantic Verbal Fluency Test** asks participants to name as many animals as possible.
        These tasks are analyzed separately because they measure different aspects of language
        and were developed from different datasets.
        """
    )

    st.subheader("Cookie Theft Picture Description Task")
    st.write(
        """
        Participants describe the Cookie Theft picture. The resulting transcript is analyzed
        using word patterns, character patterns, and engineered linguistic features. These
        features can reflect vocabulary use, sentence structure, repetition, information
        content, and other properties of connected speech.
        """
    )

    st.subheader("Semantic Verbal Fluency Test")
    st.write(
        """
        Participants name as many animals as possible during a semantic verbal fluency task.
        The current model analyzes total responses, unique responses, repetitions, and
        type-token ratio. The task is labeled by its formal name on the website, while the
        instructions explain that the participant should name animals.
        """
    )

    st.info(
        "The two task scores are not averaged into one disease probability. "
        "Each result is interpreted only against the threshold selected for that model."
    )

with data_tab:
    st.header("Datasets used in the broader project")
    st.write(
        """
        The broader research project combines six speech datasets into a unified dataset.
        The goal is to use participant-only speech whenever possible, preserve diagnosis and
        demographic metadata, prevent interviewer leakage, and separate subjects between
        training and testing.
        """
    )

    st.subheader("ADReSS 2020")
    st.write(
        """
        **ADReSS 2020** stands for *Alzheimer's Dementia Recognition through Spontaneous Speech*.
        It contains Cookie Theft picture-description recordings and transcripts from participants
        with Alzheimer's disease and cognitively healthy controls.

        The source folders include original recordings and participant-only recordings. This
        project uses only the participant-only files, such as `S001_PAR.wav`, rather than the
        original mixed-speaker recordings. This reduces the chance that the model learns features
        from the interviewer instead of the participant.
        """
    )

    st.subheader("ADReSS 2021")
    st.write(
        """
        **ADReSS 2021**, also called **ADReSSo 2021**, extends the ADReSS research challenge.
        It includes speech-based Alzheimer's disease classification and cognitive-decline
        prediction tasks.

        This project uses the prepared participant-only audio from the `patient_audio` folder,
        including files such as `adrso001_PAR_only.wav`. Diagnosis and progression information
        are kept separate because classification and decline prediction are different research
        targets.
        """
    )

    st.subheader("ADReSS-M")
    st.write(
        """
        **ADReSS-M** is a multilingual extension of the ADReSS family of datasets. Its recordings
        required a larger preprocessing pipeline before they could be included in the unified
        dataset.

        The completed processing steps include:

        - loudness normalization;
        - speaker diarization;
        - segmentation;
        - Whisper transcription;
        - removal of interviewer prompts;
        - participant-only speech extraction;
        - organization into consistent audio and transcript folders.

        The final processed structure includes `par_audio`, `par_audio_normalized`,
        `segmentation`, and `transcripts`. The canonical manifest uses the participant-only
        audio in `processed_diarized/par_audio`.
        """
    )

    st.subheader("Pitt Corpus")
    st.write(
        """
        The **Pitt Corpus** is distributed through DementiaBank. It contains speech and
        transcripts from participants with dementia and comparison participants across several
        tasks, including Cookie Theft picture description, verbal fluency, recall, and sentence
        production.

        Participant-only audio was extracted for this project so interviewer speech is not used
        as a model input. Pitt contributes a large portion of the Alzheimer's disease examples
        in the broader dataset.
        """
    )

    st.subheader("Lu Corpus")
    st.write(
        """
        The **Lu Corpus** is another DementiaBank source included in the unified project.
        Participant-only audio has already been extracted into a dedicated
        `participant_only_audio` folder. This lets the project use the participant's speech
        without including interviewer prompts or interviewer voice characteristics.
        """
    )

    st.subheader("Train/Test TalkBank release")
    st.write(
        """
        The separate **Train/Test TalkBank release** contains short participant-only recordings
        and transcripts. These samples were already prepared without interviewer speech, so they
        did not require the same diarization and segmentation pipeline used for some of the other
        datasets.
        """
    )

    st.subheader("Wisconsin Longitudinal Study")
    st.write(
        """
        The **Wisconsin Longitudinal Study**, abbreviated **WLS**, follows Wisconsin high-school
        graduates across adulthood. In the current Semantic Verbal Fluency Test model, WLS
        supplies the cognitively healthy comparison group, while the Alzheimer's disease group
        comes from the Pitt Corpus.

        Because diagnosis and dataset source are linked, this creates an important confounding
        risk: the model may learn differences between the two studies rather than only differences
        related to cognition.
        """
    )

    st.divider()
    st.subheader("Quality-reviewed unified dataset")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Training samples retained", "2,080")
        st.caption("No training recordings were removed during the reported quality-review pass.")
    with c2:
        st.metric("Test samples retained", "371")
        st.caption("33 of 404 test recordings were removed after manual audio-quality review.")

    st.subheader("Dataset design principles")
    st.markdown(
        """
        - Use participant-only speech whenever available.
        - Prevent the same subject from appearing in both training and testing.
        - Preserve diagnosis, age, sex, MMSE, dataset, subject ID, and recording ID when available.
        - Keep audio and transcripts aligned through a canonical manifest.
        - Record quality-control decisions instead of silently deleting samples.
        - Avoid interviewer leakage and dataset-source leakage whenever possible.
        """
    )

with models_tab:
    st.header("Current models")

    st.subheader("Cookie Theft Picture Description Task model")
    st.write(
        """
        The picture-description system is an ensemble of four components:
        """
    )
    st.markdown(
        """
        - word-level TF-IDF with a support vector machine;
        - character-level TF-IDF with a support vector machine;
        - logistic regression using engineered linguistic features;
        - logistic regression combining word, character, and linguistic features.
        """
    )
    st.write(
        """
        Their outputs are combined using weights of **0.45, 0.15, 0.05, and 0.35**.
        The selected decision threshold is **0.48**. On the quality-reviewed evaluation set of
        371 samples, the reported balanced accuracy was **88.69%** and ROC-AUC was **91.39%**.
        These are internal research results, not clinical validation results.
        """
    )

    st.subheader("Semantic Verbal Fluency Test model")
    st.write(
        """
        The current model analyzes the list of animals entered by the participant. Its four
        features are:
        """
    )
    st.markdown(
        """
        - total responses;
        - unique responses;
        - repeated responses;
        - type-token ratio.
        """
    )
    st.write(
        """
        The model was developed using **226 subjects**: 113 participants with Alzheimer's disease
        from the Pitt Corpus and 113 cognitively healthy comparison participants from the
        Wisconsin Longitudinal Study. Its selected threshold is **0.52**. The reported internal
        balanced accuracy was **89.82%** and ROC-AUC was **96.19%**.
        """
    )

    st.warning(
        "These performance values come from internal evaluation. They do not establish clinical "
        "accuracy or generalizability to hospitals, clinics, or the general population."
    )


with results_tab:
    st.header("Cookie Theft Picture Description Task results")

    picture_images = [
        ("Model performance summary", "FINAL_metrics_summary.png"),
        ("ROC curve", "FINAL_roc_curve.png"),
        ("Precision-recall curve", "FINAL_precision_recall_curve.png"),
        ("Confusion matrix", "FINAL_confusion_matrix.png"),
        ("Normalized confusion matrix", "FINAL_confusion_matrix_normalized.png"),
        ("Calibration curve", "FINAL_calibration_curve.png"),
        ("Probability distributions", "FINAL_probability_distributions.png"),
    ]

    for title, filename in picture_images:
        image_path = PICTURE_CHARTS / filename
        if image_path.exists():
            st.subheader(title)
            st.image(str(image_path), width=650)
        else:
            st.warning(f"Missing chart: {filename}")

    picture_metrics_path = PICTURE_DATA / "FINAL_metrics.csv"
    if picture_metrics_path.exists():
        st.subheader("Picture-description metrics")
        st.dataframe(pd.read_csv(picture_metrics_path), use_container_width=True)

    per_dataset_path = PICTURE_DATA / "FINAL_per_dataset_metrics.csv"
    if per_dataset_path.exists():
        st.subheader("Performance by dataset")
        st.dataframe(pd.read_csv(per_dataset_path), use_container_width=True)

    configuration_path = PICTURE_DATA / "validation_selected_configuration.csv"
    if configuration_path.exists():
        st.subheader("Selected validation configuration")
        st.dataframe(pd.read_csv(configuration_path), use_container_width=True)

    report_path = PICTURE_DATA / "FINAL_evaluation_report.txt"
    if report_path.exists():
        st.subheader("Evaluation report")
        st.code(report_path.read_text(encoding="utf-8", errors="replace"))

    st.divider()
    st.header("Semantic Verbal Fluency Test results")

    fluency_images = [
        ("Confusion matrix", "final_confusion_matrix.png"),
        ("ROC curve", "final_roc_curve.png"),
        ("Precision-recall curve", "final_precision_recall_curve.png"),
    ]

    for title, filename in fluency_images:
        image_path = FLUENCY_CHARTS / filename
        if image_path.exists():
            st.subheader(title)
            st.image(str(image_path), width=650)
        else:
            st.warning(f"Missing chart: {filename}")

    fluency_tables = [
        ("Fluency metrics", "final_metrics.csv"),
        ("Model coefficients", "final_coefficients.csv"),
        ("Bootstrap confidence intervals", "bootstrap_confidence_intervals.csv"),
        ("Nested cross-validation fold metrics", "nested_fold_metrics.csv"),
    ]

    for title, filename in fluency_tables:
        table_path = FLUENCY_DATA / filename
        if table_path.exists():
            st.subheader(title)
            st.dataframe(pd.read_csv(table_path), use_container_width=True)

    predictions_path = FLUENCY_DATA / "nested_out_of_fold_predictions.csv"
    if predictions_path.exists():
        with st.expander("Out-of-fold prediction data"):
            st.dataframe(pd.read_csv(predictions_path), use_container_width=True)

    st.caption(
        "These charts and tables report internal research evaluation. "
        "They do not establish clinical validity."
    )


with limits_tab:
    st.header("Important limitations")

    st.subheader("Dataset-source confounding")
    st.write(
        """
        The Semantic Verbal Fluency Test model compares Alzheimer's disease participants from
        Pitt with healthy participants from WLS. Because diagnosis and dataset source are linked,
        differences in recording conditions, transcription conventions, recruitment, age,
        education, demographics, or study procedures may influence the model.
        """
    )

    st.subheader("External validation")
    st.write(
        """
        Both models require testing on independent datasets collected under matched conditions.
        Internal evaluation alone is not enough to support real-world or clinical conclusions.
        """
    )
    st.subheader("Not a diagnosis")
    st.write(
        """
        A score above a research threshold does not mean that a participant has Alzheimer's
        disease, mild cognitive impairment, or another neurological condition. Language can be
        affected by age, education, language background, fatigue, anxiety, hearing, speech
        disorders, and many other factors.
        """
    )