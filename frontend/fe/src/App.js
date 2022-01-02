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
import Strategy from "./component/Strategy";
import PortFolio from "./component/PortFolio";
import Orders from "./component/Orders";
import BGTask from "./component/BGTask";
import watchlistCache from './utils/WatchListCache';
import { getBackend } from './utils/Backend'
import { HashRouter as Router, Switch, Route } from "react-router-dom";

export default class App extends React.Component {
  constructor(props) {
    super(props);

    this.setLoggedInUser = this.setLoggedInUser.bind(this);
    this.updateWatchListCacheCallback = this.updateWatchListCacheCallback.bind(this);

    this.setAuthenticationStatus = this.setAuthenticationStatus.bind(this);
    this.onLogoutLinkClick = this.onLogoutLinkClick.bind(this);

    this.state = {
      loggedInUser: '',
      isAuthenticated: getBackend().isAuthenticated(),
      watchListCache: null
    };
  }

  updateWatchListCacheCallback(httpStatus, json) {
    console.info('updateWatchListCacheCallback: httpStatus:%o', httpStatus)

    if (httpStatus === 401) {
      console.info('updateWatchListCacheCallback: authentication failure :%o', json)

      this.setAuthenticationStatus(false);
      return;
    }


    if (httpStatus === 200) {
      this.setState({
        watchListCache: watchlistCache,
      });
    }

  }

  componentDidMount() {
    console.info('componentDidMount..');

    if (this.state.isAuthenticated) {
      // Load the watchlist cache
      watchlistCache.loadWatchList(this.updateWatchListCacheCallback);
    }
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
            <Navbar.Brand href="/#home">
              Brino
            </Navbar.Brand>
            <Navbar.Text>
              <Nav.Link href="/#orders">Orders</Nav.Link>
            </Navbar.Text>
            <Navbar.Text>
              <Nav.Link href="/#strategy">Strategy</Nav.Link>
            </Navbar.Text>
            <Navbar.Text>
              <Nav.Link href="/#portfolio">Portfolio</Nav.Link>
            </Navbar.Text>
            <Navbar.Text>
              <Nav.Link href="/#watchlist">Watch List</Nav.Link>
            </Navbar.Text>
            <Navbar.Text>
              <Nav.Link href="/bgtask">BGTask</Nav.Link>
            </Navbar.Text>
            <Navbar.Collapse className="justify-content-end">
              <Navbar.Text>
                <Nav.Link href="/#setting">Setting</Nav.Link>
              </Navbar.Text>
              <Navbar.Text>
                <Nav.Link href="/#login" onClick={this.onLogoutLinkClick}>Logout</Nav.Link>
              </Navbar.Text>
            </Navbar.Collapse>
          </Navbar>

          <Switch>
            <Route path="/home"> <Home auth={ authProps } watchListCache={this.state.watchListCache}/> </Route>
            <Route path="/login"> <Login auth={ authProps } /> </Route>
            <Route path="/orders"> <Orders auth={ authProps } watchListCache={this.state.watchListCache} /> </Route>
            <Route path="/strategy"> <Strategy auth={ authProps } watchListCache={this.state.watchListCache}/> </Route>
            <Route path="/portfolio"> <PortFolio auth={ authProps } watchListCache={this.state.watchListCache}/> </Route>
            <Route path="/watchlist"> <WatchList auth={ authProps } watchListCache={this.state.watchListCache}/> </Route>
            <Route path="/bgtask"> <BGTask auth={ authProps } /> </Route>
            <Route path="/setting"> <Setting auth={ authProps } /> </Route>
            <Route exact path="/"> <Home auth={ authProps } watchListCache={this.state.watchListCache}/> </Route>
            <Route> <NotFound auth={ authProps } /> </Route>
          </Switch>
        </div>
      </Router>
    );
  }
}
