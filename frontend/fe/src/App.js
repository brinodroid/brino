import React from 'react';
import './App.css';
import Navbar from 'react-bootstrap/Navbar';
import 'bootstrap/dist/css/bootstrap.min.css';
import Login from "./component/Login";
import Home from "./component/Home";
import { getBackend } from './utils/backend'
import {
  BrowserRouter as Router,
  Switch,
  Route
} from "react-router-dom";

export default class App extends React.Component {
  constructor(props) {
    super(props);

    this.setAuthenticationStatus = this.setAuthenticationStatus.bind(this);

    this.state = {
      isAuthenticated: false,
      username: ''
    };
  }

  componentDidMount() {
    if ( getBackend().isAuthenticated()) {
        this.setAuthenticationStatus(true);
    }
  }

  setAuthenticationStatus(isAuthenticated) {
    this.setState({isAuthenticated: isAuthenticated});
  }

  render() {
    const authProps= {
        isAuthenticated: this.state.isAuthenticated,
        setAuthenticationStatus: this.setAuthenticationStatus
    };

    return (
        <Router>
            <div className="App">
                <Navbar bg="dark" variant="dark">
                    <Navbar.Brand href="#home">
                    Brino
                </Navbar.Brand>
                </Navbar>

                <Switch>
                    <Route exact path="/">
                        <Home auth={ authProps } />
                    </Route>
                    <Route path="/login">
                        <Login auth={ authProps } />
                    </Route>
                </Switch>
            </div>
       </Router>
      );
    }
}
