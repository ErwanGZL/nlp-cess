import re

import nltk
from unidecode import unidecode

nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)


def preprocess(src: str) -> str:
    paragraphs = unidecode(src).split("\n\n")
    content = ""

    for p in paragraphs:
        sentences = nltk.sent_tokenize(p, language="english")
        for s in sentences:
            s = re.sub("\n", " ", s)
            content += s + "\n"
        content += "\n"

    return content
