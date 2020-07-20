#!/usr/bin/env python3

from collections import defaultdict, Counter
import os.path
import sys


DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")) + "/"
MISSING = defaultdict(lambda: defaultdict(lambda: set()))


class Sample:
    def __init__(self, line):
        # Heuristically determine format
        split_line = line.split("\t")
        if len(split_line) < 8:
            # Abbreviated format.
            (lang_id, lang_name, family, *feature_pieces,) = split_line
            latitude = "nan"
            longitude = "nan"
            genus = None
            country_codes = ""
        else:
            # Full format.
            # Note that even if for some reason the abbreviated makes it here,
            # it will fail in the float-comparison :)
            (
                lang_id,
                lang_name,
                latitude,
                longitude,
                genus,
                family,
                country_codes,
                *feature_pieces,
            ) = split_line

        self.lang = {
            "id": lang_id,
            "name": lang_name,
            "latitude": float(latitude),
            "longitude": float(longitude),
            "genus": genus,
            "family": family,
            "countries": tuple(country_codes.split(" ")),
            "controlled_genus": genus if genus in FileTriple.controlled_genera else FileTriple.controlled_genera[-1],
        }
        self.features = {
            k.lower(): v.split()[0]
            for k, v in [
                kv.split("=")
                for kv in (
                    "|".join(feature_pieces)
                    .replace(
                        "double negationPosition_of_negative",
                        "double negation|Position_of_negative",
                    )
                    .replace(
                        "double negationSVONeg_Order",
                        "double negation|SVONeg_Order",
                    )
                    .replace(
                        "double negationSNegVO_Order",
                        "double negation|SNegVO_Order",
                    )
                    .replace(
                        "double negationPreverbal_Negative",
                        "double negation|Preverbal_Negative",
                    )
                    .replace(
                        "1 Separate word, no double negation|Word&NoDoubleNeg",
                        "1 Separate word, no double negation",
                    )
                    .replace(
                        "2 Prefix, no double negation|Prefix&NoDoubleNeg",
                        "2 Prefix, no double negation",
                    )
                    .replace(" (= ", " (EQUALS ")
                ).split("|")
            ]
        }
        assert all([v == "?" or v == str(int(v)) for v in self.features.values()])


class TestFile:
    def __init__(self, filename):
        self.filename = filename
        self.id2sample = {}
        self.lang_values = defaultdict(Counter)
        self.available_feature_values = defaultdict(Counter)
        self.genus2family = {}

        with open(filename) as f:
            for l in f.read().splitlines():
                if l.startswith("wals_code") or not l.strip():
                    continue
                # Construct Sample and add to dict
                s = Sample(l)
                assert s.lang["id"] not in self.id2sample
                self.id2sample[s.lang["id"]] = s
                # These will be used for grouping later
                for k, v in s.lang.items():
                    self.lang_values[k][v] += 1
                for k, v in s.features.items():
                    self.available_feature_values[k][v] += 1
                # Mostly used this for testing and validating, not used rn.
                if s.lang["genus"] is not None:
                    if s.lang["genus"] not in self.genus2family:
                        self.genus2family[s.lang["genus"]] = s.lang["family"]
                    else:
                        assert self.genus2family[s.lang["genus"]] == s.lang["family"]
            self.lang_values = dict(self.lang_values)
            self.available_feature_values = dict(self.available_feature_values)


def average(scorepairs, mode):
    if mode == "micro":
        numerator = sum([n for n, _ in scorepairs])
        denominator = sum([d for _, d in scorepairs])
        return (numerator / denominator) if denominator > 0 else float("nan")
    elif mode == "macro":
        return sum([n / (d if d > 0 else float("nan")) for n, d in scorepairs]) / len(scorepairs)
    elif mode == "single":
        [(numerator, denominator)] = scorepairs
        return (numerator / denominator) if denominator > 0 else float("nan")
    else:
        raise ValueError(f"Illegal averaging mode {mode}")


