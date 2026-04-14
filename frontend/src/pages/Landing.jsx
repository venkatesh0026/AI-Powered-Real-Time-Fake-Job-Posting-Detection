import { Link } from 'react-router-dom'

export default function Landing() {
    return (
        <div className="landing-container">
            {/* Animated Background */}
            <div className="landing-bg"></div>

            {/* Floating Orbs */}
            <div className="orb orb-1"></div>
            <div className="orb orb-2"></div>
            <div className="orb orb-3"></div>

            {/* Hero Section */}
            <header className="hero">
                <div className="hero-badge animate-in">
                    <span className="dot"></span>
                    AI-Powered Protection
                </div>

                <h1 className="animate-in animate-in-delay-1">
                    <span className="gradient-text">Fake Job Detector</span>
                </h1>

                <p className="animate-in animate-in-delay-2">
                    Protect your career from recruitment fraud with our advanced deep learning technology.
                    Get instant, accurate analysis of job postings.
                </p>

                <div className="cta-buttons animate-in animate-in-delay-3">
                    <Link to="/signup" className="btn btn-primary">
                        ✨ Start Analyzing
                    </Link>
                    <Link to="/login" className="btn btn-secondary">
                        Sign In
                    </Link>
                </div>
            </header>

            {/* Features Section */}
            <section className="features">
                <div className="features-grid">
                    <div className="feature glass-card animate-in animate-in-delay-1">
                        <div className="feature-icon">🤖</div>
                        <h3>AI Powered</h3>
                        <p>State-of-the-art NLP models trained on thousands of real and fake job postings for maximum accuracy.</p>
                    </div>

                    <div className="feature glass-card animate-in animate-in-delay-2">
                        <div className="feature-icon">⚡</div>
                        <h3>Instant Analysis</h3>
                        <p>Get results in milliseconds. Don't waste valuable time applying to fraudulent job postings.</p>
                    </div>

                    <div className="feature glass-card animate-in animate-in-delay-3">
                        <div className="feature-icon">🔒</div>
                        <h3>Private & Secure</h3>
                        <p>Your data is processed securely and never shared with third parties. Your privacy matters.</p>
                    </div>
                </div>
            </section>
        </div>
    )
}
