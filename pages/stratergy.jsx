import { useState, useEffect } from 'react'
import axios from 'axios'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  PieChart, Pie, Cell, Legend
} from 'recharts'

const API = 'http://localhost:8000'

const PHASE_COLORS = {
  Powerplay: '#3182ce',
  Middle:    '#38a169',
  Slog:      '#d69e2e',
  Death:     '#e53e3e',
}

const DISMISSAL_COLORS = ['#e94560','#3182ce','#38a169','#d69e2e','#805ad5']

export default function Strategy() {
  const [players,    setPlayers]    = useState([])
  const [batsman,    setBatsman]    = useState('DA Warner')
  const [phase,      setPhase]      = useState('death')
  const [strategy,   setStrategy]   = useState(null)
  const [loading,    setLoading]    = useState(false)
  const [llmText,    setLlmText]    = useState('')
  const [llmLoading, setLlmLoading] = useState(false)

  useEffect(() => {
    axios.get(`${API}/players`).then(r => {
      setPlayers(r.data.players.map(p => p.batsman).sort())
    })
    fetchStrategy('DA Warner', 'death')
  }, [])

  async function fetchStrategy(b, p) {
    setLoading(true)
    setStrategy(null)
    setLlmText('')
    try {
      const r = await axios.post(`${API}/strategy`, { batsman: b, phase: p })
      setStrategy(r.data)
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  async function fetchLLM() {
    if (!strategy) return
    setLlmLoading(true)
    try {
      const r = await axios.post(`${API}/llm-strategy`, { batsman, phase })
      setLlmText(r.data.ai_narrative)
    } catch (e) {
      setLlmText('LLM not available. Add Anthropic API credits.')
    }
    setLlmLoading(false)
  }

  function handleGenerate() {
    fetchStrategy(batsman, phase)
  }

  const s = strategy
  const p = s?.stats
  const d = s?.dismissal

  // Chart data
  const phaseData = s ? [
    { phase: 'Powerplay', sr: p.sr_powerplay },
    { phase: 'Middle',    sr: p.sr_middle },
    { phase: 'Slog',      sr: p.sr_slog },
    { phase: 'Death',     sr: p.sr_death },
  ] : []

  const dismissalData = d ? Object.entries(d.probabilities).map(([k, v]) => ({
    name: k, value: v
  })) : []

  const radarData = s ? [
    { subject: 'Dot %',     A: Math.min(p.dot_pct / 60 * 100, 100) },
    { subject: 'Boundary%', A: Math.min(p.boundary_pct / 30 * 100, 100) },
    { subject: 'Avg',       A: Math.min(p.batting_avg / 60 * 100, 100) },
    { subject: 'SR',        A: Math.min(p.strike_rate / 180 * 100, 100) },
    { subject: 'PP SR',     A: Math.min(p.sr_powerplay / 200 * 100, 100) },
    { subject: 'Death SR',  A: Math.min(p.sr_death / 250 * 100, 100) },
  ] : []

  const weaknessColor = s
    ? p.weakness_score > 0.6 ? '#e94560'
    : p.weakness_score > 0.4 ? '#f6ad55'
    : '#48bb78'
    : '#48bb78'

  const weaknessLabel = s
    ? p.weakness_score > 0.6 ? 'HIGH RISK'
    : p.weakness_score > 0.4 ? 'MEDIUM RISK'
    : 'LOW RISK'
    : ''

  return (
    <div>
      {/* Hero */}
      <div className="hero">
        <div className="hero-title">🏏 Cricket Strategy AI</div>
        <div className="hero-sub">AI-powered bowling strategy using 845 IPL matches</div>
        <div className="hero-stats">
          {[['92.4%','ML Accuracy'],['845','Matches'],['398','Players'],['401K','Deliveries']].map(([v,l]) => (
            <div key={l}>
              <div className="hero-stat-val">{v}</div>
              <div className="hero-stat-lbl">{l}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Controls */}
      <div className="card" style={{marginBottom:'1.5rem'}}>
        <div style={{display:'flex', gap:'1rem', alignItems:'flex-end', flexWrap:'wrap'}}>
          <div style={{flex:2, minWidth:'200px'}}>
            <label>Select Batsman</label>
            <select value={batsman} onChange={e => setBatsman(e.target.value)}>
              {players.map(p => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
          <div style={{flex:1, minWidth:'160px'}}>
            <label>Match Phase</label>
            <select value={phase} onChange={e => setPhase(e.target.value)}>
              {['powerplay','middle','slog','death'].map(p => (
                <option key={p} value={p}>{p.charAt(0).toUpperCase()+p.slice(1)}</option>
              ))}
            </select>
          </div>
          <button className="btn btn-primary" onClick={handleGenerate} style={{whiteSpace:'nowrap'}}>
            Generate Strategy
          </button>
        </div>
      </div>

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          Generating AI strategy...
        </div>
      )}

      {s && !loading && (
        <>
          {/* Player Header */}
          <div className="player-header">
            <div>
              <div className="player-name">{s.batsman}</div>
              <div className="player-team">🏟️ {s.team} &nbsp;|&nbsp; 📊 {s.phase} overs</div>
            </div>
            <div style={{textAlign:'center'}}>
              <div style={{fontSize:'0.75rem', color:'var(--text-faint)'}}>WEAKNESS SCORE</div>
              <div className="weakness-score" style={{color: weaknessColor}}>{p.weakness_score}</div>
              <div className="weakness-bar-bg" style={{width:'120px'}}>
                <div className="weakness-bar-fill" style={{
                  width: `${p.weakness_score * 100}%`,
                  background: weaknessColor
                }}></div>
              </div>
              <div style={{fontSize:'0.75rem', color: weaknessColor, marginTop:'0.3rem'}}>{weaknessLabel}</div>
            </div>
            <div style={{textAlign:'center'}}>
              <div style={{fontSize:'0.75rem', color:'var(--text-faint)'}}>MOST LIKELY DISMISSAL</div>
              <div style={{marginTop:'0.5rem'}}>
                <span className="dismissal-pill">{d.most_likely.toUpperCase()}</span>
              </div>
              <div style={{fontSize:'0.75rem', color:'var(--text-muted)', marginTop:'0.5rem'}}>
                {d.probabilities[d.most_likely]?.toFixed(1)}% probability
              </div>
            </div>
          </div>

          {/* Metrics */}
          <div className="metric-grid">
            {[
              ['Matches',     p.matches],
              ['Total Runs',  p.total_runs?.toLocaleString()],
              ['Batting Avg', p.batting_avg?.toFixed(1)],
              ['Strike Rate', p.strike_rate?.toFixed(1)],
              ['Dot Ball %',  p.dot_pct?.toFixed(1) + '%'],
              ['Boundary %',  p.boundary_pct?.toFixed(1) + '%'],
              ['Weakness',    p.weakness_score?.toFixed(3)],
            ].map(([l, v]) => (
              <div className="metric-card" key={l}>
                <div className="metric-val">{v}</div>
                <div className="metric-lbl">{l}</div>
              </div>
            ))}
          </div>

          {/* Charts Row */}
          <div className="grid-3" style={{marginBottom:'1.5rem'}}>

            {/* Phase SR Bar */}
            <div className="card">
              <div className="card-title">Strike Rate by Phase</div>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={phaseData}>
                  <XAxis dataKey="phase" tick={{fill:'#a0aec0', fontSize:11}} />
                  <YAxis tick={{fill:'#a0aec0', fontSize:11}} />
                  <Tooltip
                    contentStyle={{background:'#1a1a2e', border:'1px solid #2d3748', borderRadius:'8px'}}
                    labelStyle={{color:'#e2e8f0'}}
                    itemStyle={{color:'#e94560'}}
                  />
                  <Bar dataKey="sr" radius={[4,4,0,0]}>
                    {phaseData.map((entry) => (
                      <Cell key={entry.phase} fill={PHASE_COLORS[entry.phase] || '#e94560'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Dismissal Pie */}
            <div className="card">
              <div className="card-title">Dismissal Breakdown</div>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={dismissalData}
                    cx="50%" cy="50%"
                    innerRadius={50} outerRadius={80}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {dismissalData.map((_, i) => (
                      <Cell key={i} fill={DISMISSAL_COLORS[i % DISMISSAL_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(v) => [`${v.toFixed(1)}%`]}
                    contentStyle={{background:'#1a1a2e', border:'1px solid #2d3748', borderRadius:'8px'}}
                    itemStyle={{color:'#e2e8f0'}}
                  />
                  <Legend
                    iconType="circle"
                    iconSize={8}
                    formatter={(v) => <span style={{color:'#a0aec0', fontSize:'11px'}}>{v}</span>}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Radar */}
            <div className="card">
              <div className="card-title">Weakness Radar</div>
              <ResponsiveContainer width="100%" height={200}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#2d3748" />
                  <PolarAngleAxis dataKey="subject" tick={{fill:'#a0aec0', fontSize:10}} />
                  <PolarRadiusAxis tick={{fill:'#718096', fontSize:8}} />
                  <Radar dataKey="A" stroke="#e94560" fill="#e94560" fillOpacity={0.25} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Tips + Pitch */}
          <div className="grid-2" style={{marginBottom:'1.5rem'}}>

            {/* Bowling Tips */}
            <div className="card">
              <div className="card-title">AI Bowling Tips</div>
              {s.bowling_tips.map((tip, i) => (
                <div className="tip" key={i}>
                  <span className="tip-num">{i+1}.</span>{tip}
                </div>
              ))}
              <div style={{marginTop:'1.5rem'}}>
                <div className="card-title">Fielding Plan</div>
                {s.fielding_plan.catching?.length > 0 && (
                  <div style={{marginBottom:'0.5rem'}}>
                    <span style={{color:'var(--red)', fontSize:'0.8rem', fontWeight:600}}>Catching: </span>
                    <span style={{color:'var(--text-muted)', fontSize:'0.85rem'}}>{s.fielding_plan.catching.join(', ')}</span>
                  </div>
                )}
                {s.fielding_plan.boundary?.length > 0 && (
                  <div style={{marginBottom:'0.5rem'}}>
                    <span style={{color:'var(--green)', fontSize:'0.8rem', fontWeight:600}}>Boundary: </span>
                    <span style={{color:'var(--text-muted)', fontSize:'0.85rem'}}>{s.fielding_plan.boundary.join(', ')}</span>
                  </div>
                )}
                {s.fielding_plan.pressure?.length > 0 && (
                  <div>
                    <span style={{color:'var(--blue)', fontSize:'0.8rem', fontWeight:600}}>Pressure: </span>
                    <span style={{color:'var(--text-muted)', fontSize:'0.85rem'}}>{s.fielding_plan.pressure.join(', ')}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Pitch Diagram */}
            <div className="card">
              <div className="card-title">Pitch Diagram</div>
              <PitchDiagram fielding={s.fielding_plan} batsman={s.batsman} phase={s.phase} />
            </div>
          </div>

          {/* LLM Section */}
          <div className="card">
            <div className="card-title">Claude AI — Natural Language Strategy</div>
            <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'1rem'}}>
              <span style={{color:'var(--text-muted)', fontSize:'0.85rem'}}>
                Generate a detailed coaching brief using Claude AI
              </span>
              <button className="btn btn-primary" onClick={fetchLLM} disabled={llmLoading}>
                {llmLoading ? 'Generating...' : 'Generate AI Brief'}
              </button>
            </div>
            {llmLoading && <div className="loading"><div className="spinner"></div>Claude AI is thinking...</div>}
            {llmText && (
              <div style={{
                background:'var(--bg-secondary)',
                border:'1px solid var(--border)',
                borderRadius:'8px',
                padding:'1.2rem',
                color:'var(--text-primary)',
                lineHeight:'1.7',
                fontSize:'0.9rem',
                whiteSpace:'pre-wrap'
              }}>
                {llmText}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}

// ── Pitch SVG Component ──
function PitchDiagram({ fielding, batsman, phase }) {
  const positions = {
    'Fine leg':         [0.15,  -0.88],
    'Deep square leg':  [-0.75, -0.58],
    'Square leg':       [-0.52, -0.28],
    'Mid-wicket':       [-0.58,  0.1],
    'Mid-on':           [-0.24,  0.52],
    'Mid-off':          [0.24,   0.52],
    'Cover point':      [0.58,   0.28],
    'Point':            [0.62,  -0.05],
    'Gully':            [0.52,  -0.38],
    '2nd slip':         [0.40,  -0.52],
    'Long-on':          [-0.28,  0.88],
    'Long-off':         [0.28,   0.88],
    'Deep mid-wicket':  [-0.82,  0.38],
    'Short leg':        [-0.18, -0.26],
    'Silly point':      [0.18,  -0.26],
    'Extra cover':      [0.48,   0.42],
    'Cover':            [0.48,   0.22],
    'Short mid-wicket': [-0.26,  0.20],
    'Silly mid-on':     [-0.14,  0.36],
  }

  const colorMap = { catching: '#fc8181', boundary: '#68d391', pressure: '#63b3ed' }
  const cx = 170, cy = 170, r = 150

  return (
    <div>
      <svg viewBox="0 0 340 340" className="pitch-svg">
        {/* Outfield */}
        <circle cx={cx} cy={cy} r={r} fill="#1a5c1a" opacity="0.4" stroke="white" strokeWidth="1.5" strokeOpacity="0.5" />
        {/* Infield */}
        <circle cx={cx} cy={cy} r={r*0.55} fill="#1a7a1a" opacity="0.4" stroke="white" strokeWidth="1" strokeOpacity="0.3" strokeDasharray="4 4" />
        {/* Pitch */}
        <rect x={cx-8} y={cy-30} width="16" height="60" fill="#c8a96e" rx="2" opacity="0.9" />
        {/* Crease */}
        <line x1={cx-8} y1={cy-22} x2={cx+8} y2={cy-22} stroke="white" strokeWidth="1.5" />
        <line x1={cx-8} y1={cy+22} x2={cx+8} y2={cy+22} stroke="white" strokeWidth="1.5" />
        {/* Stumps */}
        {[-3,0,3].map(x => <line key={x} x1={cx+x} y1={cy-27} x2={cx+x} y2={cy-20} stroke="#333" strokeWidth="1.5" />)}
        {[-3,0,3].map(x => <line key={'b'+x} x1={cx+x} y1={cy+20} x2={cx+x} y2={cy+27} stroke="#333" strokeWidth="1.5" />)}
        {/* Batsman */}
        <circle cx={cx} cy={cy+8} r="8" fill="#f6ad55" stroke="white" strokeWidth="1.5" />
        <text x={cx} y={cy+12} textAnchor="middle" fill="white" fontSize="7" fontWeight="bold">B</text>
        {/* Bowler */}
        <polygon points={`${cx},${cy-48} ${cx-6},${cy-36} ${cx+6},${cy-36}`} fill="#63b3ed" stroke="white" strokeWidth="1" />

        {/* Fielders */}
        {Object.entries(fielding).map(([type, positions_list]) =>
          (positions_list || []).map(pos => {
            const coords = positions[pos]
            if (!coords) return null
            const [fx, fy] = coords
            const px = cx + fx * r
            const py = cy - fy * r
            return (
              <g key={pos}>
                <circle cx={px} cy={py} r="11" fill={colorMap[type]} stroke="white" strokeWidth="1.5" />
                <text x={px} y={py+3} textAnchor="middle" fill="white" fontSize="6" fontWeight="bold">
                  {pos.slice(0,3).toUpperCase()}
                </text>
              </g>
            )
          })
        )}
      </svg>

      {/* Legend */}
      <div style={{display:'flex', gap:'1rem', justifyContent:'center', marginTop:'0.5rem', flexWrap:'wrap'}}>
        {[['#fc8181','Catching'],['#68d391','Boundary'],['#63b3ed','Pressure'],['#f6ad55','Batsman']].map(([c,l]) => (
          <div key={l} style={{display:'flex', alignItems:'center', gap:'0.4rem', fontSize:'0.75rem', color:'var(--text-muted)'}}>
            <div style={{width:'8px', height:'8px', borderRadius:'50%', background:c}}></div>
            {l}
          </div>
        ))}
      </div>
    </div>
  )
}