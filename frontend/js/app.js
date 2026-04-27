// frontend/js/app.js
const DEFAULT_API_BASE_URL = '/api/v1';
const LOCAL_API_BASE_URL = 'http://localhost:3000/api/v1';
function resolveApiBaseUrl() {
    const configuredApiBaseUrl = window.APP_CONFIG?.API_BASE_URL;
    if (configuredApiBaseUrl) {
        return configuredApiBaseUrl;
    }
    const hostname = window.location.hostname;
    const port = window.location.port;
    const isLocalFrontendHost = hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '0.0.0.0';
    const isBackendOrigin = port === '8000';
    if (isLocalFrontendHost && !isBackendOrigin) {
        return LOCAL_API_BASE_URL;
    }
    return DEFAULT_API_BASE_URL;
}
const API_BASE_URL = resolveApiBaseUrl();

document.addEventListener('DOMContentLoaded', async () => {
    const selectElement = document.getElementById('county-select');
    const downloadBtn = document.getElementById('download-btn');

    // Fetch counties
    try {
        const response = await fetch(`${API_BASE_URL}/counties`);
        if (!response.ok) throw new Error('Falha ao carregar os municípios');
        
        const counties = await response.json();
        
        // Populate select
        selectElement.innerHTML = '<option value="" disabled selected>Selecione um município...</option>';
        counties.forEach(county => {
            const option = document.createElement('option');
            option.value = county.id;
            option.textContent = county.display;
            selectElement.appendChild(option);
        });

    } catch (error) {
        console.error(error);
        selectElement.innerHTML = '<option value="" disabled>Erro ao carregar os municípios</option>';
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