import React from 'react';
import './App.css';
import Navbar from 'react-bootstrap/Navbar';
import 'bootstrap/dist/css/bootstrap.min.css';
import Login from "./component/Login";
import Home from "./component/Home";
import { getBackend } from './utils/backend'

export default class App extends React.Component {
  constructor(props) {
    super(props);

    this.setAuthenticationStatus = this.setAuthenticationStatus.bind(this);

    this.state = {
      authenticated: false,
      username: ''
    };
  }

  componentDidMount() {
    if ( getBackend().isAuthenticated()) {
        this.setAuthenticationStatus(true);
    }
  }

  setAuthenticationStatus(authenticated) {
    this.setState({authenticated: authenticated});
  }

  render() {
    let homePage = <Home />;
    if (!this.state.authenticated) {
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
