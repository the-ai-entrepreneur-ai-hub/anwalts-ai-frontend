document.addEventListener('DOMContentLoaded', () => {
    // File Upload Logic
    const uploadArea = document.getElementById('file-upload');
    const uploadText = uploadArea.querySelector('p');

    uploadArea.addEventListener('click', () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.pdf,.docx,.txt';
        input.onchange = e => {
            const file = e.target.files[0];
            if (file) {
                uploadText.textContent = `Datei ausgewählt: ${file.name}`;
            }
        }
        input.click();
    });

    // Language Selection Logic
    const langButtons = document.querySelectorAll('.segmented-control button');
    langButtons.forEach(button => {
        button.addEventListener('click', () => {
            langButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
        });
    });

    // Clear Button Logic
    const clearButton = document.querySelector('.btn-secondary');
    const form = document.querySelector('form');
    clearButton.addEventListener('click', () => {
        form.reset();
        // Reset language toggle to default
        langButtons.forEach((btn, index) => {
            if (index === 0) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
        uploadText.textContent = 'Datei hier ablegen oder zum Suchen klicken';
    });
});
