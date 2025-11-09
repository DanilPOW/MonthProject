import axios from 'axios'

const API_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const register = (email, password) =>
  api.post('/register', { email, password })

export const login = (email, password) =>
  api.post('/token', new URLSearchParams({ username: email, password }))

export const getTracks = () => api.get('/tracks')

export const createTrack = (track) => api.post('/tracks', track)

export const joinTrack = (trackId) => api.post(`/tracks/${trackId}/join`)

export const leaveTrack = (trackId) => api.post(`/tracks/${trackId}/leave`)

export const getAssignments = (trackId) => api.get(`/tracks/${trackId}/assignments`)

export const submitAssignment = (assignmentId, repositoryUrl) =>
  api.post(`/assignments/${assignmentId}/submit`, { repository_url: repositoryUrl })

export const getReviewAssignment = (assignmentId) =>
  api.get(`/assignments/${assignmentId}/review`)

export const submitReview = (submissionId, score, comment) =>
  api.post(`/submissions/${submissionId}/review`, { score, comment })

export const getComments = (assignmentId) => api.get(`/assignments/${assignmentId}/comments`)

export const createComment = (assignmentId, text) =>
  api.post(`/assignments/${assignmentId}/comments`, { text })

export const getNotifications = () => api.get('/notifications')

