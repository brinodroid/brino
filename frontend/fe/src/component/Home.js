import React from 'react';
import { Redirect } from 'react-router-dom';
import Alert from 'react-bootstrap/Alert';
import Button from 'react-bootstrap/Button';
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import ButtonToolbar from 'react-bootstrap/ButtonToolbar';
import Modal from 'react-bootstrap/Modal';
import Form from 'react-bootstrap/Form';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

import { getBackend } from '../utils/Backend';
import Table from '../utils/Table';

export default class Home extends React.Component {
  constructor(props) {
    super(props);

    this.onEditButtonClick = this.onEditButtonClick.bind(this);
    this.onDeleteButtonClick = this.onDeleteButtonClick.bind(this);
    this.onAddButtonClick = this.onAddButtonClick.bind(this);

    this.loadBgtask = this.loadBgtask.bind(this);
    this.createBgtask = this.createBgtask.bind(this);
    this.deleteBgtask = this.deleteBgtask.bind(this);
    this.updateBgtask = this.updateBgtask.bind(this);

    this.onCloseDetailedViewModal = this.onCloseDetailedViewModal.bind(this);
    this.onModalActionButtonClick = this.onModalActionButtonClick.bind(this);
    this.showModalActionButton = this.showModalActionButton.bind(this);
    this.showErrorMsg = this.showErrorMsg.bind(this);
    this.showModal = this.showModal.bind(this);
    this.showModalForm = this.showModalForm.bind(this);
    this.showModalFormGroup = this.showModalFormGroup.bind(this);
    this.onFormValuesChange = this.onFormValuesChange.bind(this);

    this.state = {
      isBgtaskLoaded: false,
      bgtaskList : null,
      errorMsg : '',
      showDetailedViewModal: false,
      createBgtask: false,
      deleteBgtask: false,
      formValues : {id: "", dataIdType: "", dataId: "", status: "", action: "", actionResult: "", updateTimestamp: "", detials: ""}
    }
  }

  onCloseDetailedViewModal() {
    console.info('onCloseDetailedViewModal: ...')
    this.setState({
      showDetailedViewModal: false,
      deleteBgtask: false,
      createBgtask: false,
      formValues : {id: "", dataIdType: "", dataId: "", status: "", action: "", actionResult: "", updateTimestamp: ""}
    });
  }

  onEditButtonClick (rowData) {
    console.info('onEditButtonClick: rowData=%o', rowData);
    this.setState({
      showDetailedViewModal: true,
      formValues: rowData
    });
  }

  onAddButtonClick() {
    console.info('onAddButtonClick: ...')
    this.setState({
      showDetailedViewModal: true,
      createBgtask: true
    });
  }

  onDeleteButtonClick(rowData) {
    console.info('onDeleteButtonClick: rowData=%o', rowData);
    this.setState({
      showDetailedViewModal: true,
      deleteBgtask: true,
      formValues: rowData
    });
  }

  showErrorMsg() {
    if (this.state.errorMsg !== "") {
      return <Alert variant={'danger'} > {this.state.errorMsg} </Alert>
    }
  }

  loadBgtask() {
    console.info('loadBgtask: Loading bgtask...')
    let loadBgtaskCallback = function (httpStatus, json) {
      if ( httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("loadBgtaskCallback: authentication expired?");
        return;
      }

      if ( httpStatus !== 200) {
        console.error("loadBgtaskCallback: failure: http:%o", httpStatus);
        this.setState({
          errorMsg: "Failed to load bgtask"
        })
        return;
      }

      console.info("loadBgtaskCallback: json: %o", json);
      this.setState({
        isBgtaskLoaded: true,
        bgtaskList : json,
        errorMsg: ""
      });
    }

    getBackend().getBgtask(loadBgtaskCallback.bind(this));
  }

