import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getTracks, joinTrack, leaveTrack } from '../api'

export default function TrackList() {
  const [tracks, setTracks] = useState([])
  const navigate = useNavigate()

  useEffect(() => {
    loadTracks()
  }, [])

  const loadTracks = async () => {
    try {
      const res = await getTracks()
      setTracks(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  const handleJoin = async (trackId) => {
    try {
      await joinTrack(trackId)
      loadTracks()
    } catch (err) {
      alert(err.response?.data?.detail || 'Error')
    }
  }

  const handleLeave = async (trackId) => {
    try {
      await leaveTrack(trackId)
      loadTracks()
    } catch (err) {
      alert(err.response?.data?.detail || 'Error')
    }
  }

  return (
    <div className="container">
      <h1>Tracks</h1>
      {tracks.map(track => (
        <div key={track.id} style={{ background: 'white', padding: '20px', margin: '10px 0', borderRadius: '5px' }}>
          <h2>{track.title}</h2>
          <p>{track.description}</p>
          <p>Participants: {track.participant_count}/{track.quota}</p>
          {track.started_at && <p style={{ color: 'green' }}>Started</p>}
          <div style={{ marginTop: '10px' }}>
            <button onClick={() => navigate(`/tracks/${track.id}`)}>View</button>
            {!track.started_at && (
              track.participant_count < track.quota ? (
                <button onClick={() => handleJoin(track.id)} style={{ marginLeft: '10px' }}>Join</button>
              ) : (
                <button onClick={() => handleLeave(track.id)} style={{ marginLeft: '10px', background: '#dc3545' }}>Leave</button>
              )
            )}
          </div>
        </div>
      ))}
    </div>
  )
}

