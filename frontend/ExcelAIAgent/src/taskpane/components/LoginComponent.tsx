import * as React from 'react'
import { useAuth } from '../../contexts/AuthContext'

export const LoginComponent: React.FC = () => {
  const [email, setEmail] = React.useState('')
  const [password, setPassword] = React.useState('')
  const [isSignUp, setIsSignUp] = React.useState(false)
  const [error, setError] = React.useState('')
  const [loading, setLoading] = React.useState(false)
  
  const { signIn, signUp } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (isSignUp) {
        await signUp(email, password)
        setError('Check your email for confirmation link!')
      } else {
        await signIn(email, password)
      }
    } catch (err: any) {
      setError(err.message || 'Authentication failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container" style={{
      padding: '20px',
      maxWidth: '400px',
      margin: '0 auto',
      fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif'
    }}>
      <h2 style={{ textAlign: 'center', marginBottom: '20px' }}>
        {isSignUp ? 'Sign Up' : 'Sign In'}
      </h2>
      
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
        <div>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{
              width: '100%',
              padding: '10px',
              border: '1px solid #ccc',
              borderRadius: '4px',
              fontSize: '14px'
            }}
          />
        </div>
        
        <div>
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{
              width: '100%',
              padding: '10px',
              border: '1px solid #ccc',
              borderRadius: '4px',
              fontSize: '14px'
            }}
          />
        </div>
        
        {error && (
          <div style={{
            color: '#d32f2f',
            fontSize: '14px',
            textAlign: 'center',
            padding: '10px',
            backgroundColor: '#ffebee',
            borderRadius: '4px'
          }}>
            {error}
          </div>
        )}
        
        <button 
          type="submit" 
          disabled={loading}
          style={{
            width: '100%',
            padding: '12px',
            backgroundColor: loading ? '#ccc' : '#0078d4',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            fontSize: '16px',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Loading...' : (isSignUp ? 'Sign Up' : 'Sign In')}
        </button>
      </form>
      
      <div style={{ textAlign: 'center', marginTop: '15px' }}>
        <button 
          onClick={() => setIsSignUp(!isSignUp)}
          style={{
            background: 'none',
            border: 'none',
            color: '#0078d4',
            cursor: 'pointer',
            fontSize: '14px',
            textDecoration: 'underline'
          }}
        >
          {isSignUp ? 'Already have an account? Sign In' : 'Need an account? Sign Up'}
        </button>
      </div>
      
      {isSignUp && (
        <div style={{
          marginTop: '15px',
          padding: '10px',
          backgroundColor: '#e3f2fd',
          borderRadius: '4px',
          fontSize: '12px',
          color: '#1976d2'
        }}>
          💡 For testing, you can use: test@example.com / TestPassword123!
        </div>
      )}
    </div>
  )
}
