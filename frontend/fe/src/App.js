import React from 'react';
import './App.css';
import Navbar from 'react-bootstrap/Navbar';
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  return (
    <div className="App">
        <Navbar bg="dark" variant="dark">
            <Navbar.Brand href="#home">
            Brino
        </Navbar.Brand>
      </Navbar>
    </div>
  );
}

export default App;
