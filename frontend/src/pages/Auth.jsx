import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import '../index.css';
import './Auth.css';

// --- SVG ICONS ---
const UserIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
    <circle cx="12" cy="7" r="4" />
  </svg>
);

const EmailIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
    <polyline points="22,6 12,13 2,6" />
  </svg>
);

const PasswordIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
  </svg>
);

// Import Lucide icons
import { Bot, Zap, Shield, Users } from 'lucide-react';

const DatabaseIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <ellipse cx="12" cy="5" rx="9" ry="3" />
    <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
    <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
  </svg>
);

export default function Auth() {
  const location = useLocation();
  const navigate = useNavigate();
  const { login, signup } = useAuth();
  
  const [isSignup, setIsSignup] = useState(location.pathname === '/signup');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Login form state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  // Signup form state
  const [signupData, setSignupData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'buyer'
  });

  useEffect(() => {
    setIsSignup(location.pathname === '/signup');
    if (location.state?.message) {
      setSuccess(location.state.message);
    }
  }, [location]);

  const toggleMode = () => {
    setIsSignup(!isSignup);
    setError('');
    setSuccess('');
    navigate(isSignup ? '/login' : '/signup', { replace: true });
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const response = await login(email, password);
      setSuccess("Login successful! Redirecting...");

      if (response.user?.role === 'vendor' || response.user?.role === 'admin') {
        navigate('/vendor-dashboard');
      } else if (response.user?.role === 'buyer') {
        navigate('/buyer-dashboard');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      setError(err.message || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (signupData.password !== signupData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (signupData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);

    try {
      await signup(
        signupData.email,
        signupData.password,
        signupData.role,
        signupData.fullName || null
      );
      setSuccess('Account created successfully!');
      setTimeout(() => {
        setIsSignup(false);
        navigate('/login', { state: { message: 'Account created! Please sign in.' } });
      }, 1500);
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSignupChange = (e) => {
    setSignupData({
      ...signupData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="auth-split-container">
      {/* Left Side - Puddle Description */}
      <div className="auth-info-panel">
        <div className="auth-info-content">
          <div className="puddle-logo">
            <DatabaseIcon />
            <h1>Puddle</h1>
          </div>
          
          <h2 className="info-headline">The Intelligent Marketplace for Data</h2>
          
          <p className="info-description">
            Puddle connects data buyers and vendors through configurable AI agents, making data discovery faster, 
            more transparent, and more trustworthy.
          </p>

          <div className="info-features">
            <div className="feature-item">
              <div className="feature-icon">🤖</div>
              <div className="feature-content">
                <h3>AI-Powered Agents</h3>
                <p>Each vendor gets a custom AI agent that answers questions, explains datasets, and handles negotiations.</p>
              </div>
            </div>

            <div className="feature-item">
              <div className="feature-icon">⚡</div>
              <div className="feature-content">
                <h3>Fast Discovery</h3>
                <p>Search, compare, and interact with multiple data vendors through a unified conversational interface.</p>
              </div>
            </div>

            <div className="feature-item">
              <div className="feature-icon">🔒</div>
              <div className="feature-content">
                <h3>Verified & Traceable</h3>
                <p>Every dataset is linked to its verified source, ensuring credibility and preventing AI hallucinations.</p>
              </div>
            </div>

            <div className="feature-item">
              <div className="feature-icon">🎯</div>
              <div className="feature-content">
                <h3>Human + AI</h3>
                <p>AI handles routine queries while humans control sensitive decisions like pricing and contracts.</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Auth Forms */}
      <div className="auth-form-panel">
        <div className="auth-card">
          <div className="auth-header">
            <h1 className="auth-title">
              {isSignup ? 'Create Account' : 'Welcome to Puddle'}
            </h1>
            <p className="auth-subtitle">
              {isSignup ? 'Join Puddle marketplace' : 'Sign in to your account'}
            </p>
          </div>

          {success && <div className="alert success">{success}</div>}
          {error && <div className="alert error">{error}</div>}

          {/* Login Form */}
          {!isSignup && (
            <form onSubmit={handleLogin} className="auth-form">
              <div className="form-group">
                <div className="input-icon"><EmailIcon /></div>
                <label htmlFor="email">Email</label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  required
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <div className="input-icon"><PasswordIcon /></div>
                <label htmlFor="password">Password</label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  required
                  disabled={loading}
                />
              </div>

              <button type="submit" className="auth-button" disabled={loading}>
                {loading ? "Signing in..." : "Get Started"}
              </button>
            </form>
          )}

          {/* Signup Form */}
          {isSignup && (
            <form onSubmit={handleSignup} className="auth-form">
              <div className="form-group">
                <div className="input-icon"><UserIcon /></div>
                <label htmlFor="fullName">Full Name</label>
                <input
                  id="fullName"
                  name="fullName"
                  type="text"
                  value={signupData.fullName}
                  onChange={handleSignupChange}
                  placeholder="John Doe (Optional)"
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <div className="input-icon"><EmailIcon /></div>
                <label htmlFor="signupEmail">Email</label>
                <input
                  id="signupEmail"
                  name="email"
                  type="email"
                  value={signupData.email}
                  onChange={handleSignupChange}
                  placeholder="you@example.com"
                  required
                  disabled={loading}
                />
              </div>

              <div className="role-toggle-group">
                <div className="role-toggle-header">
                  <span className="role-question">Are you a vendor?</span>
                  <label className="toggle-wrapper" htmlFor="roleToggle">
                    <input
                      type="checkbox"
                      id="roleToggle"
                      name="role"
                      checked={signupData.role === 'vendor'}
                      onChange={(e) => setSignupData({
                        ...signupData,
                        role: e.target.checked ? 'vendor' : 'buyer'
                      })}
                      disabled={loading}
                      className="toggle-checkbox"
                    />
                    <span className="toggle-slider"></span>
                  </label>
                </div>
                <p className="role-description">
                  {signupData.role === 'vendor' 
                    ? 'You can sell data on Puddle' 
                    : 'You can browse and purchase data on Puddle'}
                </p>
              </div>

              <div className="form-group">
                <div className="input-icon"><PasswordIcon /></div>
                <label htmlFor="signupPassword">Password</label>
                <input
                  id="signupPassword"
                  name="password"
                  type="password"
                  value={signupData.password}
                  onChange={handleSignupChange}
                  placeholder="At least 6 characters"
                  required
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <div className="input-icon"><PasswordIcon /></div>
                <label htmlFor="confirmPassword">Confirm Password</label>
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  value={signupData.confirmPassword}
                  onChange={handleSignupChange}
                  placeholder="Confirm your password"
                  required
                  disabled={loading}
                />
              </div>

              <button type="submit" className="auth-button" disabled={loading}>
                {loading ? 'Creating account...' : 'Create Account'}
              </button>
            </form>
          )}

          <div className="auth-footer">
            <p>
              {isSignup ? 'Already have an account?' : "Don't have an account?"}{' '}
              <button onClick={toggleMode} className="auth-toggle-btn" disabled={loading}>
                {isSignup ? 'Sign in' : 'Sign up'}
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}