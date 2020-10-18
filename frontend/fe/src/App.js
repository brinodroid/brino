import React from 'react';
import './App.css';
import Navbar from 'react-bootstrap/Navbar';
import 'bootstrap/dist/css/bootstrap.min.css';
import Login from "./component/Login";
import Home from "./component/Home";

export default class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      authenticated: localStorage.getItem('token') ? true : false,
      username: ''
    };
  }

  componentDidMount() {
    if (this.state.authenticated) {
    }
  }

  render() {
    let homePage = <Home />;
    if (this.state.authenticated) {
        // If user is not authenticated, show Login page
        homePage = <Login />;
    }

    return (
        <div className="App">
            <Navbar bg="dark" variant="dark">
                <Navbar.Brand href="#home">
                Brino
            </Navbar.Brand>
          </Navbar>
          {homePage}
        </div>
      );
    }
}
