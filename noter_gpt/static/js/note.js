function viewSideBySide(similarNote) {
  fetch('/note-content/' + similarNote)
    .then(response => response.text())
    .then(data => {
      document.getElementById('similar_content').innerText = data;
      document.getElementById('similar_content_wrapper').style.display = 'flex';
      summarizeText('similar_content', 'similar_content_summary', true)
    });
}

function summarizeContent(filename, targetId) {
  document.getElementById(targetId).innerText = "";
  document.getElementById(targetId).parentNode.ariaBusy = true;
  fetch('/note-summary/' + filename)
    .then(response => response.text())
    .then(summary => {
      document.getElementById(targetId).innerText = summary;
      document.getElementById(targetId).parentNode.ariaBusy = false;
    });
}

function summarizeText(sourceId, targetId, checkChanged = false) {
  document.getElementById(targetId).innerText = "";
  document.getElementById(targetId).parentNode.ariaBusy = true;
  sourceText = extractTextFromElementById(sourceId);

  fetch('/text-summary', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text: sourceText })
  })
    .then(response => response.text())
    .then(summary => {
      if (checkChanged && extractTextFromElementById(sourceId) != sourceText) {
        return;
      }
      document.getElementById(targetId).innerText = summary;
      document.getElementById(targetId).parentNode.ariaBusy = false;
    });
}

function extractTextFromElementById(id) {
  element = document.getElementById(id);
  return element.value || element.innerText;
}