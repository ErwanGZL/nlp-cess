# NLP CESS Pipeline

This repository contains the source code resulting from a university NLP project.
HKUST, CSIT6000R Natural Language Processing (Spring 2024-2025).

Character Extraction and Summarization in Stories

> [!NOTE]
> The provided code is parameterized for CPU usage, please change model parameters according to your device.

## Requirements

- [Python](https://www.python.org/) >= 12
- [Ollama](https://ollama.com/), _service for running LLMs locally_
- [uv](https://docs.astral.sh/uv/), _project and dependency manager_

## How to run

We use `uv` as our project manager.

```sh
uv sync
uv run main.py <path/to/file>
```

You are required to provide the path to the story to process as CLI argument.
Results can be found inside the `out/` folder after execution.

A pronoun dictionnary is required at `/pronouns.json`. It can be modified to your needs.
Keep the following structure for the provided program to run:

```json
{
    "feminine": ["..."],
    "masculine": ["..."],
    "neuter": ["..."],
    "titles": ["..."],
}
```

However, please note that the models used in the pipepline are made to work with the english language.

> [!IMPORTANT]
> The pipeline runs a LLM through the **Ollama service**.
> Please ensure that you have Ollama installed and running on your machine.

> [!WARNING]
> The runtime of both the NER and Coreference models require high RAM resources available.
> The memory usage will vary with the length of the input text.
