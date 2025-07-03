document.getElementById('uploadForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const fileInput = document.getElementById('file');
    const submitBtn = document.getElementById('submitBtn');
    const progressDiv = document.getElementById('progress');
    const statusDiv = document.getElementById('status');
    const downloadDiv = document.getElementById('downloadLink');
    const srtLink = document.getElementById('srtLink');

    // Reset UI
    statusDiv.style.display = 'none';
    downloadDiv.style.display = 'none';
    submitBtn.disabled = true;
    progressDiv.style.display = 'block';

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('model_size', document.getElementById('model').value);
    formData.append('lang', document.getElementById('language').value);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || 'Upload failed with status ' + response.status);
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const filename = fileInput.files[0].name.replace(/\.[^/.]+$/, "") + '.srt';

        srtLink.href = url;
        srtLink.download = filename;

        statusDiv.textContent = 'Subtitles generated successfully!';
        statusDiv.className = 'success';
        statusDiv.style.display = 'block';
        downloadDiv.style.display = 'block';

    } catch (error) {
        console.error('Error:', error);
        statusDiv.textContent = 'Error: ' + error.message;
        statusDiv.className = 'error';
        statusDiv.style.display = 'block';
    } finally {
        submitBtn.disabled = false;
        progressDiv.style.display = 'none';
    }
}); 