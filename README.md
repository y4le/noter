## Setup
- install poetry
- `poetry env use python3.9`
- `poetry install`
- create `.env` file in project directory
  - add `OPENAI_API_KEY` if you want to use openAi API features
  - add `NOTER_NOTES_DIR='~/path/to/your/notes'`
  - optionally add `NOTER_CACHE_DIR='~/path/to/.noter'`, defaults to `.../notes/.noter`

## Usage
- optionally pre-cache summaries:
  - locally generated: `poetry run cli summarize_all`
  - openai generated: `poetry run cli summarize_all --use-openai`
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
