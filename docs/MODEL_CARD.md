# NeuroVoice Model Card

## Model overview

NeuroVoice is an experimental, student-built research application for exploring speech and language patterns in the Cookie Theft Picture Description and Semantic Verbal Fluency tasks. It is not a medical device or clinically validated screening system.

## Intended use

- Educational demonstration of speech transcription and task-specific machine-learning workflows.
- Exploratory research into linguistic features in selected speech datasets.
- Reproducibility and discussion of methodological limitations.

## Out-of-scope uses

Do not use NeuroVoice to diagnose Alzheimer's disease or another condition, estimate an individual's disease probability, determine impairment severity, make treatment decisions, or replace professional assessment.

## Inputs and processing

The application accepts audio for supported tasks and transcribes it on the application server using an English Whisper model. Task-specific processing then analyzes the transcript.

### Cookie Theft Picture Description

The checked-in application inference code in `src/cookie_model.py` loads a four-component transcript-only ensemble:

- Word TF-IDF + linear SVM
- Character TF-IDF + linear SVM
- Linguistic-feature logistic regression
- Combined word/character/linguistic logistic regression

The ensemble weights are read from `models/cookie/validation_selected_configuration.csv` (0.45, 0.15, 0.05, and 0.35 in the current configuration); the saved decision threshold is 0.61. Audio is used for transcription; the current application inference path does not load an acoustic classifier.

### Semantic Verbal Fluency

The application extracts four transcript features: total alphabetic tokens, unique tokens, repeated tokens, and type-token ratio. The saved classifier uses a threshold of 0.52. The feature extractor does not verify that each recognized word is a valid member of the requested semantic category (animals).

## Research datasets and evaluation

The broader research workflow has involved ADReSS 2020, ADReSSo 2021, ADReSS-M, Pitt Corpus, Lu Corpus, and other TalkBank releases. Dataset use differs by experiment; inclusion in this list does not mean every dataset trained every deployed model.

The repository contains separate research evaluation artifacts:

- The Cookie Theft transcript–acoustic fusion report describes 2,080 training recordings and 371 reviewed test recordings, after 33 of 404 recordings were removed during quality review. The report states that the test subset was filtered after prior model-error inspection and that the acoustic extraction source was unavailable and the fusion pipeline reconstructed. Its reported metrics are post-hoc diagnostic results, not an untouched-test estimate and not performance of the deployed transcript-only ensemble.
- The Semantic Verbal Fluency experiment reports nested cross-validation on 226 participants: 113 Pitt Corpus AD participants and 113 Wisconsin Longitudinal Study controls. The reported accuracy and balanced accuracy are 89.82%, ROC-AUC 96.19%, and average precision 96.72%. Diagnosis group is confounded with dataset source (Pitt for AD; WLS for controls), so the model may learn study, recruitment, demographic, recording, or transcription differences as well as cognitive-language patterns.

These are internal research results, not independent external validation or clinical performance estimates.

## Known limitations and risks

- No independent external clinical validation has been completed.
- Whisper transcription errors can affect all downstream features.
- Semantic verbal fluency features do not validate animal semantics.
- Dataset-source confounding limits interpretation of the fluency experiment.
- The fusion evaluation is post-hoc and does not match the deployed Cookie Theft inference path.
- Age, education, language background, hearing, speech differences, recording conditions, and other factors may affect speech and model outputs.
- Dataset sizes and composition may limit generalizability.
- A model output must not be interpreted as a diagnosis, disease probability, or impairment-severity measurement.

## Data and privacy

Audio is processed on the application server. The transcription function uses temporary files and removes them when processing finishes. The active Streamlit audio-input widget may retain its recording for the session, and hosting infrastructure may process technical logs under its own policies. Do not upload identifying or private health information.

Raw participant recordings and restricted dataset contents should not be committed to this repository. Follow each dataset's access agreement, citation requirements, and redistribution restrictions.

## Recommended next steps

1. Reconcile every deployed model artifact with reproducible training and inference code.
2. Use participant-level splits and document them for each experiment.
3. Evaluate on matched, independent external datasets.
4. Investigate dataset-source and demographic confounding.
5. Validate semantic category membership in the fluency task.
6. Report calibration, uncertainty, subgroup performance, and failure cases.
7. Obtain appropriate ethics and clinical oversight before any prospective clinical research.

## Technical implementation

See [the repository README](../README.md) for installation, current application architecture, evaluation-artifact descriptions, and repository layout.
