# NeuroVoice architecture

## Deployed Streamlit application

```mermaid
flowchart TD
    A[Audio input widget] --> B[Audio bytes in active session]
    B --> C[Temporary WAV conversion with FFmpeg]
    C --> D[Whisper transcription on server]
    D --> E{Assessment task}
    E --> F[Cookie Theft transcript]
    E --> G[Animal-category transcript]
    F --> H[Word TF-IDF SVM]
    F --> I[Character TF-IDF SVM]
    F --> J[Linguistic-feature logistic regression]
    F --> K[Combined text logistic regression]
    H --> L[Weighted transcript ensemble]
    I --> L
    J --> L
    K --> L
    G --> M[Four lexical/count features]
    M --> N[Saved fluency classifier]
    L --> O[Cookie Theft task result]
    N --> P[Fluency task result]
    O --> Q[Separate task results and PDF]
    P --> Q
    R[Optional memory activity] --> S[Separate descriptive result]
```

## Important implementation distinction

The deployed Cookie Theft inference code in `src/cookie_model.py` loads four transcript models. It does not load an acoustic model. The transcript–acoustic stacking metrics under `assets/data/picture/` describe a separate experiment and must not be presented as metrics for the current web-app inference path.

The optional memory activity is a separate exercise. It must not be combined with the two speech-model outputs into a weighted disease or screening score.

## Data flow and retention

- The audio-input widget supplies audio to the Streamlit server.
- `src/transcription.py` writes temporary source/normalized audio files inside a temporary directory.
- FFmpeg converts audio to mono 16-kHz WAV with filtering.
- Whisper runs as a local model process on the server.
- The temporary directory is removed when transcription returns or raises an error.
- The app should not create a second persistent copy of uploaded audio in session state.
- Streamlit's audio-input widget can retain the uploaded file during the active session; session reset or expiration should clear it.
