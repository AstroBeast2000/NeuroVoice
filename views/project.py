from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[1]
PICTURE_CHARTS = BASE_DIR / "assets" / "charts" / "picture"
FLUENCY_CHARTS = BASE_DIR / "assets" / "charts" / "fluency"
PICTURE_DATA = BASE_DIR / "assets" / "data" / "picture"
FLUENCY_DATA = BASE_DIR / "assets" / "data" / "fluency"


def read_csv_if_present(path: Path):
    if not path.exists():
        return None
    try:
        return pd.read_csv(path)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        st.warning(f"Could not read {path.name}: {exc}")
        return None


def show_chart(directory: Path, filename: str, title: str, width: int = 760):
    path = directory / filename
    if path.exists():
        st.subheader(title)
        st.image(str(path), width=width)
    else:
        st.caption(f"Figure not available in this checkout: {filename}")


st.title("Research & Data")
st.caption(
    "Technical documentation and internal evaluation artifacts for an experimental "
    "speech-and-language research prototype. Not a diagnostic or clinical screening tool."
)

overview_tab, data_tab, models_tab, results_tab, limits_tab = st.tabs(
    ["Overview", "Data sources", "Application models", "Evaluation artifacts", "Limitations"]
)

with overview_tab:
    st.header("Project overview")
    st.write(
        """
        NeuroVoice explores language patterns in two tasks: the Cookie Theft Picture
        Description Task (connected speech) and Semantic Verbal Fluency (animal naming).
        Each task has its own feature representation and model. Their outputs are displayed
        separately; they are not combined into a disease probability.
        """
    )
    st.graphviz_chart(
        '''
        digraph neurovoice {
          rankdir=TB;
          node [shape=box, style="rounded,filled", fillcolor="#17243a", fontcolor="white", color="#6d86c9"];
          audio [label="Audio input"];
          whisper [label="FFmpeg preparation + Whisper transcription"];
          cookie [label="Cookie Theft transcript"];
          fluency [label="Animal-naming transcript"];
          textmodel [label="Four-component transcript ensemble"];
          features [label="Four lexical/count features"];
          cresult [label="Cookie Theft research output"];
          fresult [label="Fluency research output"];
          report [label="Separate task results / PDF"];
          audio -> whisper;
          whisper -> cookie;
          whisper -> fluency;
          cookie -> textmodel -> cresult -> report;
          fluency -> features -> fresult -> report;
        }
        ''',
        use_container_width=True,
    )
    st.info(
        "The optional memory activity is separate. It is not included in a weighted "
        "speech or Alzheimer's screening score."
    )

with data_tab:
    st.header("Research data sources")
    st.write(
        """
        The broader research workflow has involved multiple public or access-controlled
        speech resources. Their use varies by experiment; a dataset mentioned here did not
        necessarily train every model in the application.
        """
    )
    sources = [
        ("ADReSS 2020", "Cookie Theft picture-description recordings and transcripts for AD/control research."),
        ("ADReSSo 2021", "Speech-based Alzheimer's classification and cognitive-decline research tasks."),
        ("ADReSS-M", "Multilingual ADReSS extension; project preprocessing included diarization, segmentation, participant-speech extraction, and transcription."),
        ("Pitt Corpus (DementiaBank)", "Speech and transcripts across several tasks; supplies the AD group in the current fluency experiment."),
        ("Lu Corpus", "DementiaBank speech resource included in the broader preprocessing workflow."),
        ("Other TalkBank releases", "Additional participant speech/transcript material used in broader data preparation."),
        ("Wisconsin Longitudinal Study (WLS)", "Supplies the control group in the current fluency experiment."),
    ]
    for name, description in sources:
        with st.expander(name):
            st.write(description)

    st.warning(
        "The current Semantic Verbal Fluency experiment compares Pitt AD participants with "
        "WLS controls. Diagnosis and source dataset are linked, creating dataset-source "
        "confounding that nested cross-validation does not remove."
    )

    st.subheader("ADReSS-M quality-review record")
    c1, c2, c3 = st.columns(3)
    c1.metric("Training recordings", "2,080")
    c2.metric("Reviewed test recordings", "371")
    c3.metric("Excluded from test review", "33")
    st.caption(
        "The associated Cookie Theft evaluation report says 33 of 404 test recordings "
        "were removed after prior model-error inspection. These figures describe a "
        "post-hoc quality-reviewed subset, not an untouched independent test set."
    )

with models_tab:
    st.header("Models loaded by the current application")

    st.subheader("Cookie Theft Picture Description")
    st.write(
        """
        The current application code in `src/cookie_model.py` loads four transcript-only
        components. Audio is used to generate the transcript; the checked-in application
        inference path does not load an acoustic classifier.
        """
    )
    st.table(
        pd.DataFrame(
            [
                ["Word TF-IDF + linear SVM", "Word-level lexical patterns"],
                ["Character TF-IDF + linear SVM", "Character n-gram patterns"],
                ["Linguistic logistic regression", "Hand-engineered transcript features"],
                ["Combined text logistic regression", "Combined word, character, and linguistic representation"],
            ],
            columns=["Component", "Role"],
        )
    )
    config_path = BASE_DIR / "models" / "cookie" / "validation_selected_configuration.csv"
    config = read_csv_if_present(config_path)
    if config is not None and not config.empty:
        row = config.iloc[0]
        st.write(
            f"Saved threshold: **{float(row['threshold']):.2f}**. "
            f"Saved ensemble weights: **{row['weights']}**."
        )

    st.subheader("Semantic Verbal Fluency")
    st.write(
        """
        The current feature extractor derives total alphabetic tokens, unique tokens,
        repeated tokens, and type-token ratio from the transcript. The saved classifier
        uses those four values and a threshold of 0.52.
        """
    )
    st.warning(
        "The current tokenizer does not independently validate that each recognized word "
        "is an animal. This is a known limitation of the application-level feature extraction."
    )

