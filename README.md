## Setup
- install poetry
- `poetry env use python3.9`
- `poetry install`
- create `.env` file in project directory
- add `OPENAI_API_KEY` if you want to use openAi API features
- add `NOTER_NOTES_DIR='~/path/to/your/notes'`
- optionally add `NOTER_CACHE_DIR='~/path/to/.noter'`, defaults to `.../notes/.noter`

## Test
- run non-network tests with `poetry run pytest` in the `tests/` dir
- run all tests with `poetry run pytest --runapi` in the `tests/` dir

## TODO
- [ ] invalidate existing embeddings when we use different embedder or model
- [X] invalidate existing summaries when we use different summarizer
- [X] summarize function
- [X] use summarizer in web app
- [ ] allow web app to show multiple side by sides
- [X] parameterize notes folder, storage location, local/openai
- [X] cache summarizations based on file hash
- [X] look into ripgrepy for local full text file search
- [X] add text search to index.html
- [ ] recursively summarize large files with LocalSummarizer
- [X] rethink how to specify where .noter is stored, shouldn't be based on run dir
- [ ] auto summarize documents in background
- [ ] add instructor embedder https://huggingface.co/hkunlp/instructor-xl
- [X] fully support nested notes directories
