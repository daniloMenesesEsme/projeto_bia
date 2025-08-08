import React, { useState } from 'react';
import Login from './Login';
import Chat from './Chat';
import './App.css';

function App() {
  const [auth, setAuth] = useState({ username: null, token: null });

  const handleLogin = (username, token) => {
    setAuth({ username, token });
  };

  return (
    <div className="App">
      {auth.token ? (
        <Chat username={auth.username} token={auth.token} />
      ) : (
        <Login onLogin={handleLogin} />
      )}
    </div>
  );
}

export default App;
