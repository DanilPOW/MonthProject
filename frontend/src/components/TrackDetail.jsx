import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { getAssignments, submitAssignment, getReviewAssignment, submitReview, getComments, createComment, getNotifications } from '../api'

export default function TrackDetail() {
  const { id } = useParams()
  const [assignments, setAssignments] = useState([])
  const [selectedAssignment, setSelectedAssignment] = useState(null)
  const [repositoryUrl, setRepositoryUrl] = useState('')
  const [reviewData, setReviewData] = useState(null)
  const [score, setScore] = useState('')
  const [reviewComment, setReviewComment] = useState('')
  const [comments, setComments] = useState([])
  const [newComment, setNewComment] = useState('')
  const [notifications, setNotifications] = useState([])

  useEffect(() => {
    loadAssignments()
    loadNotifications()
    const interval = setInterval(loadNotifications, 60000) // каждую минуту
    return () => clearInterval(interval)
  }, [id])

  useEffect(() => {
    if (selectedAssignment) {
      loadComments(selectedAssignment.id)
    }
  }, [selectedAssignment])

  const loadAssignments = async () => {
    try {
      const res = await getAssignments(id)
      setAssignments(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  const loadComments = async (assignmentId) => {
    try {
      const res = await getComments(assignmentId)
      setComments(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  const loadNotifications = async () => {
    try {
      const res = await getNotifications()
      setNotifications(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  const handleSubmit = async () => {
    try {
      await submitAssignment(selectedAssignment.id, repositoryUrl)
      alert('Submitted!')
      setRepositoryUrl('')
      loadAssignments()
    } catch (err) {
      alert(err.response?.data?.detail || 'Error')
    }
  }

  const handleStartReview = async () => {
    try {
      const res = await getReviewAssignment(selectedAssignment.id)
      setReviewData(res.data)
    } catch (err) {
      alert(err.response?.data?.detail || 'Error')
    }
  }

  const handleSubmitReview = async () => {
    try {
      await submitReview(reviewData.submission_id, parseFloat(score), reviewComment)
      alert('Review submitted!')
      setReviewData(null)
      setScore('')
      setReviewComment('')
      loadAssignments()
    } catch (err) {
      alert(err.response?.data?.detail || 'Error')
    }
  }

  const handleAddComment = async () => {
    try {
      await createComment(selectedAssignment.id, newComment)
      setNewComment('')
      loadComments(selectedAssignment.id)
    } catch (err) {
      alert(err.response?.data?.detail || 'Error')
    }
  }

  return (
    <div className="container">
      <h1>Track Detail</h1>
      
      {notifications.length > 0 && (
        <div style={{ background: '#fff3cd', padding: '10px', margin: '10px 0', borderRadius: '5px' }}>
          <h3>Notifications</h3>
          {notifications.map((n, i) => (
            <p key={i}>{n.message}</p>
          ))}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '20px' }}>
        <div>
          <h2>Assignments</h2>
          {assignments.map(assn => (
            <div
              key={assn.id}
              onClick={() => setSelectedAssignment(assn)}
              style={{
                padding: '10px',
                margin: '5px 0',
                background: selectedAssignment?.id === assn.id ? '#e3f2fd' : 'white',
                cursor: 'pointer',
                borderRadius: '5px'
              }}
            >
              {assn.title}
            </div>
          ))}
        </div>

        {selectedAssignment && (
          <div style={{ background: 'white', padding: '20px', borderRadius: '5px' }}>
            <h2>{selectedAssignment.title}</h2>
            <p>{selectedAssignment.description}</p>
            
            <div style={{ marginTop: '20px' }}>
              <h3>Submit Solution</h3>
              <input
                type="text"
                placeholder="Repository URL"
                value={repositoryUrl}
                onChange={(e) => setRepositoryUrl(e.target.value)}
              />
              <button onClick={handleSubmit}>Submit</button>
            </div>

            <div style={{ marginTop: '20px' }}>
              <button onClick={handleStartReview}>Start Code Review</button>
              {reviewData && (
                <div style={{ marginTop: '10px', padding: '10px', background: '#f5f5f5' }}>
                  <p>Review: <a href={reviewData.repository_url} target="_blank" rel="noreferrer">{reviewData.repository_url}</a></p>
                  <input type="number" placeholder="Score" value={score} onChange={(e) => setScore(e.target.value)} />
                  <textarea placeholder="Comment" value={reviewComment} onChange={(e) => setReviewComment(e.target.value)} />
                  <button onClick={handleSubmitReview}>Submit Review</button>
                </div>
              )}
            </div>

            <div style={{ marginTop: '20px' }}>
              <h3>Diary</h3>
              <textarea
                placeholder="Add comment..."
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
              />
              <button onClick={handleAddComment}>Add Comment</button>
              {comments.map(c => (
                <div key={c.id} style={{ marginTop: '10px', padding: '10px', background: '#f9f9f9' }}>
                  <p>{c.text}</p>
                  <small>{new Date(c.created_at).toLocaleString()}</small>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

