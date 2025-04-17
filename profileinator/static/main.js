document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('upload-form');
    const photoUpload = document.getElementById('photo-upload');
    const numVariants = document.getElementById('num-variants');
    const generateButton = document.getElementById('generate-button');
    const preview = document.getElementById('preview');
    const uploadedImage = document.getElementById('uploaded-image');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const profileImages = document.getElementById('profile-images');

    // Show preview when file is selected
    photoUpload.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                uploadedImage.src = e.target.result;
                preview.classList.remove('hidden');
            };
            reader.readAsDataURL(file);
        }
    });

    // Handle form submission
    uploadForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const file = photoUpload.files[0];
        if (!file) {
            alert('Please select an image file');
            return;
        }

        // Show loading spinner
        loading.classList.remove('hidden');
        results.classList.add('hidden');
        generateButton.disabled = true;

        // Create FormData and append file and options
        const formData = new FormData();
        formData.append('image', file);
        formData.append('num_variants', numVariants.value);

        try {
            const response = await fetch('/generate/', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`Server returned ${response.status}`);
            }

            const data = await response.json();
            
            // When the API returns images, display them
            if (data.images && data.images.length > 0) {
                displayProfileImages(data.images);
            } else {
                // Fallback for when we're still in development
                profileImages.innerHTML = `<p>Profile generation will be implemented soon!</p>`;
            }
            
            results.classList.remove('hidden');
        } catch (error) {
            console.error('Error generating profiles:', error);
            alert('Failed to generate profiles. Please try again.');
        } finally {
            loading.classList.add('hidden');
            generateButton.disabled = false;
        }
    });

    // Function to display generated profile images
    function displayProfileImages(images) {
        profileImages.innerHTML = '';
        
        images.forEach((imageData, index) => {
            const card = document.createElement('div');
            card.className = 'profile-card';
            
            const img = document.createElement('img');
            img.className = 'profile-image';
            img.src = `data:image/jpeg;base64,${imageData}`;
            img.alt = `AI Generated Profile ${index + 1}`;
            
            const actions = document.createElement('div');
            actions.className = 'profile-actions';
            
            const downloadBtn = document.createElement('button');
            downloadBtn.className = 'download-button';
            downloadBtn.textContent = 'Download';
            downloadBtn.addEventListener('click', () => {
                downloadImage(imageData, `profile-${index + 1}.jpg`);
            });
            
            actions.appendChild(downloadBtn);
            card.appendChild(img);
            card.appendChild(actions);
            profileImages.appendChild(card);
        });
    }

    // Function to download an image
    function downloadImage(base64Data, filename) {
        const link = document.createElement('a');
        link.href = `data:image/jpeg;base64,${base64Data}`;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
});
