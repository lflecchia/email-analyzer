const progressContainer = document.getElementById('progress-container');
const progressBar = document.getElementById('progress-bar');
const progressText = document.getElementById('progress-text');
const startBtn = document.getElementById('start-analysis');

startBtn.addEventListener('click', startAnalysis);

async function startAnalysis() {
  progressContainer.classList.remove('hidden');
  progressBar.style.width = '0%';
  progressText.textContent = 'Starting...';
  try {
    await apiFetch('/api/analyze', { method: 'POST' });
    pollProgress();
  } catch (err) {
    progressText.textContent = 'Failed to start analysis';
  }
}

async function pollProgress() {
  while (true) {
    try {
      const data = await apiFetch('/api/progress');
      if (typeof data.progress === 'number') {
        progressBar.style.width = data.progress + '%';
      }
      progressText.textContent = data.message || `${data.progress}%`;
      if (data.status !== 'running') {
        break;
      }
    } catch (err) {
      progressText.textContent = 'Error retrieving progress';
      break;
    }
    await sleep(1000);
  }
}
