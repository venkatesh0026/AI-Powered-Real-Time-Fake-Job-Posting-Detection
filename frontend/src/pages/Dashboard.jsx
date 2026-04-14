import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { supabase } from '../lib/supabase'

export default function Dashboard() {
    const { user, signOut } = useAuth()
    const [formData, setFormData] = useState({
        title: '',
        company: '',
        description: '',
        requirements: '',
        benefits: ''
    })
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value })
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError(null)
        setResult(null)

        try {
            // Get token from session
            const { data } = await supabase.auth.getSession()
            const token = data.session?.access_token || 'mock_token'

            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(formData)
            })

            console.log('Response status:', response.status)
            console.log('Response headers:', response.headers)

            if (!response.ok) {
                const errorText = await response.text()
                console.error('Error response:', errorText)
                throw new Error(`API Error ${response.status}: ${errorText}`)
            }

            const data_response = await response.json()
            console.log('Prediction result:', data_response)
            setResult(data_response)
        } catch (err) {
            console.error('Prediction error:', err)
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="dashboard-container">
            <div className="dashboard-inner">
                <header className="dashboard-header">
                    <h2>Job Validator</h2>
                    <div className="user-info">
                        <span className="user-email">{user.email}</span>
                        <button onClick={() => signOut()} className="sign-out-btn">
                            Sign Out
                        </button>
                    </div>
                </header>

                <main>
                    <section className="check-job">
                        <h3 className="gradient-text">Analyze Job Post</h3>

                        <form onSubmit={handleSubmit}>
                            <div className="form-group">
                                <label>💼 Job Title</label>
                                <input
                                    name="title"
                                    placeholder="e.g. Senior Software Engineer"
                                    value={formData.title}
                                    onChange={handleChange}
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label>🏢 Company</label>
                                <input
                                    name="company"
                                    placeholder="e.g. Tech Corp Inc."
                                    value={formData.company}
                                    onChange={handleChange}
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label>📄 Job Description</label>
                                <textarea
                                    name="description"
                                    placeholder="Paste the full job description here..."
                                    value={formData.description}
                                    onChange={handleChange}
                                    required
                                    rows={8}
                                />
                            </div>

                            <div style={{ display: 'flex', justifyContent: 'center', marginTop: '1.5rem' }}>
                                <button type="submit" className="btn btn-primary" disabled={loading}>
                                    {loading ? (
                                        <>
                                            <span className="spinner"></span>
                                            Analyzing...
                                        </>
                                    ) : (
                                        '🔍 Check Validity'
                                    )}
                                </button>
                            </div>
                        </form>
                    </section>

                    {error && (
                        <div className="error-message" style={{ marginTop: '1.5rem' }}>
                            {error}
                        </div>
                    )}

                    {result && (
                        <section className="result-section">
                            <div className={`result-card ${result.label.toLowerCase()}`}>
                                <p className="result-label">
                                    {result.label === 'Genuine' ? '✅' : '⚠️'} {result.label}
                                </p>
                                <p className="result-confidence">
                                    {(result.confidence * 100).toFixed(0)}%
                                </p>
                                <p className="result-sublabel">Confidence Score</p>
                                {result.details && (
                                    <p className="result-details">{result.details}</p>
                                )}
                            </div>
                        </section>
                    )}
                </main>
            </div>
        </div>
    )
}
