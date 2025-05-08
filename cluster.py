from collections import defaultdict

from fuzzywuzzy import fuzz

from pronouns import pronouns


class Cluster:
    def __init__(self, src: list[tuple[str, tuple[int, int]]]):
        self.src = src
        self.gender = None
        self.pronouns = defaultdict(lambda: defaultdict(int))
        self.entities = defaultdict(int)

        # Evaluate cluster gender
        for n, (s, e) in src:
            n = n.lower()
            if n in pronouns["feminine"]:
                self.pronouns["feminine"][n] += 1
            elif n in pronouns["masculine"]:
                self.pronouns["masculine"][n] += 1
            elif n in pronouns["neuter"]:
                self.pronouns["neuter"][n] += 1
            elif n not in pronouns["other"]:
                self.entities[n] += 1
        self.gender = max(
            self.pronouns, key=lambda g: sum(self.pronouns[g].values()), default=None
        )

    def is_interesting(self, threshold=2, gendered=True):
        if gendered and self.gender is None:
            return False
        if sum(self.entities.values()) < threshold:
            return False
        return True

    def similarity(self, entity: str, pos: tuple[int, int]) -> float:
        entity_lower = entity.lower()

        # --- 1. Check for EXACT POSITIONAL MATCH (100% confidence) ---
        for cluster_entity, cluster_pos in self.src:
            if pos == cluster_pos:
                return 1.0  # Same mention → must be the same entity

        # --- 2. If no positional match, use FUZZY STRING + PROXIMITY ---
        max_similarity = 0.0
        best_proximity_score = 0.0

        for cluster_entity, cluster_pos in self.src:
            # (A) Fuzzy string similarity (0-100 scale → normalized to 0-1)
            str_sim = fuzz.ratio(entity_lower, cluster_entity.lower()) / 100.0

            # (B) Position proximity score (inverse distance)
            distance = self.calculate_distance(pos, cluster_pos)
            proximity_score = 1.0 / (1.0 + distance)

            # Combined score (weighted sum)
            combined_score = 0.6 * str_sim + 0.4 * proximity_score

            if combined_score > max_similarity:
                max_similarity = combined_score

        return max_similarity

    @staticmethod
    def calculate_distance(pos1: tuple[int, int], pos2: tuple[int, int]) -> int:
        """Calculate the distance between two spans. Returns 0 if overlapping."""
        start1, end1 = pos1
        start2, end2 = pos2
        if end1 <= start2:
            return start2 - end1
        elif end2 <= start1:
            return start1 - end2
        else:
            return 0  # Overlapping or adjacent

    def __repr__(self):
        return f"{self.is_interesting()} {self.gender} {dict(self.entities)}"
