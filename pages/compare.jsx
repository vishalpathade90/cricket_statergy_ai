import { useState, useEffect } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts'

const API = 'http://localhost:8000'

export default function Compare() {
  const [players,  setPlayers]  = useState([])
  const [playerA,  setPlayerA]  = useState('DA Warner')
  const [playerB,  setPlayerB]  = useState('CH Gayle')
  const [phase,    setPhase]    = useState('death')
  const [result,   setResult]   = useState(null)
  const [loading,  setLoading]  = useState(false)

  useEffect(() => {
    axios.get(`${API}/players`).then(r =>
      setPlayers(r.data.players.map(p => p.batsman).sort())
    )
  }, [])

  async function compare() {
    setLoading(true)
    setResult(null)
    try {
      const r = await axios.post(`${API}/compare`, {
        player_a: playerA, player_b: playerB, phase
      })
      setResult(r.data)
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  const phaseKeys = ['sr_powerplay','sr_middle','sr_slog','sr_death']
  const phaseLabels = ['Powerplay','Middle','Slog','Death']

  const phaseData = result ? phaseLabels.map((label, i) => ({
    phase: label,
    [playerA]: result.player_a.stats[phaseKeys[i]],
    [playerB]: result.player_b.stats[phaseKeys[i]],
  })) : []

  const metrics = result ? [
    { label: 'Batting Avg',  a: result.player_a.stats.batting_avg,    b: result.player_b.stats.batting_avg,    higherBetter: true },
    { label: 'Strike Rate',  a: result.player_a.stats.strike_rate,    b: result.player_b.stats.strike_rate,    higherBetter: true },
    { label: 'Dot Ball %',   a: result.player_a.stats.dot_pct,        b: result.player_b.stats.dot_pct,        higherBetter: false },
    { label: 'Boundary %',   a: result.player_a.stats.boundary_pct,   b: result.player_b.stats.boundary_pct,   higherBetter: true },
    { label: 'Weakness',     a: result.player_a.stats.weakness_score, b: result.player_b.stats.weakness_score, higherBetter: false },
  ] : []

  return (
    <div>
      <h2 style={{fontSize:'1.5rem', fontWeight:700, marginBottom:'1.5rem', color:'var(--text-primary)'}}>
        Player Comparison
      </h2>

      {/* Controls */}
      <div className="card" style={{marginBottom:'1.5rem'}}>
        <div style={{display:'flex', gap:'1rem', alignItems:'flex-end', flexWrap:'wrap'}}>
          <div style={{flex:1, minWidth:'180px'}}>
            <label>Player A</label>
            <select value={playerA} onChange={e => setPlayerA(e.target.value)}>
              {players.map(p => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
          <div style={{flex:1, minWidth:'180px'}}>
            <label>Player B</label>
            <select value={playerB} onChange={e => setPlayerB(e.target.value)}>
              {players.map(p => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
          <div style={{flex:1, minWidth:'140px'}}>
            <label>Phase</label>
            <select value={phase} onChange={e => setPhase(e.target.value)}>
              {['powerplay','middle','slog','death'].map(p => (
                <option key={p} value={p}>{p.charAt(0).toUpperCase()+p.slice(1)}</option>
              ))}
            </select>
          </div>
          <button className="btn btn-primary" onClick={compare}>Compare</button>
        </div>
      </div>

      {loading && <div className="loading"><div className="spinner"></div>Comparing players...</div>}

      {result && !loading && (
        <>
          {/* Recommendation */}
          <div style={{
            background:'rgba(233,69,96,0.1)',
            border:'1px solid var(--accent)',
            borderRadius:'10px',
            padding:'1rem 1.5rem',
            marginBottom:'1.5rem',
            display:'flex',
            alignItems:'center',
            gap:'1rem'
          }}>
            <span style={{fontSize:'1.5rem'}}>🎯</span>
            <div>
              <div style={{fontWeight:700, color:'var(--accent)'}}>AI Recommendation</div>
              <div style={{color:'var(--text-muted)', fontSize:'0.9rem'}}>{result.recommendation}</div>
            </div>
          </div>

          {/* Head to head */}
          <div className="grid-2" style={{marginBottom:'1.5rem'}}>
            {[result.player_a, result.player_b].map((player, idx) => (
              <div className="card" key={idx}>
                <div style={{
                  fontSize:'1.2rem', fontWeight:700,
                  color: result.weaker_batsman === player.batsman ? 'var(--red)' : 'var(--green)',
                  marginBottom:'0.5rem'
                }}>
                  {player.batsman}
                  {result.weaker_batsman === player.batsman &&
                    <span className="badge badge-red" style={{marginLeft:'0.5rem', fontSize:'0.65rem'}}>WEAKER</span>
                  }
                </div>
                <div style={{color:'var(--text-muted)', fontSize:'0.8rem', marginBottom:'1rem'}}>{player.team}</div>
                {metrics.map(m => {
                  const val  = idx === 0 ? m.a : m.b
                  const other = idx === 0 ? m.b : m.a
                  const better = m.higherBetter ? val >= other : val <= other
                  return (
                    <div key={m.label} style={{
                      display:'flex', justifyContent:'space-between',
                      padding:'0.5rem 0',
                      borderBottom:'1px solid var(--border)'
                    }}>
                      <span style={{color:'var(--text-faint)', fontSize:'0.85rem'}}>{m.label}</span>
                      <span style={{
                        fontWeight:600, fontSize:'0.9rem',
                        color: better ? 'var(--green)' : 'var(--red)'
                      }}>
                        {typeof val === 'number' ? val.toFixed(1) : val}
                      </span>
                    </div>
                  )
                })}
              </div>
            ))}
          </div>

          {/* Phase SR Chart */}
          <div className="card">
            <div className="card-title">Phase Strike Rate Comparison</div>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={phaseData} barGap={4}>
                <XAxis dataKey="phase" tick={{fill:'#a0aec0', fontSize:12}} />
                <YAxis tick={{fill:'#a0aec0', fontSize:12}} />
                <Tooltip
                  contentStyle={{background:'#1a1a2e', border:'1px solid #2d3748', borderRadius:'8px'}}
                  labelStyle={{color:'#e2e8f0'}}
                />
                <Legend formatter={v => <span style={{color:'#a0aec0'}}>{v}</span>} />
                <Bar dataKey={playerA} fill="#e94560" radius={[4,4,0,0]} />
                <Bar dataKey={playerB} fill="#3182ce" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  )
}