import math
import unittest

from src.fluency_model_v2 import AnimalFluencyModel
from src.linguistic_features import LinguisticFeatures


class AnimalFluencyFeatureTests(unittest.TestCase):
    def test_counts_tokens_and_repetitions(self):
        result = AnimalFluencyModel.extract_features("Cat, dog, cat! HORSE.")

        self.assertEqual(result["clean_total_items"], 4)
        self.assertEqual(result["clean_unique_items"], 3)
        self.assertEqual(result["clean_repetition_count"], 1)
        self.assertAlmostEqual(result["clean_type_token_ratio"], 0.75)

    def test_empty_text_returns_zero_features(self):
        result = AnimalFluencyModel.extract_features("   ... ")

        self.assertEqual(result["clean_total_items"], 0)
        self.assertEqual(result["clean_unique_items"], 0)
        self.assertEqual(result["clean_repetition_count"], 0)
        self.assertEqual(result["clean_type_token_ratio"], 0.0)

    def test_apostrophes_and_case_are_normalized(self):
        result = AnimalFluencyModel.extract_features("Dog's DOG'S")

        self.assertEqual(result["clean_total_items"], 2)
        self.assertEqual(result["clean_unique_items"], 1)
        self.assertEqual(result["clean_repetition_count"], 1)
        self.assertEqual(result["clean_type_token_ratio"], 0.5)


class LinguisticFeatureTests(unittest.TestCase):
    def test_transform_returns_finite_26_feature_vector(self):
        matrix = LinguisticFeatures().transform(
            ["The boy is reaching for cookies while water spills."]
        )

        self.assertEqual(matrix.shape, (1, 26))
        self.assertTrue(all(math.isfinite(float(value)) for value in matrix[0]))

    def test_empty_transcript_is_handled(self):
        matrix = LinguisticFeatures().transform([""])

        self.assertEqual(matrix.shape, (1, 26))
        self.assertTrue(all(math.isfinite(float(value)) for value in matrix[0]))


if __name__ == "__main__":
    unittest.main()
