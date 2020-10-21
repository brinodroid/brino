import React from 'react';
import { Redirect } from 'react-router-dom';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import Alert from 'react-bootstrap/Alert';
import './Login.css';
import { getBackend } from '../utils/backend'

export default class Login extends React.Component {
  constructor(props) {
    super(props);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.showErrorMsg = this.showErrorMsg.bind(this);

    this.state = {
        username: "",
        password: "",
        errorMsg: ""
    }
  }

  handleSubmit(event) {
    event.preventDefault();
    let authenticateCallback = function (httpStatus) {
        if ( httpStatus !== 200) {
            this.props.auth.setAuthenticationStatus(false);
            console.error("Login: authentication failure: http:", httpStatus);
            this.setState({
                errorMsg: "Login credentials invalid"
            })
            return;
        }

        // Login successful
        this.props.auth.setAuthenticationStatus(true);
    }

    getBackend().authenticate(this.state.username, this.state.password, authenticateCallback.bind(this));
  }

  handleChange(event) {
    this.setState({[event.target.id]: event.target.value})
  }

  showErrorMsg() {
    if (this.state.errorMsg !== "") {
        return <Alert variant={'danger'} > {this.state.errorMsg} </Alert>
    }
  }

  render() {
    if ( this.props.auth.isAuthenticated ) {
        console.info('Login: authenticated, redirecting to home page');
        return <Redirect to= '/home' />;
    }

    return (
      <div className="login">
        { this.showErrorMsg() }
        <Form onSubmit={this.handleSubmit} >

            <Form.Group controlId="username">
                <Form.Label>User Name</Form.Label>
                <Form.Control type="username"
                    value={this.state.username}
                    onChange={this.handleChange}
                    placeholder="User Name" />
            </Form.Group>

            <Form.Group controlId="password">
                <Form.Label>Password</Form.Label>
                <Form.Control type="password"
                    value={this.state.password}
                    onChange={this.handleChange}
                    placeholder="Password" />
            </Form.Group>
            <Button variant="primary" type="submit">
                Submit
           </Button>
        </Form>
      </div>
    );
  }
}