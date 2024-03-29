function viewSideBySide(similarNote) {
  fetch('/note-content/' + similarNote)
    .then(response => response.text())
    .then(data => {
      document.getElementById('similar_content').innerText = data;
      document.getElementById('similar_content_wrapper').style.display = 'flex';
      summarizeFile(similarNote, 'similar_content_summary', true)
    });
}

let fetchController;

function summarizeFile(filename, targetId, checkChanged = false) {
  document.getElementById(targetId).innerText = "";
  document.getElementById(targetId).parentNode.ariaBusy = true;

  const fetchOptions = {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
    },
  };

  if (checkChanged) {
    if (fetchController) {
      fetchController.abort(); // cancel previous request if necessary
    }
    fetchController = new AbortController();
    fetchOptions.signal = fetchController.signal;
  }

  fetch('/note-summary/' + filename, fetchOptions)
    .then(response => response.text())
    .then(summary => {
      document.getElementById(targetId).innerText = summary;
      document.getElementById(targetId).parentNode.ariaBusy = false;
    }).catch(error => {
      if (error.name === 'AbortError') {
        console.log('Fetch aborted');
      } else {
        console.error('Fetch error:', error);
      }
    });
}

function extractTextFromElementById(id) {
  element = document.getElementById(id);
  return element.value || element.innerText;
}