from pathlib import Path
import ast

import joblib
import numpy as np
import pandas as pd

import __main__

from src.linguistic_features import LinguisticFeatures

# The original models were saved while LinguisticFeatures
# existed in the training notebook's __main__ module.
__main__.LinguisticFeatures = LinguisticFeatures


MODEL_DIR = Path(__file__).resolve().parents[1] / "models" / "cookie"

MODEL_NAMES = [
    "word_tfidf_svm",
    "char_tfidf_svm",
    "linguistic_logreg",
    "word_char_linguistic_logreg",
]


class CookieTheftEnsemble:
    def __init__(self):
        self.models = {
            name: joblib.load(MODEL_DIR / f"{name}.joblib")
            for name in MODEL_NAMES
        }

        config_path = (
            MODEL_DIR / "validation_selected_configuration.csv"
        )
        config = pd.read_csv(config_path)

        self.threshold = float(config.loc[0, "threshold"])

        self.weights = np.array(
            ast.literal_eval(config.loc[0, "weights"]),
            dtype=float,
        )

        self.columns = ast.literal_eval(
            config.loc[0, "columns"]
        )

        if self.columns != MODEL_NAMES:
            raise ValueError(
                "Model order in the configuration CSV does not match "
                "the website model order."
            )

        self.weights = self.weights / self.weights.sum()

    @staticmethod
    def get_positive_probability(model, transcript):
        probabilities = model.predict_proba([transcript])

        if probabilities.shape[1] != 2:
            raise ValueError(
                "Expected a binary classification model."
            )

        classes = list(model.classes_)

        if 1 not in classes:
            raise ValueError(
                f"Positive class 1 not found. Classes: {classes}"
            )

        positive_index = classes.index(1)
        return float(probabilities[0, positive_index])

    def predict(self, transcript):
        transcript = str(transcript).strip()

        if not transcript:
            raise ValueError("Transcript cannot be empty.")

        individual_scores = {}

        for name in MODEL_NAMES:
            individual_scores[name] = (
                self.get_positive_probability(
                    self.models[name],
                    transcript,
                )
            )

        ordered_scores = np.array(
            [
                individual_scores[name]
                for name in MODEL_NAMES
            ],
            dtype=float,
        )

        ensemble_score = float(
            np.dot(ordered_scores, self.weights)
        )

        return {
            "score": ensemble_score,
            "threshold": self.threshold,
            "flagged": ensemble_score >= self.threshold,
            "individual_scores": individual_scores,
        }
