from pathlib import Path
import re

import joblib
import numpy as np


MODEL_PATH = (
    Path(__file__).resolve().parents[1]
    / "models"
    / "fluency"
    / "category_fluency_final_model.joblib"
)


class AnimalFluencyModel:
    def __init__(self):
        package = joblib.load(MODEL_PATH)

        self.model = package["model"]
        self.feature_columns = package["feature_columns"]
        self.threshold = float(package["threshold"])
        self.limitation = package.get("important_limitation", "")

    @staticmethod
    def extract_features(response: str) -> dict:
        words = re.findall(r"[a-zA-Z']+", response.lower())

        total_items = len(words)
        unique_items = len(set(words))
        repetition_count = total_items - unique_items

        type_token_ratio = (
            unique_items / total_items
            if total_items > 0
            else 0.0
        )

        return {
            "clean_total_items": total_items,
            "clean_unique_items": unique_items,
            "clean_repetition_count": repetition_count,
            "clean_type_token_ratio": type_token_ratio,
        }

    def predict(self, response: str) -> dict:
        response = response.strip()

        if not response:
            raise ValueError("Response cannot be empty.")

        feature_values = self.extract_features(response)

        features = np.array(
            [[
                feature_values[column]
                for column in self.feature_columns
            ]],
            dtype=float,
        )

        probabilities = self.model.predict_proba(features)
        classes = list(self.model.classes_)

        positive_index = classes.index(1)
        score = float(probabilities[0, positive_index])

        return {
            "score": score,
            "threshold": self.threshold,
            "flagged": score >= self.threshold,
            "features": feature_values,
            "limitation": self.limitation,
        }
