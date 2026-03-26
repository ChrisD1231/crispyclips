import { useState } from 'react'

export default function Importer({ onStart }) {
  const [url, setUrl] = useState("")
  const [downloadingRaw, setDownloadingRaw] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault()
    if(url.trim()) onStart(url)
  }

  const handleRawDownload = async () => {
    if (!url.trim()) return;
    setDownloadingRaw(true);
    try {
      const res = await fetch('http://localhost:8000/api/download_raw', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });
      const data = await res.json();
      if (data.success) {
        // Trigger download via Blob
        const fileRes = await fetch(data.url);
        const blob = await fileRes.blob();
        const blobUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = blobUrl;
        a.download = `${data.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.mp4`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(blobUrl);
      } else {
        alert('Download failed server-side');
      }
    } catch (e) {
      console.error(e);
      alert('Error downloading video');
    }
    setDownloadingRaw(false);
  }

  return (
    <div className="glass-panel" style={{maxWidth: '700px', margin: '0 auto', textAlign: 'center'}}>
      <div style={{marginBottom: '32px'}}>
         <h2 style={{fontSize: '1.8rem', fontWeight: 600, marginBottom: '8px'}}>Start Clipping</h2>
         <p style={{color: 'var(--text-muted)'}}>Drop a YouTube link below to let AI find your best hooks.</p>
      </div>
      <form onSubmit={handleSubmit} style={{display: 'flex', gap: '16px', flexDirection: 'column'}}>
        <div style={{position: 'relative'}}>
            <input 
              className="input-field"
              type="url" 
              placeholder="https://www.youtube.com/watch?v=..." 
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              required
              style={{paddingLeft: '48px', height: '64px', fontSize: '1.2rem'}}
            />
            <svg style={{position: 'absolute', left: '16px', top: '20px', color: '#ff0000'}} width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M21.582,6.186c-0.23-0.86-0.908-1.538-1.768-1.768C18.254,4,12,4,12,4S5.746,4,4.186,4.418 c-0.86,0.23-1.538,0.908-1.768,1.768C2,7.746,2,12,2,12s0,4.254,0.418,5.814c0.23,0.86,0.908,1.538,1.768,1.768 C5.746,20,12,20,12,20s6.254,0,7.814-0.418c0.86-0.23,1.538-0.908,1.768-1.768C22,16.254,22,12,22,12S22,7.746,21.582,6.186z M9.996,15.005l0-6.01L15.224,12L9.996,15.005z"/>
            </svg>
        </div>
        <div style={{display: 'flex', gap: '16px'}}>
            <button type="submit" className="btn-primary" style={{flex: 2, height: '56px', fontSize: '1.1rem'}} disabled={!url.trim()}>
              Generate Viral Shorts
            </button>
            <button type="button" onClick={handleRawDownload} className="btn-primary" style={{flex: 1, height: '56px', fontSize: '1.1rem', backgroundColor: 'var(--bg-secondary)', color: 'white', border: 'none'}} disabled={!url.trim() || downloadingRaw}>
              {downloadingRaw ? 'Downloading...' : 'Download Original'}
            </button>
        </div>
      </form>
    </div>
  )
}
