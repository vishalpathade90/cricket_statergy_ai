import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom'
import Strategy from './pages/Strategy'
import Compare from './pages/Compare'
import Leaderboard from './pages/Leaderboard'
import Teams from './pages/Teams'
import './App.css'

export default function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="nav-brand">
            <span className="nav-icon">🏏</span>
            <span className="nav-title">Cricket Strategy AI</span>
            <span className="nav-badge">92.4% Accuracy</span>
          </div>
          <div className="nav-links">
            <NavLink to="/" end className={({isActive}) => isActive ? 'nav-link active' : 'nav-link'}>Strategy</NavLink>
            <NavLink to="/compare" className={({isActive}) => isActive ? 'nav-link active' : 'nav-link'}>Compare</NavLink>
            <NavLink to="/teams" className={({isActive}) => isActive ? 'nav-link active' : 'nav-link'}>Teams</NavLink>
            <NavLink to="/leaderboard" className={({isActive}) => isActive ? 'nav-link active' : 'nav-link'}>Leaderboard</NavLink>
          </div>
          <div className="nav-status">
            <span className="status-dot"></span>
            <span className="status-text">API Live</span>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Strategy />} />
            <Route path="/compare" element={<Compare />} />
            <Route path="/teams" element={<Teams />} />
            <Route path="/leaderboard" element={<Leaderboard />} />
          </Routes>
        </main>

        <footer className="footer">
          <span>Cricket Strategy AI v2.0</span>
          <span>•</span>
          <span>IPL 2007–2021</span>
          <span>•</span>
          <span>845 Matches • 401K Deliveries • 398 Players</span>
          <span>•</span>
          <span>Built by Vishal</span>
        </footer>
      </div>
    </Router>
  )
}
