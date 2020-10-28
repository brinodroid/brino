import React from 'react';
import { Redirect } from 'react-router-dom';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import Alert from 'react-bootstrap/Alert';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
import { getBackend } from '../utils/Backend'

export default class Setting extends React.Component {
  constructor(props) {
    super(props);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.showErrorMsg = this.showErrorMsg.bind(this);

    this.state = {
        creationTimestamp: null,
        updateTimestamp: null,
        profitTargetPercent: 0,
        stopLossPercent: 0,
        isConfigurationLoaded: false
    }
  }

  componentDidMount() {
    if (!this.state.isConfigurationLoaded) {
        console.info('Loading data...')
        let configurationCallback = function (httpStatus, json) {
            if ( httpStatus === 401) {
                this.props.auth.setAuthenticationStatus(false);
                console.error("configurationCallback: authentication expired?");
                return;
            }

            if ( httpStatus !== 200) {
                console.error("configurationCallback: authentication failure: http:%o", httpStatus);
                this.setState({
                    errorMsg: "Failed to load configuration"
                })
                return;
            }

            console.error("configurationCallback: json: %o", json);
            this.setState({
                isConfigurationLoaded: true,
                creationTimestamp: json.creationTimestamp,
                updateTimestamp: json.updateTimestamp,
                profitTargetPercent: json.profitTargetPercent,
                stopLossPercent: json.stopLossPercent
            });
       }

       getBackend().getConfiguration(configurationCallback.bind(this));
    }
  }

  handleSubmit(event) {
    event.preventDefault();
    console.error("Handle update");
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

    if ( !this.state.isConfigurationLoaded ) {
        return <Alert variant="primary"> Loading settings.. </Alert>;
    }

    return (
      <div className="setting">
      <Form>
          <Form.Group as={Row} controlId="profitTargetPercent">
            <Form.Label column sm="2">
              Profit Target Percent
            </Form.Label>
            <Col sm="2">
              <Form.Control value={this.state.profitTargetPercent} onChange={this.handleChange}/>
            </Col>
          </Form.Group>

          <Form.Group as={Row} controlId="stopLossPercent">
            <Form.Label column sm="2">
              Stop Loss Percent
            </Form.Label>
            <Col sm="2">
              <Form.Control value={this.state.stopLossPercent} onChange={this.handleChange}/>
            </Col>
          </Form.Group>
          <Form.Group as={Row}>
            <Col sm={{ span: 2, offset: 2 }}>
                <Button variant="primary" type="submit">
                   Update
                </Button>
            </Col>
          </Form.Group>
        </Form>
      </div>
    );
  }
}

