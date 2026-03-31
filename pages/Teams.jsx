import { useState, useEffect } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

const API = 'http://localhost:8000'

export default function Teams() {
  const [teams,       setTeams]       = useState([])
  const [selectedTeam, setSelectedTeam] = useState('')
  const [players,     setPlayers]     = useState([])
  const [loading,     setLoading]     = useState(true)

  useEffect(() => {
    axios.get(`${API}/teams`).then(r => {
      setTeams(r.data.teams)
      setSelectedTeam(r.data.teams[0]?.team || '')
      setLoading(false)
    })
  }, [])

  useEffect(() => {
    if (!selectedTeam) return
    axios.get(`${API}/players?team=${encodeURIComponent(selectedTeam)}`).then(r =>
      setPlayers(r.data.players)
    )
  }, [selectedTeam])

  if (loading) return <div className="loading"><div className="spinner"></div>Loading teams...</div>

  const chartData = teams.map(t => ({
    name: t.team.replace('Royal Challengers Bangalore','RCB')
               .replace('Mumbai Indians','MI')
               .replace('Chennai Super Kings','CSK')
               .replace('Kolkata Knight Riders','KKR')
               .replace('Sunrisers Hyderabad','SRH')
               .replace('Delhi Capitals','DC')
               .replace('Delhi Daredevils','DD')
               .replace('Rajasthan Royals','RR')
               .replace('Kings XI Punjab','KXIP')
               .replace('Punjab Kings','PBKS')
               .replace('Deccan Chargers','DC2')
               .replace('Pune Warriors','PW')
               .replace('Rising Pune Supergiant','RPS')
               .replace('Gujarat Lions','GL'),
    weakness: t.avg_weakness,
    sr: t.avg_strike_rate,
  }))

  return (
    <div>
      <h2 style={{fontSize:'1.5rem', fontWeight:700, marginBottom:'1.5rem', color:'var(--text-primary)'}}>
        Team Analysis
      </h2>

      {/* Team weakness chart */}
      <div className="card" style={{marginBottom:'1.5rem'}}>
        <div className="card-title">Team Average Weakness Score</div>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={chartData} layout="vertical" margin={{left:20}}>
            <XAxis type="number" tick={{fill:'#a0aec0', fontSize:11}} domain={[0,1]} />
            <YAxis dataKey="name" type="category" tick={{fill:'#a0aec0', fontSize:11}} width={50} />
            <Tooltip
              formatter={v => [v.toFixed(3), 'Avg Weakness']}
              contentStyle={{background:'#1a1a2e', border:'1px solid #2d3748', borderRadius:'8px'}}
              labelStyle={{color:'#e2e8f0'}}
            />
            <Bar dataKey="weakness" radius={[0,4,4,0]}>
              {chartData.map((entry) => (
                <Cell
                  key={entry.name}
                  fill={entry.weakness > 0.6 ? '#e94560' : entry.weakness > 0.4 ? '#f6ad55' : '#48bb78'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Team selector + players */}
      <div className="card">
        <div style={{display:'flex', gap:'1rem', alignItems:'flex-end', marginBottom:'1.5rem'}}>
          <div style={{flex:1}}>
            <label>Select Team</label>
            <select value={selectedTeam} onChange={e => setSelectedTeam(e.target.value)}>
              {teams.map(t => <option key={t.team} value={t.team}>{t.team}</option>)}
            </select>
          </div>
          <div style={{display:'flex', gap:'1.5rem'}}>
            {teams.find(t => t.team === selectedTeam) && (() => {
              const t = teams.find(t => t.team === selectedTeam)
              return [
                ['Players',   t.players],
                ['Avg SR',    t.avg_strike_rate?.toFixed(1)],
                ['Avg Weak.', t.avg_weakness?.toFixed(3)],
              ].map(([l,v]) => (
                <div key={l} style={{textAlign:'center'}}>
                  <div style={{fontSize:'1.2rem', fontWeight:700, color:'var(--accent)'}}>{v}</div>
                  <div style={{fontSize:'0.72rem', color:'var(--text-faint)'}}>{l}</div>
                </div>
              ))
            })()}
          </div>
        </div>

        <table>
          <thead>
            <tr>
              <th>Batsman</th>
              <th>Matches</th>
              <th>Avg</th>
              <th>SR</th>
              <th>Dot %</th>
              <th>Boundary %</th>
              <th>Weakness</th>
            </tr>
          </thead>
          <tbody>
            {players.sort((a,b) => b.weakness_score - a.weakness_score).map(p => (
              <tr key={p.batsman}>
                <td style={{fontWeight:600}}>{p.batsman}</td>
                <td>{p.matches}</td>
                <td>{p.batting_avg?.toFixed(1)}</td>
                <td>{p.strike_rate?.toFixed(1)}</td>
                <td style={{color:'var(--text-muted)'}}>{p.dot_pct?.toFixed ? p.dot_pct.toFixed(1)+'%' : '-'}</td>
                <td style={{color:'var(--text-muted)'}}>{p.boundary_pct?.toFixed ? p.boundary_pct.toFixed(1)+'%' : '-'}</td>
                <td>
                  <span style={{
                    fontWeight:700,
                    color: p.weakness_score > 0.6 ? 'var(--red)' :
                           p.weakness_score > 0.4 ? 'var(--amber)' : 'var(--green)'
                  }}>
                    {p.weakness_score?.toFixed(3)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}