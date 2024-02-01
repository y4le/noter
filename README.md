# Noter

Noter is a note-taking webapp that helps you write by automatically organizing
and surfacing other relevant notes. It is a personal project and very much
still a prototype. Noter uses a vector database to display related notes
alongside the current note. Notes are automatically summarized and the
resulting summaries are displayed beneath the full content of each note to
give you a quick overview. All features are available with local compute for
privacy, but users have the option to add an OpenAI API key for better and
quicker summarization and embedding.

<img width="1888" alt="noter_example" src="https://github.com/y4le/noter/assets/6445097/57419615-72ba-4691-a588-5ab1c7b7c627">


## Setup
- install poetry [link](https://python-poetry.org/docs/)
- `poetry env use python3.9`
- `poetry install`
- create `.env` file in project directory
  - add `OPENAI_API_KEY` if you want to use openAi API features
  - add `NOTER_NOTES_DIR='~/path/to/your/notes'`
  - optionally add `NOTER_CACHE_DIR='~/path/to/.noter'`, defaults to `.../notes/.noter`

## Usage
- optionally pre-cache summaries:
  - locally generated: `poetry run cli summarize_all` (takes about 4-5 seconds per file)
  - openai generated: `poetry run cli summarize_all --use-openai` (takes 1-1.5 seconds per file)
- start web server:
  - run everything locally: `poetry run cli server`
  - use openAI API: `poetry run cli server --use-openai`
- go to `http://localhost:31337`

## Test
- run non-network tests with `poetry run pytest` in the `tests/` dir
- run all tests with `poetry run pytest --runapi` in the `tests/` dir

## TODO
- similarity search
  - [X] vector database to search for text embeddings
  - [X] invalidate existing embeddings when we use different embedder or model
  - [ ] add instructor embedder https://huggingface.co/hkunlp/instructor-xl
- document summarization
  - [X] cache summarizations based on file hash
  - [X] invalidate existing summaries when we use different summarizer
  - [X] use summarizer in web app
  - [X] auto summarize documents in background (added explicit summarize_all cli command)
  - [ ] recursively summarize large files with LocalSummarizer
- full text search
  - [X] add text search to webapp
  - [X] look into ripgrepy for local full text file search
- usage / ergonomics
  - [X] rethink how to specify where .noter is stored, shouldn't be based on run dir
  - [X] allow webapp to toggle openai with cli param
  - [X] fully support nested notes directories
  - [ ] consider making openai toggle in webapp
