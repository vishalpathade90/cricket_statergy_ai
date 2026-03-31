import { useState, useEffect } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000'

export default function Leaderboard() {
  const [weakest,   setWeakest]   = useState([])
  const [strongest, setStrongest] = useState([])
  const [loading,   setLoading]   = useState(true)

  useEffect(() => {
    Promise.all([
      axios.get(`${API}/leaderboard?order=weakest&limit=15`),
      axios.get(`${API}/leaderboard?order=strongest&limit=15`),
    ]).then(([w, s]) => {
      setWeakest(w.data.players)
      setStrongest(s.data.players)
      setLoading(false)
    })
  }, [])

  const weaknessColor = score =>
    score > 0.6 ? 'var(--red)' :
    score > 0.4 ? 'var(--amber)' :
    'var(--green)'

  if (loading) return <div className="loading"><div className="spinner"></div>Loading leaderboard...</div>

  return (
    <div>
      <h2 style={{fontSize:'1.5rem', fontWeight:700, marginBottom:'1.5rem', color:'var(--text-primary)'}}>
        IPL Leaderboard
      </h2>

      <div className="grid-2">
        {/* Weakest */}
        <div className="card">
          <div className="card-title">Most Dismissable Batsmen</div>
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Batsman</th>
                <th>Team</th>
                <th>Avg</th>
                <th>SR</th>
                <th>Weakness</th>
                <th>Dismissal</th>
              </tr>
            </thead>
            <tbody>
              {weakest.map((p, i) => (
                <tr key={p.batsman}>
                  <td style={{color:'var(--accent)', fontWeight:700}}>{i+1}</td>
                  <td style={{fontWeight:600}}>{p.batsman}</td>
                  <td style={{color:'var(--text-muted)', fontSize:'0.8rem'}}>{p.team}</td>
                  <td>{p.batting_avg?.toFixed(1)}</td>
                  <td>{p.strike_rate?.toFixed(1)}</td>
                  <td>
                    <span style={{
                      color: weaknessColor(p.weakness_score),
                      fontWeight:700
                    }}>
                      {p.weakness_score?.toFixed(3)}
                    </span>
                  </td>
                  <td>
                    <span className={`badge badge-${p.most_likely_dismissal === 'CAUGHT' ? 'red' : 'blue'}`}
                      style={{fontSize:'0.65rem'}}>
                      {p.most_likely_dismissal}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Strongest */}
        <div className="card">
          <div className="card-title">Strongest Batsmen</div>
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Batsman</th>
                <th>Team</th>
                <th>Avg</th>
                <th>SR</th>
                <th>Weakness</th>
                <th>Matches</th>
              </tr>
            </thead>
            <tbody>
              {strongest.map((p, i) => (
                <tr key={p.batsman}>
                  <td style={{color:'var(--green)', fontWeight:700}}>{i+1}</td>
                  <td style={{fontWeight:600}}>{p.batsman}</td>
                  <td style={{color:'var(--text-muted)', fontSize:'0.8rem'}}>{p.team}</td>
                  <td>{p.batting_avg?.toFixed(1)}</td>
                  <td>{p.strike_rate?.toFixed(1)}</td>
                  <td>
                    <span style={{color:'var(--green)', fontWeight:700}}>
                      {p.weakness_score?.toFixed(3)}
                    </span>
                  </td>
                  <td>{p.matches}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
