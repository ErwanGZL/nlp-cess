from collections import defaultdict

from fastcoref import FCoref
from flair.data import Sentence
from flair.models import SequenceTagger

from cluster import Cluster
from named_entity import NamedEntity

coref = FCoref(device="cpu")
tagger_ner = SequenceTagger.load("flair/ner-english-large")


def coreference(text: str) -> list[list[tuple[str, tuple[int, int]]]]:
    predictions = coref.predict(texts=[text])
    k = predictions[0].get_clusters()
    p = predictions[0].get_clusters(as_strings=False)
    return [list(zip(kk, pp)) for kk, pp in zip(k, p)]


def ner(text: str):
    sentence = Sentence(text)
    tagger_ner.predict(sentence)

    data = []
    for entity in sentence.get_spans("ner"):
        if entity.tag != "PER":
            continue

        data.append(
            (
                entity.text,
                {
                    "text": entity.text,
                    "start_pos": entity.start_position,
                    "end_pos": entity.end_position,
                    "tag": entity.tag,
                },
            )
        )

    # Pruning

    grouped = defaultdict(list)
    counts = defaultdict(int)

    for k, v in data:
        grouped[k] += [v]
        counts[k] += 1

    entities = []
    for k, v in grouped.items():
        if counts[k] >= 2:  # NOTE: THRESHOLD
            entities += v
    return entities


def association(entities: list[dict], clusters: list[Cluster]) -> list[NamedEntity]:
    results = defaultdict(list)
    for e in entities:
        score = 0
        best = None
        for i, c in enumerate(clusters):
            if not c.is_interesting():
                continue

            s = c.similarity(e["text"], (e["start_pos"], e["end_pos"]))
            if s > score:
                score = s
                best = i

        if best >= 0:
            if score > 0.5:  # NOTE: THRESHOLD
                results[best].append((e, score))
            else:
                results[None].append((e, score))

    named_entities = []
    for k, v in results.items():
        if k is not None:
            ne = NamedEntity([(e, s) for e, s in v], clusters[k])
            named_entities.append(ne)

    # Merge all entities with the same identifier and gender in named_entities as a new NamedEntity

    final_entities = []
    merged_entities = defaultdict(list)

    for ne in named_entities:
        merged_entities[(ne.identifier, ne.gender)].append(ne)

    for _, nes in merged_entities.items():
        if len(nes) > 1:
            merged = NamedEntity(
                [(e, s) for ne in nes for e, s in ne.src_e], nes[0].src_c
            )
            final_entities.append(merged)
        else:
            final_entities.append(nes[0])

    return final_entities


def extract_identities(src: str) -> list[NamedEntity]:
    entities = ner(src)
    clusters = [Cluster(c) for c in coreference(src)]
    identities = association(entities, clusters)
    return identities
