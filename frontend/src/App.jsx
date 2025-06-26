import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [prompt, setPrompt] = useState('')
  const [response, setResponse] = useState('')
  const [history, setHistory] = useState([])
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    
    try {
      const res = await fetch(import.meta.env.VITE_API_URL + '/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      })
      const data = await res.json()
      setResponse(data.response)
      fetchHistory()
    } catch (err) {
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const fetchHistory = async () => {
    const res = await fetch(import.meta.env.VITE_API_URL + '/api/history')
    const data = await res.json()
    setHistory(data)
  }

  useEffect(() => { fetchHistory() }, [])

  return (
    <div className="app">
      <h1>Gemini AI Assistant</h1>
      
      <form onSubmit={handleSubmit}>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Ask me anything..."
          required
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Thinking...' : 'Ask Gemini'}
        </button>
      </form>

      {response && (
        <div className="response">
          <h3>Response:</h3>
          <p>{response}</p>
        </div>
      )}

      <div className="history">
        <h3>Chat History</h3>
        {history.map(item => (
          <div key={item.id} className="history-item">
            <p><strong>You:</strong> {item.prompt}</p>
            <p><strong>AI:</strong> {item.response}</p>
            <small>{new Date(item.timestamp).toLocaleString()}</small>
          </div>
        ))}
      </div>
    </div>
  )
}

export default App
