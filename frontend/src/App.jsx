import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './components/Login'
import TrackList from './components/TrackList'
import TrackDetail from './components/TrackDetail'

function App() {
  const [user, setUser] = useState(null)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) setUser({ token })
  }, [])

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={!user ? <Login setUser={setUser} /> : <Navigate to="/tracks" />} />
        <Route path="/tracks" element={user ? <TrackList /> : <Navigate to="/login" />} />
        <Route path="/tracks/:id" element={user ? <TrackDetail /> : <Navigate to="/login" />} />
        <Route path="/" element={<Navigate to={user ? "/tracks" : "/login"} />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App

