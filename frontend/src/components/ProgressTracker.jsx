export default function ProgressTracker({ data }) {
    return (
        <div className="glass-panel" style={{maxWidth: '600px', margin: '0 auto'}}>
            <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '12px'}}>
                <span style={{fontWeight: 600, color: 'var(--text-active)'}} className="pulsing">{data.status}</span>
                <span style={{color: 'var(--accent)', fontWeight: 700}}>{data.progress}%</span>
            </div>
            <div className="progress-bar-container">
                <div className="progress-bar-fill" style={{width: `${data.progress}%`}}></div>
            </div>
            <p style={{color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '16px', textAlign: 'center'}}>
                This may take a few minutes depending on video length. AI is processing...
            </p>
        </div>
    )
}
