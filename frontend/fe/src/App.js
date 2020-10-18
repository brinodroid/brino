import React from 'react';
import './App.css';
import Navbar from 'react-bootstrap/Navbar';
import 'bootstrap/dist/css/bootstrap.min.css';
import Login from "./component/Login";

export default class App extends React.Component {
  render() {
    return (
        <div className="App">
            <Navbar bg="dark" variant="dark">
                <Navbar.Brand href="#home">
                Brino
            </Navbar.Brand>
          </Navbar>
          <Login />
        </div>
      );
    }
}
