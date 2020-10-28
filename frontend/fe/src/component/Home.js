import React from 'react';
import { Redirect } from 'react-router-dom';
import Alert from 'react-bootstrap/Alert';
import Button from 'react-bootstrap/Button';

import { getBackend } from '../utils/Backend';
import Table from '../utils/Table';

export default class Home extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      isWatchListLoaded: false,
      errorMsg : '',
      watchList : null
    }
  }

  componentDidMount() {
    if ( this.props.auth.loggedInUser === '') {
      // Logged in user not set
      let getLoggedInUserCallback = function (httpStatus, json) {
        if ( httpStatus !== 200) {
          console.error("getLoggedInUserCallback: failure: http:%d", httpStatus);
          getBackend().clearAuthentication();
          this.props.auth.setLoggedInUser('');
          return;
        }

        console.info("getLoggedInUserCallback: success: http:%d json:%o", httpStatus, json);
        this.props.auth.setLoggedInUser(json.username);
      }

      getBackend().getLoggedInUser(getLoggedInUserCallback.bind(this));
    }

    if (!this.state.isWatchListLoaded) {
      console.info('Loading watchlist...')
      let watchListCallback = function (httpStatus, json) {
        if ( httpStatus === 401) {
          this.props.auth.setAuthenticationStatus(false);
          console.error("watchListCallback: authentication expired?");
          return;
        }

        if ( httpStatus !== 200) {
          console.error("watchListCallback: failure: http:%o", httpStatus);
          this.setState({
            errorMsg: "Failed to load watchlist"
          })
          return;
        }

        console.error("watchListCallback: json: %o", json);
        this.setState({
          isWatchListLoaded: true,
          watchList: json,
          errorMsg: ""
        });
      }

      getBackend().getWatchList(watchListCallback.bind(this));
    }
  }

  render() {
    if ( !this.props.auth.isAuthenticated ) {
      console.info('Home:  not authenticated, redirecting to login page');
      return <Redirect to= '/login' />;
    }

    if ( !this.state.isWatchListLoaded) {
      return <Alert variant="primary"> Loading watchlist... </Alert>;
    }

    // TODO: 
    // 1. Show error
    // 2. Refresh button

    const columns = [
      { Header: 'ID',  accessor: 'id'},
      { Header: 'Asset Type', accessor: 'assetType'},
      { Header: 'Ticker', accessor: 'ticker'},
      { Header: 'Strike', accessor: 'optionStrike'},
      { Header: 'Expiry', accessor: 'optionExpiry'},
      { Header: 'Comment', accessor: 'comment'},
      { Header: 'Update Time', accessor: 'updateTimestamp'},
      { Header: 'Create Time', accessor: 'creationTimestamp'},
    ];

    return (
      <div className="home">
        Welcome home {this.props.auth.loggedInUser}
        <Table columns={columns} data={this.state.watchList} />
        <Button variant="primary"> Update </Button>
      </div>
    );
  }
}

