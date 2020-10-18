import React from 'react';
import { Redirect } from 'react-router-dom';

export default class Home extends React.Component {
  render() {
    if ( !this.props.auth.isAuthenticated ) {
        console.info('Home:  not authenticated, redirecting to login page');
        return <Redirect to= '/login' />;
    }

    return (
      <div className="home">
        Welcome to home
      </div>
    );
  }
}