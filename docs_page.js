document.addEventListener('DOMContentLoaded', () => {
    const wizardSteps = document.querySelectorAll('.wizard-step');
    const formSections = [
        document.getElementById('step-1-content'),
        document.getElementById('step-2-content'),
        document.getElementById('step-3-content')
    ];
    const nextButton = document.getElementById('next-btn');
    const prevButton = document.getElementById('prev-btn');
    const submitButton = document.getElementById('submit-btn');
    const cancelButton = document.querySelector('.btn-secondary');

    let currentStep = 0;

    const updateWizard = () => {
        wizardSteps.forEach((step, index) => {
            if (index === currentStep) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });

        formSections.forEach((section, index) => {
            if (index === currentStep) {
                section.style.display = 'block';
            } else {
                section.style.display = 'none';
            }
        });

        prevButton.style.display = currentStep === 0 ? 'none' : 'inline-block';
        nextButton.style.display = currentStep === formSections.length - 1 ? 'none' : 'inline-block';
        submitButton.style.display = currentStep === formSections.length - 1 ? 'inline-block' : 'none';
    };

    nextButton.addEventListener('click', () => {
        if (currentStep < formSections.length - 1) {
            currentStep++;
            updateWizard();
        }
    });

    prevButton.addEventListener('click', () => {
        if (currentStep > 0) {
            currentStep--;
            updateWizard();
        }
    });

    cancelButton.addEventListener('click', () => {
        document.querySelector('form').reset();
        currentStep = 0;
        updateWizard();
    });

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

    updateWizard(); // Initial setup
});
