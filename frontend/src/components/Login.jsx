import { useState } from 'react'
import { register, login } from '../api'

export default function Login({ setUser }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isRegister, setIsRegister] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (isRegister) {
        await register(email, password)
      }
      const res = await login(email, password)
      localStorage.setItem('token', res.data.access_token)
      setUser({ token: res.data.access_token })
    } catch (err) {
      setError(err.response?.data?.detail || 'Error')
    }
  }

  return (
    <div className="container" style={{ maxWidth: '400px', marginTop: '100px' }}>
      <h1>{isRegister ? 'Register' : 'Login'}</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit">{isRegister ? 'Register' : 'Login'}</button>
      </form>
      <button onClick={() => setIsRegister(!isRegister)} style={{ marginTop: '10px', background: '#6c757d' }}>
        {isRegister ? 'Switch to Login' : 'Switch to Register'}
      </button>
    </div>
  )
}