  createBgtask(bgtask) {
    console.info('createBgtask: adding entry=%o', bgtask)
    let createBgtaskCallback = function (httpStatus, json) {
      if ( httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("createBgtaskCallback: authentication expired?");
        return;
      }

      if ( httpStatus !== 200) {
        console.error("createBgtaskCallback: failure: http:%o", httpStatus);
        this.setState({
          errorMsg: "Failed to create bgtask"
        })
        return;
      }

      console.info("createBgtaskCallback: json: %o", json);

      //Reloading the bgtaskList
      this.loadBgtask();
    }

    getBackend().createBgtask(bgtask, createBgtaskCallback.bind(this));
    this.onCloseDetailedViewModal();
  }

  updateBgtask(bgtask) {
    console.info('updateBgtask: adding entry=%o', bgtask)
    let updateBgtaskCallback= function (httpStatus, json) {
      if ( httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("updateBgtaskCallback: authentication expired?");
        return;
      }

      if ( httpStatus !== 200) {
        console.error("updateBgtaskCallback: failure: http:%o", httpStatus);
        this.setState({
          errorMsg: "Failed to update bgtask"
        })
        return;
      }

      console.info("updateBgtaskCallback: json: %o", json);

      //Reloading the bgtaskList
      this.loadBgtask();
    }

    getBackend().updateBgtask(bgtask, updateBgtaskCallback.bind(this));
    this.onCloseDetailedViewModal();
  }

  deleteBgtask(bgtask) {
    console.info('deleteBgtask: adding entry=%o', bgtask)
    let deleteBgtaskCallback = function (httpStatus, json) {
      if ( httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("deleteBgtaskCallback: authentication expired?");
        return;
      }

      if ( httpStatus !== 204) {
        console.error("deleteBgtaskCallback: failure: http:%o", httpStatus);
        this.setState({
          errorMsg: "Failed to delete to bgtask"
        })
        return;
      }

      console.info("deleteBgtaskCallback: json: %o", json);

      //Reloading the bgtaskList
      this.loadBgtask();
    }

    getBackend().deleteBgtask(bgtask, deleteBgtaskCallback.bind(this));
    this.onCloseDetailedViewModal();
  }

  componentDidMount() {
    console.info('componentDidMount..');
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

    if (!this.state.isBgtaskLoaded) {
      this.loadBgtask();
    }
  }

  onFormValuesChange(event) {
    let updatedFormValues = {...this.state.formValues, [event.target.id]: event.target.value};
    console.info('onFormValuesChange: updatedFormValues=%o ', updatedFormValues);
    this.setState({formValues: updatedFormValues});
  }

  showModalFormGroup(readOnly, controlId, label, value) {
    return (
      <Form.Group as={Row} controlId={controlId}>
        <Form.Label column sm="4"> {label} </Form.Label>
        <Col sm="8">
          <Form.Control readOnly={readOnly} value={value} onChange={this.onFormValuesChange} />
        </Col>
      </Form.Group>
    );
  }

  showModalForm() {
    /*if (!this.state.formValues) {
      return <Alert variant={'danger'} > No row selected? </Alert>
    }*/
    let readOnly = false;
    if (this.state.deleteBgtask) readOnly = true;
    console.info('showModalForm: formValues=%o', this.state.formValues);

    return (
      <Form onSubmit={this.handleSubmit} >

        { this.showModalFormGroup(true, "updateTimestamp", "Update Timestamp", this.state.formValues.updateTimestamp) }
        { this.showModalFormGroup(true, "id", "ID", this.state.formValues.id) }
        { this.showModalFormGroup(readOnly, "dataIdType", "Type", this.state.formValues.dataIdType) }
        { this.showModalFormGroup(readOnly, "dataId", "Data Id", this.state.formValues.dataId) }
        { this.showModalFormGroup(readOnly, "action", "Action", this.state.formValues.action) }
        { this.showModalFormGroup(true, "actionResult", "Action Status", this.state.formValues.actionResult) }
        { this.showModalFormGroup(true, "status", "Status", this.state.formValues.status) }

      </Form>
    );
  }

