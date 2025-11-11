
const API_BASE_URL = ' https://opi1s5dgdl.execute-api.af-south-1.amazonaws.com/Prod';

document.getElementById('shortenForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const urlInput = document.getElementById('urlInput');
    const url = urlInput.value.trim();
    
    if (!url) {
        alert('Please enter a valid URL');
        return;
    }
    
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Shortening...';
    submitBtn.disabled = true;
    
    try {
        console.log('Calling API:', API_BASE_URL + '/create');
        const response = await fetch(API_BASE_URL + '/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url })
        });
        
        const data = await response.json();
        console.log('API Response:', data);
        
        if (response.ok) {
            document.getElementById('shortUrlLink').href = data.short_url;
            document.getElementById('shortUrlLink').textContent = data.short_url;
            document.getElementById('originalUrl').textContent = data.original_url;
            document.getElementById('result').classList.remove('hidden');
            document.getElementById('result').scrollIntoView({ behavior: 'smooth' });
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to shorten URL. Check console for details.');
    } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
});

document.getElementById('copyBtn').addEventListener('click', () => {
    const shortUrl = document.getElementById('shortUrlLink').textContent;
    navigator.clipboard.writeText(shortUrl).then(() => {
        const copyBtn = document.getElementById('copyBtn');
        copyBtn.textContent = 'Copied!';
        setTimeout(() => { copyBtn.textContent = 'Copy'; }, 2000);
    });
});
