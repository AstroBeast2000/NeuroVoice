import re
from collections import Counter

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin


class LinguisticFeatures(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.fillers = {
            "um", "uh", "erm", "hmm", "mm", "mhm", "uhh", "umm"
        }

        self.vague_words = {
            "thing", "things", "something", "anything", "stuff", "whatever",
            "maybe", "perhaps", "probably", "guess", "think", "looks", "like",
            "some", "someone", "somebody", "somewhere"
        }

        self.pronouns = {
            "he", "she", "they", "it", "him", "her", "them", "his", "hers",
            "their", "this", "that", "these", "those"
        }

        self.cookie_units = {
            "cookie", "cookies", "jar", "boy", "girl", "mother", "mom", "woman",
            "sink", "water", "overflowing", "faucet", "stool", "chair", "fall",
            "falling", "dishes", "plate", "cups", "window", "curtains", "kitchen",
            "counter", "cabinet", "cupboard", "apron", "floor"
        }

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        feats = []

        for text in X:
            text = str(text).lower()

            words = re.findall(r"[a-z']+", text)

            sentences = re.split(r"[.!?]+", text)
            sentences = [
                sentence.strip()
                for sentence in sentences
                if sentence.strip()
            ]

            n_words = len(words)
            n_unique = len(set(words))
            n_sentences = len(sentences)
            chars = len(text)

            counts = Counter(words)

            filler_count = sum(
                counts[word]
                for word in self.fillers
            )

            vague_count = sum(
                counts[word]
                for word in self.vague_words
            )

            pronoun_count = sum(
                counts[word]
                for word in self.pronouns
            )

            cookie_unit_count = sum(
                counts[word]
                for word in self.cookie_units
            )

            repeated_word_count = sum(
                count - 1
                for count in counts.values()
                if count > 1
            )

            max_word_repeat = (
                max(counts.values())
                if counts
                else 0
            )

            avg_word_len = (
                np.mean([len(word) for word in words])
                if words
                else 0
            )

            avg_sent_len = (
                n_words / max(n_sentences, 1)
            )

            type_token_ratio = (
                n_unique / max(n_words, 1)
            )

            repetition_ratio = (
                repeated_word_count / max(n_words, 1)
            )

            filler_ratio = (
                filler_count / max(n_words, 1)
            )

            vague_ratio = (
                vague_count / max(n_words, 1)
            )

            pronoun_ratio = (
                pronoun_count / max(n_words, 1)
            )

            cookie_unit_ratio = (
                cookie_unit_count / max(n_words, 1)
            )

            long_word_count = sum(
                len(word) >= 7
                for word in words
            )

            long_word_ratio = (
                long_word_count / max(n_words, 1)
            )

            adjacent_repeats = sum(
                words[index] == words[index - 1]
                for index in range(1, len(words))
            )

            adjacent_repeat_ratio = (
                adjacent_repeats / max(n_words - 1, 1)
            )

            question_marks = text.count("?")

            first_person_count = sum(
                counts[word]
                for word in {
                    "i", "me", "my", "mine",
                    "we", "us", "our", "ours"
                }
            )

            first_person_ratio = (
                first_person_count / max(n_words, 1)
            )

            feats.append([
                n_words,
                np.log1p(n_words),
                n_unique,
                np.log1p(n_unique),
                n_sentences,
                chars,
                avg_word_len,
                avg_sent_len,
                type_token_ratio,
                repetition_ratio,
                max_word_repeat,
                filler_count,
                filler_ratio,
                vague_count,
                vague_ratio,
                pronoun_count,
                pronoun_ratio,
                cookie_unit_count,
                cookie_unit_ratio,
                long_word_count,
                long_word_ratio,
                adjacent_repeats,
                adjacent_repeat_ratio,
                question_marks,
                first_person_count,
                first_person_ratio,
            ])

        return np.asarray(feats, dtype=float)
