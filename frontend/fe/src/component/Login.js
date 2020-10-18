import React from 'react';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import './Login.css';
import {getBackend} from '../utils/backend'

export default class Login extends React.Component {
  constructor(props) {
    super(props);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleChange = this.handleChange.bind(this);

    this.state = {
        username: "",
        password: ""
    }
  }

  handleSubmit(event) {
    event.preventDefault();
    let authenticateCallback = function (httpStatus) {
        console.error("authenticationCallback: %d", httpStatus);
    }

    getBackend().authenticate(this.state.username, this.state.password, authenticateCallback);
  }

  handleChange(event) {
    this.setState({[event.target.id]: event.target.value})
  }

  render() {
    return (
      <div className="login">
        <Form onSubmit={this.handleSubmit}>

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