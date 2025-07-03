document.getElementById('upload-form').addEventListener('submit', async function (e) {
    e.preventDefault();
  
    const form = e.target;
    const formData = new FormData(form);
    const status = document.getElementById('status');
    const progress = document.getElementById('progress');
  
    status.innerText = 'Uploading...';
    progress.style.display = 'block';
  
    try {
      const response = await fetch('/generate-subtitles', {
        method: 'POST',
        body: formData
      });
  
      const data = await response.json();
      progress.style.display = 'none';
  
      if (response.ok && data.success) {
        status.innerText = '✅ ' + data.message;
      } else {
        status.innerText = '❌ Error: ' + data.message;
      }
  
    } catch (error) {
      progress.style.display = 'none';
      console.error(error);
      status.innerText = '❌ Connection error occurred.';
    }
  });
  