with results_tab:
    st.header("Internal research evaluation artifacts")

    st.subheader("Cookie Theft transcript–acoustic fusion experiment")
    picture_metrics = read_csv_if_present(PICTURE_DATA / "FINAL_metrics.csv")
    if picture_metrics is not None and not picture_metrics.empty:
        row = picture_metrics.iloc[0]
        cols = st.columns(4)
        cols[0].metric("Accuracy", f"{float(row['accuracy']):.1%}")
        cols[1].metric("Balanced accuracy", f"{float(row['balanced_accuracy']):.1%}")
        cols[2].metric("ROC-AUC", f"{float(row['roc_auc']):.1%}")
        cols[3].metric("Average precision", f"{float(row['average_precision']):.1%}")
        st.caption(
            f"Artifact status: {row.get('evaluation_status', 'not specified')}. "
            "These metrics are from a separate transcript–acoustic fusion artifact, "
            "not the current four-component transcript-only app inference path."
        )
    show_chart(PICTURE_CHARTS, "FINAL_metrics_summary.png", "Fusion experiment: metric summary")
    show_chart(PICTURE_CHARTS, "FINAL_roc_curve.png", "Fusion experiment: ROC curve")
    show_chart(PICTURE_CHARTS, "FINAL_precision_recall_curve.png", "Fusion experiment: precision–recall curve")
    show_chart(PICTURE_CHARTS, "FINAL_confusion_matrix.png", "Fusion experiment: confusion matrix")

    report_path = PICTURE_DATA / "FINAL_evaluation_report.txt"
    if report_path.exists():
        with st.expander("Read the complete evaluation report and its caveats"):
            st.code(report_path.read_text(encoding="utf-8-sig", errors="replace"))

    st.error(
        "Important: the Cookie Theft report describes a post-hoc quality-filtered test subset "
        "(371 retained from 404 after prior model-error inspection). It is not an unbiased "
        "untouched-test estimate. The report also notes that the acoustic extraction source "
        "was unavailable and the fusion pipeline was reconstructed."
    )

    st.divider()
    st.subheader("Semantic Verbal Fluency nested cross-validation")
    fluency_metrics = read_csv_if_present(FLUENCY_DATA / "final_metrics.csv")
    if fluency_metrics is not None and not fluency_metrics.empty:
        row = fluency_metrics.iloc[0]
        cols = st.columns(4)
        cols[0].metric("Accuracy", f"{float(row['accuracy']):.1%}")
        cols[1].metric("Balanced accuracy", f"{float(row['balanced_accuracy']):.1%}")
        cols[2].metric("ROC-AUC", f"{float(row['roc_auc']):.1%}")
        cols[3].metric("Average precision", f"{float(row['average_precision']):.1%}")

    ci = read_csv_if_present(FLUENCY_DATA / "bootstrap_confidence_intervals.csv")
    if ci is not None and not ci.empty:
        auc_row = ci.loc[ci["metric"] == "roc_auc"]
        if not auc_row.empty:
            row = auc_row.iloc[0]
            st.caption(
                f"ROC-AUC 95% bootstrap interval: "
                f"{float(row['ci_95_lower']):.1%}–{float(row['ci_95_upper']):.1%}."
            )

    show_chart(FLUENCY_CHARTS, "final_confusion_matrix.png", "Fluency: confusion matrix")
    show_chart(FLUENCY_CHARTS, "final_roc_curve.png", "Fluency: ROC curve")
    show_chart(FLUENCY_CHARTS, "final_precision_recall_curve.png", "Fluency: precision–recall curve")

    st.warning(
        "The 226-subject fluency experiment uses Pitt for AD cases and WLS for controls. "
        "Because diagnosis and dataset source are linked, the reported nested cross-validation "
        "metrics may reflect source differences as well as language differences."
    )

with limits_tab:
    st.header("Limitations and interpretation")
    limitations = [
        ("No clinical validation", "No independent clinical validation has been completed. Scores are not diagnostic probabilities or clinical screening results."),
        ("Cookie Theft artifact mismatch", "The stored transcript–acoustic fusion evaluation is not the same as the four-component transcript-only inference path loaded by the current app."),
        ("Post-hoc test filtering", "The Cookie Theft fusion report states that the test subset was filtered after prior model-error inspection."),
        ("Dataset-source confounding", "The fluency experiment uses Pitt AD cases and WLS controls, so diagnosis and source dataset are confounded."),
        ("Transcription error", "Whisper errors, accents, background noise, recording quality, and language variation can affect transcript-derived features."),
        ("Fluency parser", "The current feature extractor counts alphabetic tokens and does not verify animal-category membership."),
        ("Generalizability", "Age, education, language background, hearing, speech differences, and collection conditions may influence outputs."),
    ]
    for title, detail in limitations:
        with st.expander(title):
            st.write(detail)

    st.error(
        "Do not use NeuroVoice to diagnose, rule out, screen for, or make treatment decisions "
        "about any medical condition. A score above a model threshold is only a model-specific "
        "research output."
    )
