import { useState } from 'react';

export default function Studio({ clips, jobId }) {
    const [localClips, setLocalClips] = useState(clips);
    const [editingIndex, setEditingIndex] = useState(null);
    const [editForm, setEditForm] = useState({ font: 'Arial Black', color: '&H00FFFFFF', position: 'Middle' });
    const [loadingIndex, setLoadingIndex] = useState(null);

    if (!localClips || localClips.length === 0) {
        return <div style={{textAlign: 'center', color: 'var(--text-muted)'}}>No clips were generated. Try a different video.</div>
    }

    const handleDownload = async (url, title) => {
        try {
            const res = await fetch(url);
            const blob = await res.blob();
            const blobUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = blobUrl;
            a.download = `${title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.mp4`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(blobUrl);
        } catch (e) {
            console.error('Download failed', e);
        }
    };

    const handleShare = async (clip) => {
        if (navigator.share) {
            try {
                await navigator.share({
                    title: clip.title,
                    text: `${clip.title}\n\n${clip.description}\n\n${(clip.tags || []).map(t => '#' + t).join(' ')}`,
                    url: window.location.origin + clip.url.replace('http://localhost:8000', '') // basic attempt to make it absolute if needed, or just use clip.url
                });
            } catch (error) {
                console.error('Error sharing', error);
            }
        } else {
            // Fallback: Copy generic share text to clipboard
            navigator.clipboard.writeText(`${clip.title}\n\n${clip.url}`);
            alert('Link copied to clipboard!');
        }
    };

    const handleRerender = async (index) => {
        setLoadingIndex(index);
        try {
            const res = await fetch('http://localhost:8000/api/rerender', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    job_id: jobId,
                    clip_index: index,
                    ...editForm
                })
            });
            const data = await res.json();
            if (data.success) {
                const updatedClips = [...localClips];
                updatedClips[index].url = data.url;
                setLocalClips(updatedClips);
            }
        } catch (e) {
            console.error('Rerender failed', e);
        }
        setLoadingIndex(null);
        setEditingIndex(null);
    };

    return (
        <div style={{animation: 'pulse 0.5s ease-out', animationIterationCount: 1}}>
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '32px'}}>
                <div>
                    <h2 style={{fontSize: '2rem', fontWeight: 700}}>Clip Studio</h2>
                    <p style={{color: 'var(--text-muted)', marginTop: '8px'}}>Your viral shorts are ready to publish.</p>
                </div>
                <button className="btn-primary" style={{padding: '12px 24px'}}>Batch Export All</button>
            </div>
            
            <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '24px'}}>
                {localClips.map((clip, i) => (
                    <div key={i} className="glass-panel" style={{padding: '16px', display: 'flex', flexDirection: 'column'}}>
                        <div style={{position: 'relative', width: '100%', paddingTop: '177%', backgroundColor: '#000', borderRadius: '12px', overflow: 'hidden', marginBottom: '16px'}}>
                             <video 
                                key={clip.url}
                                src={clip.url} 
                                controls 
                                preload="metadata"
                                style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'cover', opacity: loadingIndex === i ? 0.5 : 1}}
                             />
                             {loadingIndex === i && (
                                <div style={{position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', color: 'white', fontWeight: 'bold'}}>
                                    Re-rendering...
                                </div>
                             )}
                             <div style={{position: 'absolute', top: '12px', right: '12px', background: 'rgba(0,0,0,0.6)', padding: '6px 10px', borderRadius: '6px', fontSize: '0.85rem', fontWeight: 700, color: '#2ed573'}}>
                                {clip.duration}s
                             </div>
                             <div style={{position: 'absolute', top: '12px', left: '12px', background: 'var(--accent)', padding: '6px 10px', borderRadius: '6px', fontSize: '0.85rem', fontWeight: 700, boxShadow: 'var(--neon-glow)'}}>
                                Score: {clip.score}
                             </div>
                        </div>
                        <div style={{background: 'rgba(255,255,255,0.05)', padding: '12px', borderRadius: '8px', marginBottom: '16px', display: 'flex', flexDirection: 'column', flexGrow: 1}}>
                            <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '4px'}}>
                                <strong style={{color: 'var(--text-active)', fontSize: '0.9rem'}}>Viral Title</strong>
                                <button onClick={() => navigator.clipboard.writeText(clip.title)} style={{background: 'none', border: 'none', color: 'var(--accent)', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 'bold'}}>Copy</button>
                            </div>
                            <div style={{marginBottom: '16px', color: 'var(--text-muted)', fontSize: '0.95rem', lineHeight: '1.4'}}>{clip.title}</div>
                            
                            <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '4px'}}>
                                <strong style={{color: 'var(--text-active)', fontSize: '0.9rem'}}>Description & Tags</strong>
                                <button onClick={() => navigator.clipboard.writeText(`${clip.description}\n\n${(clip.tags || []).map(t => '#' + t).join(' ')}`)} style={{background: 'none', border: 'none', color: 'var(--accent)', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 'bold'}}>Copy</button>
                            </div>
                            <div style={{height: '80px', overflowY: 'auto', color: 'var(--text-muted)', fontSize: '0.85rem', whiteSpace: 'pre-wrap', paddingRight: '4px', border: '1px solid rgba(255,255,255,0.1)', padding: '8px', borderRadius: '4px'}}>
                                {clip.description}
                                <br/><br/>
                                <span style={{color: 'var(--accent)'}}>{(clip.tags || []).map(t => '#' + t).join(' ')}</span>
                            </div>
                        </div>
                        {editingIndex === i ? (
                            <div style={{background: 'rgba(0,0,0,0.2)', padding: '12px', borderRadius: '8px', marginBottom: '16px', display: 'flex', flexDirection: 'column', gap: '8px'}}>
                                <select value={editForm.font} onChange={(e) => setEditForm({...editForm, font: e.target.value})} style={{padding: '8px', borderRadius: '4px', background: 'var(--bg-secondary)', color: 'white'}}>
                                    <option value="Arial Black">Arial Black</option>
                                    <option value="Impact">Impact</option>
                                    <option value="Tahoma">Tahoma</option>
                                    <option value="Comic Sans MS">Comic Sans (Ironic)</option>
                                </select>
                                <select value={editForm.color} onChange={(e) => setEditForm({...editForm, color: e.target.value})} style={{padding: '8px', borderRadius: '4px', background: 'var(--bg-secondary)', color: 'white'}}>
                                    <option value="&H00FFFFFF">White Text</option>
                                    <option value="&H0000FFFF">Yellow Text</option>
                                    <option value="&H0000FF00">Neon Green Text</option>
                                    <option value="&H000000FF">Red Text</option>
                                </select>
                                <select value={editForm.position} onChange={(e) => setEditForm({...editForm, position: e.target.value})} style={{padding: '8px', borderRadius: '4px', background: 'var(--bg-secondary)', color: 'white'}}>
                                    <option value="Top">Top Position</option>
                                    <option value="Middle">Middle Position</option>
                                    <option value="Bottom">Bottom Position</option>
                                </select>
                                <div style={{display: 'flex', gap: '8px', marginTop: '4px'}}>
                                    <button onClick={() => setEditingIndex(null)} style={{flex: 1, padding: '8px', background: 'transparent', border: '1px solid white', color: 'white', cursor: 'pointer', borderRadius: '4px'}}>Cancel</button>
                                    <button onClick={() => handleRerender(i)} style={{flex: 1, padding: '8px', background: 'var(--accent)', border: 'none', color: 'white', cursor: 'pointer', borderRadius: '4px', fontWeight: 'bold'}}>Apply</button>
                                </div>
                            </div>
                        ) : (
                            <div style={{display: 'flex', gap: '8px'}}>
                                 <button className="btn-primary" style={{flex: 1, padding: '10px', background: 'var(--bg-tertiary)', color: 'var(--text-active)', boxShadow: 'none', fontSize: '0.9rem'}} onClick={() => { setEditingIndex(i); setEditForm({ font: 'Arial Black', color: '&H00FFFFFF', position: 'Middle' }); }}>Edit</button>
                                 <button onClick={() => handleShare(clip)} className="btn-primary" style={{flex: 1, padding: '10px', background: 'var(--bg-secondary)', color: 'var(--text-active)', border: 'none', cursor: 'pointer', boxShadow: 'none', fontSize: '0.9rem'}}>Share</button>
                                 <button onClick={() => handleDownload(clip.url, clip.title)} className="btn-primary" style={{flex: 1, padding: '10px', textAlign: 'center', border: 'none', cursor: 'pointer', fontSize: '0.9rem'}}>Download</button>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    )
}
