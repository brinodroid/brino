import React from 'react';
import { Redirect } from 'react-router-dom';
import { getBackend } from '../utils/backend'

export default class Home extends React.Component {
  constructor(props) {
    super(props);
  }

  componentDidMount() {
    if ( this.props.auth.loggedInUser === '') {
        // Logged in user not set
        let getLoggedInUserCallback = function (httpStatus, username) {
            if ( httpStatus !== 200) {
                console.error("getLoggedInUserCallback: failure: http:%d", httpStatus);
                getBackend().clearAuthentication();
                this.props.auth.setLoggedInUser('');
                return;
            }

            console.info("getLoggedInUserCallback: success: http:%d username:%s", httpStatus, username);
            this.props.auth.setLoggedInUser(username);
        }

        getBackend().getLoggedInUser(getLoggedInUserCallback.bind(this));
    }
  }

  render() {
    if ( !this.props.auth.isAuthenticated ) {
        console.info('Home:  not authenticated, redirecting to login page');
        return <Redirect to= '/login' />;
    }

    return (
      <div className="home">
        Welcome home {this.props.auth.loggedInUser}
      </div>
    );
  }
}