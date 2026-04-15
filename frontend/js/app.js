// frontend/js/app.js
const API_BASE_URL = 'http://localhost:8000/api/v1';

document.addEventListener('DOMContentLoaded', async () => {
    const selectElement = document.getElementById('county-select');
    const downloadBtn = document.getElementById('download-btn');

    // Fetch counties
    try {
        const response = await fetch(`${API_BASE_URL}/counties`);
        if (!response.ok) throw new Error('Failed to fetch counties');
        
        const counties = await response.json();
        
        // Populate select
        selectElement.innerHTML = '<option value="" disabled selected>Select a County...</option>';
        counties.forEach(county => {
            const option = document.createElement('option');
            option.value = county.id;
            option.textContent = county.display;
            selectElement.appendChild(option);
        });

    } catch (error) {
        console.error(error);
        selectElement.innerHTML = '<option value="" disabled>Error loading data</option>';
    }

    // Enable button when a county is selected
    selectElement.addEventListener('change', () => {
        if (selectElement.value) {
            downloadBtn.disabled = false;
        }
    });

    // Handle PDF download
    downloadBtn.addEventListener('click', () => {
        const countyId = selectElement.value;
        if (!countyId) return; // Guard clause

        // Open in new tab which triggers the download
        const pdfUrl = `${API_BASE_URL}/reports/pdf/${countyId}`;
        window.open(pdfUrl, '_blank');
    });
});