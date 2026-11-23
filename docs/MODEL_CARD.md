# NeuroVoice model card

**Status:** Research prototype  
**Owner:** NeuroVoice project  
**Last reviewed:** 2026-11-23

## Summary

NeuroVoice is an educational and research application that analyzes transcripts from two language tasks: Cookie Theft picture description and animal-category verbal fluency. The application is not a medical device and is not intended for diagnosis, screening, triage, prognosis, or treatment decisions.

## Intended use

- Demonstrating a speech-to-text and language-feature research workflow.
- Exploring how task-specific language representations behave on research datasets.
- Supporting reproducibility discussions and future research development.

## Out-of-scope use

- Diagnosing or ruling out Alzheimer's disease, mild cognitive impairment, Parkinson's disease, dementia, or any other condition.
- Estimating an individual's disease probability, severity, or future decline.
- Making clinical, educational eligibility, employment, insurance, or other consequential decisions.

## Application implementation

### Cookie Theft Picture Description

The current checked-in Streamlit application loads four transcript-based components from `models/cookie/` through `src/cookie_model.py`:

1. Word TF-IDF + linear SVM
2. Character TF-IDF + linear SVM
3. Linguistic-feature logistic regression
4. Combined word/character/linguistic logistic regression

The ensemble weights and threshold are read from `validation_selected_configuration.csv`. The current inference path transcribes audio and classifies the transcript; it does not load the acoustic Extra Trees model described by a separate evaluation artifact.

### Semantic Verbal Fluency

The current feature extractor in `src/fluency_model_v2.py` computes total alphabetic tokens, unique tokens, repeated tokens, and type-token ratio. It does not verify that each token is an animal name. The saved model applies its stored preprocessing and classifier to those four features.

## Evaluation artifacts and interpretation

### Cookie Theft fusion artifact

`assets/data/picture/FINAL_evaluation_report.txt` reports a transcript–acoustic stacking experiment with 2,080 training recordings and 371 reviewed test recordings:

| Metric | Reported value |
|---|---:|
| Accuracy | 91.11% |
| Balanced accuracy | 89.81% |
| F1 | 88.26% |
| ROC-AUC | 91.41% |
| Average precision | 92.93% |
| Sensitivity | 83.22% |
| Specificity | 96.40% |

**Critical qualification:** the report says the test set was filtered after prior model-error inspection (33 of 404 recordings were removed during quality review). It is therefore a post-hoc diagnostic subset, not an untouched independent test set. The report also notes that the acoustic extraction source was unavailable and the fusion pipeline was reconstructed. These metrics do not describe the currently checked-in four-component transcript-only application inference path and must not be represented as deployed application performance.

### Semantic verbal fluency artifacts

The saved nested cross-validation artifacts contain 226 participant-level records, with 113 Pitt AD participants and 113 WLS controls. The reported results are:

| Metric | Estimate |
|---|---:|
| Accuracy | 89.82% |
| Balanced accuracy | 89.82% |
| Precision | 91.67% |
| Recall | 87.61% |
| F1 | 89.59% |
| ROC-AUC | 96.19% |
| Average precision | 96.72% |

The saved bootstrap file reports a 95% ROC-AUC interval of approximately 93.68%–98.21% and a balanced-accuracy interval of approximately 85.82%–93.75%.

**Critical qualification:** the AD group is sourced from Pitt and the control group from WLS. Diagnosis and dataset source are therefore confounded. Nested cross-validation does not remove this source confounding or establish generalization to matched populations.

## Data and preprocessing

The broader project has worked with ADReSS 2020, ADReSSo 2021, ADReSS-M, Pitt, Lu, and other TalkBank material. Which sources are used depends on the specific experiment. Do not assume every source trained every model.

Participant-only audio is preferred where available to reduce interviewer leakage. Speaker diarization, segmentation, normalization, transcription, and metadata alignment have been used in the broader preprocessing workflow. Participant-level train/test separation is essential when there are repeated recordings per person.

Raw or restricted recordings must not be added to this repository unless the dataset license and consent terms explicitly permit redistribution.

## Known limitations and risks

- No independent external clinical validation.
- Post-hoc filtering in the Cookie Theft fusion test subset.
- A mismatch between the Cookie Theft fusion evaluation artifact and the current app inference implementation.
- Pitt-versus-WLS source confounding in the fluency experiment.
- Small and non-representative research samples.
- Potential age, education, language, demographic, recording, and transcription confounding.
- ASR errors can change downstream language features.
- The fluency tokenizer counts alphabetic words and does not verify animal-category membership.
- Thresholds are development choices, not clinical cutoffs.
- Model probabilities are not calibrated disease probabilities.

## Privacy

The application processes audio on the server. Temporary transcription files are cleaned up when the transcription function exits. The Streamlit audio-input widget may retain uploaded audio for the duration of the active session. Do not submit identifiable or sensitive health information. Hosting infrastructure may process technical logs under its own policies.

## Required work before stronger claims

1. Align the deployed Cookie Theft inference code with the exact model and artifacts used for reported evaluation, or clearly maintain them as separate experiments.
2. Publish reproducible training/evaluation scripts, exact dataset manifests, subject-level split definitions, and preprocessing versions.
3. Re-evaluate on an untouched, independently held-out participant set.
4. Address dataset-source confounding with matched cohorts and external datasets.
5. Validate the fluency response parser against the task's animal-category requirements without changing feature definitions silently.
6. Report confidence intervals, calibration, subgroup performance, and failure cases.
7. Obtain appropriate expert, ethics, and clinical oversight before any clinical research or use.

## Change log

- 2026-11-23: Clarified the deployed inference path, separated research artifacts from application metrics, documented dataset-source confounding and post-hoc test filtering, and clarified audio-session handling.
