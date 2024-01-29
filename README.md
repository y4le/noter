## Setup
- install poetry
- `poetry env use python3.9`
- `poetry install`

## TODO
- [ ] invalidate existing embeddings when we use different embedder or model
- [X] invalidate existing summaries when we use different summarizer
- [X] summarize function
- [X] use summarizer in web app
- [ ] allow web app to show multiple side by sides
- [X] parameterize notes folder, storage location, local/openai
- [X] cache summarizations based on file hash
- [X] look into ripgrepy for local full text file search
- [ ] add text search to index.html
- [ ] recursively summarize large files with LocalSummarizer
- [ ] rethink how to specify where .noter is stored, shouldn't be based on run dir
- [ ] auto summarize documents in background
