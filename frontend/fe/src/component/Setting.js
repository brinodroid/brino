import React from 'react';
import { Redirect } from 'react-router-dom';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import Alert from 'react-bootstrap/Alert';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
import { getBackend } from '../utils/backend'

export default class Setting extends React.Component {
  constructor(props) {
    super(props);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.showErrorMsg = this.showErrorMsg.bind(this);

    this.state = {
        username: "",
        password: "",
        errorMsg: "",
        authenticated: false
    }
  }

  handleSubmit(event) {
    event.preventDefault();
    let authenticateCallback = function (httpStatus) {
        if ( httpStatus !== 200) {
            console.error("Setting: authentication failure: http:", httpStatus);
            this.setState({
                errorMsg: "Setting credentials invalid"
            })
            return;
        }

        console.info("Setting: redirecting to home");
        this.setState({authenticated:true})
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
    if ( !this.props.auth.isAuthenticated ) {
        console.info('Setting: authenticated, redirecting to home page');
        return <Redirect to= '/login' />;
    }

    return (
      <div className="setting">
      <Form>
          <Form.Group as={Row} controlId="formPlaintextPassword">
            <Form.Label column sm="2">
              Password
            </Form.Label>
            <Col sm="2">
              <Form.Control placeholder="Password" />
            </Col>
          </Form.Group>
        </Form>
      </div>
    );
  }
}