class FileTriple:
    controlled_genera = sorted(["Mayan", "Tucanoan", "Madang", "Mahakiranti", "Northern Pama-Nyungan", "Nilotic", "other genera"])

    def __init__(self, participant_filename):
        self.name = os.path.basename(participant_filename).replace('.tsv', '')
        self.gold = TestFile(DATA_PATH + "test_gold.csv")
        self.mask = TestFile(DATA_PATH + "test_blinded.csv")
        self.pred = TestFile(participant_filename)
        for s in self.mask.id2sample.values():
            for k in [k for k, v in s.features.items() if v != "?"]:
                del s.features[k]

    def score_sample(self, s):
        i = s.lang["id"]
        feats_gold = self.gold.id2sample[i].features
        feats_mask = self.mask.id2sample[i].features
        if i in self.pred.id2sample:
            feats_pred = self.pred.id2sample[i].features
        else:
            for k, v in feats_mask.items():
                if v.strip == "?":
                    MISSING[self.name][i].add(k)
            feats_pred = feats_mask
        numerator, denominator = 0, 0
        for k, m in feats_mask.items():
            if m.strip() == "?":
                # move this inside the next if to get "ignore" behavior
                denominator += 1
                assert feats_gold[k] != "?"
                if k in feats_pred:
                    if feats_gold[k] == feats_pred[k]:
                        numerator += 1
                else:
                    MISSING[self.name][i].add(k)
        return numerator, denominator

    def accuracy_per_field(self, name_container, get_field, field_name, mode):
        return sorted(
            [
                (
                    name,
                    average(
                        [
                            self.score_sample(s)
                            for s in self.gold.id2sample.values()
                            if field_name in get_field(s)
                            and get_field(s)[field_name] == name
                        ],
                        mode,
                    ),
                )
                for name in name_container[field_name]
            ]
        )

    def accuracy_per_lang_field(self, field_name, mode):
        return self.accuracy_per_field(
            self.gold.lang_values, lambda s: s.lang, field_name, mode
        )

    def accuracy_per_feature_field(self, field_name, mode):
        return self.accuracy_per_field(
            self.gold.available_feature_values, lambda s: s.features, field_name, mode
        )

    def print_accuracies(self):
        print("Accuracies per language:")
        for name, acc in self.accuracy_per_lang_field("id", "single"):
            print(f"{name}\t{acc:.4f}")

        for field in ("family", "genus"):
            for mode in ("micro", "macro"):
                print(f"\nAccuracies per language {field} ({mode}):")
                for (name, acc) in self.accuracy_per_lang_field(field, mode):
                    print(f"{name}\t{acc:.4f}")

        for field in sorted(list(self.gold.available_feature_values.keys())):
            for mode in ("micro", "macro"):
                print(f"\nAccuracies per language {field} ({mode}):")
                for (name, acc) in self.accuracy_per_feature_field(field, mode):
                    print(f"{name}\t{acc:.4f}")


filetriples = [FileTriple(filename) for filename in sys.argv[1:]]
ex = filetriples[0]

for mode in ("micro",):  #, "macro"):
    print("\n# Averaging:", mode, "\n")
    print("submission", *ex.controlled_genera, sep="\t")
    print("number of languages", *[len([s for s in ex.mask.id2sample.values() if s.lang["controlled_genus"] == g]) for g in ex.controlled_genera], sep="\t")
    for triple in filetriples:
        print(triple.name, *[
            acc for _, acc in triple.accuracy_per_lang_field("controlled_genus", mode)
        ], sep="\t")
    print("\noverall:")
    for triple in filetriples:
        print(
            triple.name,
            average(
                [
                    triple.score_sample(s)
                    for s in triple.gold.id2sample.values()
                ],
                mode,
            ),
            sep="\t"
        )


print("\n# Errors\n")
for triple in filetriples:
    missing_features = 0
    if MISSING[triple.name]:
        broken_langs = [(lang, len(MISSING[triple.name][lang])) for lang in MISSING[triple.name]]
        print(f"{triple.name} missing {sum([c for _, c in broken_langs])}/2417 features in {len(broken_langs)}/149 languages!")
