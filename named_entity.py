from collections import defaultdict

from cluster import Cluster


class NamedEntity:
    def __init__(self, entities: list[tuple[any, float]], cluster: Cluster):
        self.src_e = entities
        self.src_c = cluster
        self.gender = cluster.gender

        self._ent_weight = defaultdict(int)
        for entity, _ in entities:
            self._ent_weight[entity["text"]] += 1

        self.identifier = max(self._ent_weight, key=lambda k: self._ent_weight[k])

        self.aliases = {
            entity["text"]: self._ent_weight[entity["text"]]
            / (len(entities) - self._ent_weight[self.identifier])
            for entity, _ in entities
            if entity["text"].lower() != self.identifier.lower()
        }

    def get_aliases(self, r=0.3):
        items = self._ent_weight.copy()
        # Remove the main identifier from the items
        items.pop(self.identifier, None)
        # Calculate proportions
        total = sum(items.values())
        proportions = {k: v / total for k, v in items.items()}
        sorted_items = sorted(
            proportions.items(), key=lambda x: x[1]
        )  # ascending order by proportion

        # Find the cutoff index where 30% of cumulative proportion is reached
        cumulative = 0
        to_remove = []
        for k, prop in sorted_items:
            if cumulative + prop <= r:
                cumulative += prop
                to_remove.append(k)
            else:
                break

        # Prune the items
        pruned_items = {k: v for k, v in items.items() if k not in to_remove}
        return pruned_items

    def mentions(self, bucket_size=1000) -> tuple[dict[int, list], int]:
        mentions = self.src_c.src
        if not mentions:
            return {}, 0

        # Find the minimum start position (first mention's position)
        first_start = min(start for _, (start, _) in mentions)

        buckets = defaultdict(list)
        for span, (start, end) in mentions:
            # Shift start to be relative to first_start
            adjusted_start = start - first_start
            bucket = adjusted_start // bucket_size
            buckets[bucket] += [(span, (start, end))]

        return buckets, first_start

    def __repr__(self):
        return f"NamedEntity({self.identifier} ({self.gender}): {self.get_aliases()})"
