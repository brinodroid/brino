import React from 'react';
import './App.css';
import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';
import 'bootstrap/dist/css/bootstrap.min.css';
import Login from "./component/Login";
import Setting from "./component/Setting";
import NotFound from "./component/NotFound";
import Home from "./component/Home";
import WatchList from "./component/WatchList";
import PortFolio from "./component/PortFolio";
import Scan from "./component/Scan";
import { getBackend } from './utils/Backend'
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";

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
          <Navbar style={{marginBottom: "20px"}} bg="dark" variant="dark">
            <Navbar.Brand href="/home">
              Brino
            </Navbar.Brand>
            <Navbar.Text>
              <Nav.Link href="/portfolio">Portfolio</Nav.Link>
            </Navbar.Text>
            <Navbar.Text>
              <Nav.Link href="/watchlist">Watch List</Nav.Link>
            </Navbar.Text>
            <Navbar.Text>
              <Nav.Link href="/scan">Scan</Nav.Link>
            </Navbar.Text>
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
            <Route exact path="/"> <Home auth={ authProps } /> </Route>
            <Route exact path="/home"> <Home auth={ authProps } /> </Route>
            <Route path="/login"> <Login auth={ authProps } /> </Route>
            <Route path="/portfolio"> <PortFolio auth={ authProps } /> </Route>
            <Route path="/watchlist"> <WatchList auth={ authProps } /> </Route>
            <Route path="/scan"> <Scan auth={ authProps } /> </Route>
            <Route path="/setting"> <Setting auth={ authProps } /> </Route>
            <Route> <NotFound auth={ authProps } /> </Route>
          </Switch>
        </div>
      </Router>
    );
  }
}
