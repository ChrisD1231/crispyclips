import { useState, useEffect } from 'react'
import Importer from './components/Importer'
import ProgressTracker from './components/ProgressTracker'
import Studio from './components/Studio'
import './index.css'

function App() {
  const [jobId, setJobId] = useState(null)
  const [jobData, setJobData] = useState(null)
  
  useEffect(() => {
    let interval;
    if (jobId && (!jobData || jobData.progress < 100)) {
       interval = setInterval(async () => {
         try {
           const res = await fetch(`http://localhost:8000/api/status/${jobId}`)
           const data = await res.json()
           setJobData(data)
           if(data.progress >= 100 || data.status === "Failed") {
             clearInterval(interval)
           }
         } catch(e) {
             console.error(e);
         }
       }, 2000)
    }
    return () => clearInterval(interval)
  }, [jobId, jobData])

  const startJob = async (url) => {
    setJobId(null)
    setJobData(null)
    try {
        const res = await fetch("http://localhost:8000/api/process", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url })
        })
        const data = await res.json()
        setJobId(data.job_id)
    } catch(err) {
        setJobData({status: "Failed", error: "Cannot connect to Backend API."})
    }
  }

  return (
    <div className="app-container" style={{maxWidth: '1200px', margin: '0 auto', padding: '60px 20px'}}>
      <header style={{textAlign: 'center', marginBottom: '60px'}}>
        <h1 style={{fontSize: '3.5rem', fontWeight: 800, background: 'linear-gradient(to right, #fff, #a29bfe)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', letterSpacing: '-1px'}}>
            Crispy Clips
        </h1>
        <p style={{color: 'var(--text-muted)', fontSize: '1.2rem', marginTop: '16px', fontWeight: 500}}>
            Instantly turn long YouTube videos into viral shorts
        </p>
      </header>
      
      {!jobId && (!jobData || jobData.status !== "Failed") && <Importer onStart={startJob} />}
      {jobId && jobData && jobData.progress < 100 && jobData.status !== "Failed" && <ProgressTracker data={jobData} />}
      {jobData?.status === "Failed" && (
          <div className="glass-panel" style={{textAlign: 'center', borderColor: '#ff4757'}}>
              <h2 style={{color: '#ff4757', marginBottom: '10px'}}>Processing Failed</h2>
              <p style={{color: 'var(--text-muted)'}}>{jobData.error}</p>
              <button className="btn-primary" style={{marginTop: '20px', background: 'var(--bg-tertiary)'}} onClick={() => setJobId(null)}>Try Again</button>
          </div>
      )}
      {jobData?.progress === 100 && <Studio clips={jobData.result} jobId={jobId} />}
    </div>
  )
}

export default App
