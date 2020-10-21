import React from 'react';
import './App.css';
import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';
import 'bootstrap/dist/css/bootstrap.min.css';
import Login from "./component/Login";
import Setting from "./component/Setting";
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

    this.setLoggedInUser = this.setLoggedInUser.bind(this);
    this.setAuthenticationStatus = this.setAuthenticationStatus.bind(this);
    this.onLogoutLinkClick = this.onLogoutLinkClick.bind(this);

    this.state = {
      loggedInUser: '',
      isAuthenticated: getBackend().isAuthenticated()
    };
  }

  setAuthenticationStatus(isAuthenticated) {
    console.info('setAuthenticationStatus: isAuthenticated: %o', isAuthenticated)
    this.setState({isAuthenticated: isAuthenticated});
  }

  setLoggedInUser(loggedInUser) {
    this.setState({loggedInUser: loggedInUser});
  }

  onLogoutLinkClick() {
    console.info('onLogoutLinkClick: Logging out')
    getBackend().clearAuthentication();
  }

  render() {
    const authProps= {
        isAuthenticated: this.state.isAuthenticated,
        loggedInUser: this.state.loggedInUser,
        setAuthenticationStatus: this.setAuthenticationStatus,
        setLoggedInUser: this.setLoggedInUser,
    };

    console.info('App::render(): authProps: %o', authProps)
    return (
        <Router>
            <div className="App">
                <Navbar bg="dark" variant="dark">
                    <Navbar.Brand href="/home">
                        Brino
                    </Navbar.Brand>
                    <Navbar.Collapse className="justify-content-end">
                        <Navbar.Text>
                            <Nav.Link href="/setting">Setting</Nav.Link>
                        </Navbar.Text>
                        <Navbar.Text>
                            <Nav.Link href="/login" onClick={this.onLogoutLinkClick}>Logout</Nav.Link>
                        </Navbar.Text>
                    </Navbar.Collapse>
                </Navbar>

                <Switch>
                    <Route exact path="/home">
                        <Home auth={ authProps } />
                    </Route>
                    <Route path="/login">
                        <Login auth={ authProps } />
                    </Route>
                    <Route path="/setting">
                        <Setting auth={ authProps } />
                    </Route>
                </Switch>
            </div>
       </Router>
      );
    }
}