  onModalActionButtonClick() {
    console.info('onModalActionButtonClick: formValues=%o', this.state.formValues);
    let formValues = this.state.formValues;
    // TODO: Validate data. Temporarily setting it to null, needed for add to succeed
    formValues.optionExpiry = null;
    formValues.optionStrike = null;

    if (this.state.createBgtask) {
      console.info('onModalActionButtonClick: call add');
      this.createBgtask(this.state.formValues);
      return;
    }

    if (this.state.deleteBgtask) {
      console.info('onModalActionButtonClick: call delete');
      this.deleteBgtask(this.state.formValues);
      return;
    }

    console.info('onModalActionButtonClick: call update');
    this.updateBgtask(this.state.formValues);
  }

  showModalActionButton() {
    if (this.state.createBgtask)
      return (
        <Button variant="primary" onClick={this.onModalActionButtonClick}>
          Add
        </Button>
      );

    if (this.state.deleteBgtask) {
      return (
        <Button variant="primary" onClick={this.onModalActionButtonClick}>
          Delete
        </Button>
      );
    }

    return (
      <Button variant="primary" onClick={this.onModalActionButtonClick}>
        Update
      </Button>
    );
  }

  showModal() {
    /* animation=false added due to warning in console: https://github.com/react-bootstrap/react-bootstrap/issues/5075 */
    return (
        <Modal show={this.state.showDetailedViewModal} onHide={this.onCloseDetailedViewModal} animation={false}>
        <Modal.Header closeButton>
          <Modal.Title>Watch List Details</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {this.showModalForm()}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={this.onCloseDetailedViewModal}>
            Close
          </Button>
          {this.showModalActionButton()}
        </Modal.Footer>
      </Modal>
    );
  }

  render() {
    if ( !this.props.auth.isAuthenticated ) {
      console.info('Home:  not authenticated, redirecting to login page');
      return <Redirect to= '/login' />;
    }

    if ( !this.state.isBgtaskLoaded) {
      return <Alert variant="primary"> Loading bgtask... </Alert>;
    }

    console.info('render: this.showDetailedViewModal=%o...', this.state.showDetailedViewModal)

    const columns = [
      { Header: 'ID',  accessor: 'id',
          Cell: ({row}) => (
              <ButtonGroup className="mr-2" aria-label="First group">
                <Button onClick={ (e) => this.onEditButtonClick(row.original) }>Edit</Button>
                <Button onClick={ (e) => this.onDeleteButtonClick(row.original) }>Delete</Button>
              </ButtonGroup>
            )},
      { Header: 'Type', accessor: 'dataIdType'},
      { Header: 'Data Id', accessor: 'dataId'},
      { Header: 'Status', accessor: 'status'},
      { Header: 'Action', accessor: 'action'},
      { Header: 'Result', accessor: 'actionResult'},
      { Header: 'Details', accessor: 'details'},
      { Header: 'Update Time', accessor: 'updateTimestamp'},
    ];

    const onRowClick = (state, rowInfo, column, instance) => {
    return {
        onClick: e => {
            console.log('A Td Element was clicked!')
            console.log('it produced this event:', e)
            console.log('It was in this column:', column)
            console.log('It was in this row:', rowInfo)
            console.log('It was in this table instance:', instance)
        }
    }
    }

    return (
      <div className="home">

        <ButtonToolbar aria-label="Toolbar with button groups">
          <ButtonGroup className="mr-2" aria-label="First group">
            <Button onClick={this.onAddButtonClick}> Add </Button>
          </ButtonGroup>
          <ButtonGroup className="mr-2" aria-label="Second group">
            <Button onClick={this.loadBgtask}> Refresh </Button>
          </ButtonGroup>
        </ButtonToolbar>
        Welcome home {this.props.auth.loggedInUser}
        { this.showErrorMsg() }

        <Table columns={columns} data={this.state.bgtaskList} getTrProps={onRowClick} />

        { this.showModal() }

      </div>
    );
  }
}

