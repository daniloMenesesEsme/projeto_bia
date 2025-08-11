import React, { useState } from 'react';
import { API_BASE_URL } from './config';
import './Login.css';

function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 segundos timeout
      
      const response = await fetch(`${API_BASE_URL}/api/auth`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        onLogin(username);
      } else {
        setError('Usuário ou senha inválidos.');
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        setError('Timeout: Servidor demorou para responder. Tente novamente.');
      } else {
        // Fallback para desenvolvimento (remover em produção)
        if (username === 'admin' && password === 'boticario2024') {
          onLogin(username);
        } else {
          setError('Erro de conexão. Verifique sua internet.');
        }
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <form onSubmit={handleSubmit} className="login-form">
        <div className="logo-container">
          <img 
            className="logo" 
            src="/logo-boticario.png" 
            alt="Grupo Boticário" 
            width="80" 
            height="80"
            onError={(e) => {
              // Fallback se não encontrar o PNG
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'block';
            }}
          />
          <div className="logo-fallback" style={{display: 'none', fontSize: '60px'}}>🏪</div>
          <h2>Grupo Boticário</h2>
        </div>
        <p style={{color: '#718096', marginBottom: '32px', fontSize: '1.1em'}}>
          Assistente Virtual para Suporte
        </p>
        {error && <p className="error-message">{error}</p>}
        <div className="form-group">
          <label htmlFor="username">Usuário:</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Senha:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit" disabled={isLoading}>
          {isLoading ? (
            <>
              <span style={{marginRight: '8px'}}>🔄</span>
              Conectando... (pode demorar 30s)
            </>
          ) : (
            'Entrar'
          )}
        </button>
      </form>
    </div>
  );
}

export default Login;