import re

import ollama

from named_entity import NamedEntity


def ollama_gen(prompt: str, model="mistral"):
    ollama.pull(model)

    response = ollama.generate(
        model=model,
        prompt=prompt,
    )
    return response


def create_prompt(identifier: str, gender: str, text: str) -> str:
    return (
        f"Extract one action or thought or description about the {gender} character {identifier} that is the most relevant to the extract.\n"
        f"format your answer as a short sentence or a few words concentrating the most of the information.\n"
        f"If there is no relevant information return an empty string.\n\n"
        f"{text}"
    )


def summarize_character(id: NamedEntity, src: str, bucket_size=1500) -> list[str]:
    summaries: list[str] = []
    mentions, offset = id.mentions(bucket_size)

    print(f"Processing: {id.identifier}, {id.gender}...")
    for k, v in mentions.items():
        start = k * bucket_size + offset
        end = start + bucket_size
        text = src[start:end]

        # Replace all mentions in the text with an extremely unlikely character
        for span, (s, e) in v:
            r = "\u2063" * (e - s)
            s += -start
            e += -start
            text = text[:s] + r + text[e:]

        text = re.sub(r"\u2063+", id.identifier, text)
        prompt = create_prompt(id.identifier, id.gender, text)
        summaries.append(ollama_gen(prompt)["response"])

    return summaries
