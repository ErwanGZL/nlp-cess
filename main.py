import sys
from ast import alias
from pathlib import Path

from numpy import sort

from identity import extract_identities
from named_entity import NamedEntity
from preprocessing import preprocess
from summarization import summarize_character

output_path = Path(__file__).parent.resolve() / "out"


def load_data(file_path) -> str:
    global output_path

    file_path = Path(file_path)
    output_path = output_path / file_path.stem
    output_path.mkdir(parents=True, exist_ok=True)

    if not file_path.exists():
        print(f"File {file_path} does not exist.")
        return

    with open(file_path, "r") as f:
        print(f"Reading file: {file_path}")
        text = f.read()

    print(f"read {len(text)} characters")
    return text


def write_charactersheet(id: NamedEntity, summaries: list[str]):
    with open(output_path / f"{id.identifier}.md", "w") as f:
        aliases = ", ".join(sorted(id.aliases, key=lambda k: id.aliases[k]))
        f.write(
            f"**Name:** {id.identifier}\n"
            f"**Gender:** {id.gender}\n"
            f"**Aliases:** {aliases if aliases else "none"}\n\n"
        )
        for l in summaries:
            f.write(f"- {l.strip()}\n")


def main():
    args = sys.argv[1:]
    if not args:
        print("No arguments provided.")
        return

    src = load_data(args[0])
    content = preprocess(src)
    identities = extract_identities(content)
    for id in identities:
        summaries = summarize_character(id, content)
        write_charactersheet(id, summaries)


if __name__ == "__main__":
    main()
