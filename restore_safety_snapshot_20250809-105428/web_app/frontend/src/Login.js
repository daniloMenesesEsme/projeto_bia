import React, { useState } from 'react';
import './Login.css';

function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  
  // Usa o mesmo domínio do frontend por padrão; Vercel fará o proxy via vercel.json
  const API_BASE_URL = process.env.REACT_APP_API_URL || '';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      
      const data = await response.json();

      if (response.ok && data.token) {
        onLogin(username, data.token);
      } else {
        setError(data.message || 'Usuário ou senha inválidos.');
      }
    } catch (error) {
      console.error("Erro de conexão ao autenticar:", error);
      setError('Não foi possível conectar ao servidor. Verifique sua conexão.');
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
        <button type="submit">Entrar</button>
      </form>
    </div>
  );
}

export default Login;
