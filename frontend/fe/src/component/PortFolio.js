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

export default class PortFolio extends React.Component {
  constructor(props) {
    super(props);

    this.onEditButtonClick = this.onEditButtonClick.bind(this);
    this.onDeleteButtonClick = this.onDeleteButtonClick.bind(this);
    this.onAddButtonClick = this.onAddButtonClick.bind(this);

    this.loadPortFolio = this.loadPortFolio.bind(this);
    this.addToPortFolio = this.addToPortFolio.bind(this);
    this.deleteFromPortFolio = this.deleteFromPortFolio.bind(this);
    this.updatePortFolio = this.updatePortFolio.bind(this);

    this.onCloseDetailedViewModal = this.onCloseDetailedViewModal.bind(this);
    this.onModalActionButtonClick = this.onModalActionButtonClick.bind(this);
    this.showModalActionButton = this.showModalActionButton.bind(this);
    this.showErrorMsg = this.showErrorMsg.bind(this);
    this.showModal = this.showModal.bind(this);
    this.showModalForm = this.showModalForm.bind(this);
    this.showModalFormGroup = this.showModalFormGroup.bind(this);
    this.onFormValuesChange = this.onFormValuesChange.bind(this);

    this.state = {
      isPortFolioLoaded: false,
      errorMsg : '',
      PortFolio : null,
      showDetailedViewModal: false,
      addToPortFolio: false,
      deleteFromPortFolio: false,
      formValues : {id: "", update_timestamp: "", watchlist_id: "", source:"", transaction_type:"", entry_datetime: "", entry_price: "", units: "", exit_price: "", exit_datetime: ""}
    }
  }

  onCloseDetailedViewModal() {
    console.info('onCloseDetailedViewModal: ...')
    this.setState({
      showDetailedViewModal: false,
      deleteFromPortFolio: false,
      addToPortFolio: false,
      formValues : {id: "", update_timestamp: "", watchlist_id: "", source:"", transaction_type:"", entry_datetime: "", entry_price: "", units: "", exit_price: "", exit_datetime: ""}
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
      addToPortFolio: true
    });
  }

  onDeleteButtonClick(rowData) {
    console.info('onDeleteButtonClick: rowData=%o', rowData);
    this.setState({
      showDetailedViewModal: true,
      deleteFromPortFolio: true,
      formValues: rowData
    });
  }

  showErrorMsg() {
    if (this.state.errorMsg !== "") {
      return <Alert variant={'danger'} > {this.state.errorMsg} </Alert>
    }
  }

  loadPortFolio() {
    console.info('loadPortFolio: Loading PortFolio...')
    let loadPortFolioCallback = function (httpStatus, json) {
      if ( httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("loadPortFolioCallback: authentication expired?");
        return;
      }

      if ( httpStatus !== 200) {
        console.error("loadPortFolioCallback: failure: http:%o", httpStatus);
        this.setState({
          errorMsg: "Failed to load PortFolio"
        })
        return;
      }

      console.info("loadPortFolioCallback: json: %o", json);
      this.setState({
        isPortFolioLoaded: true,
        PortFolio: json,
        errorMsg: ""
      });
    }

    getBackend().getPortFolio(loadPortFolioCallback.bind(this));
  }

  addToPortFolio(PortFolioEntry) {
    console.info('addToPortFolio: adding entry=%o', PortFolioEntry)
    let createPortFolioCallback = function (httpStatus, json) {
      if ( httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("createPortFolioCallback: authentication expired?");
        return;
      }

      if ( httpStatus !== 200) {
        console.error("createPortFolioCallback: failure: http:%o", httpStatus);
        this.setState({
          errorMsg: "Failed to add to PortFolio"
        })
        return;
      }

      console.info("createPortFolioCallback: json: %o", json);

      //Reloading the PortFolio
      this.loadPortFolio();
    }

    getBackend().createPortFolio(PortFolioEntry, createPortFolioCallback.bind(this));
    this.onCloseDetailedViewModal();
  }

  updatePortFolio(PortFolioEntry) {
    console.info('updatePortFolio: adding entry=%o', PortFolioEntry)
    let updatePortFolioCallback= function (httpStatus, json) {
      if ( httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("updatePortFolioCallback: authentication expired?");
        return;
      }

      if ( httpStatus !== 200) {
        console.error("updatePortFolioCallback: failure: http:%o", httpStatus);
        this.setState({
          errorMsg: "Failed to update PortFolio"
        })
        return;
      }

      console.info("updatePortFolioCallback: json: %o", json);

      //Reloading the PortFolio
      this.loadPortFolio();
    }

    getBackend().updatePortFolio(PortFolioEntry, updatePortFolioCallback.bind(this));
    this.onCloseDetailedViewModal();
  }

  deleteFromPortFolio(PortFolioEntry) {
    console.info('deleteFromPortFolio: adding entry=%o', PortFolioEntry)
    let deleteFromPortFolioCallback = function (httpStatus, json) {
      if ( httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("deleteFromPortFolioCallback: authentication expired?");
        return;
      }

      if ( httpStatus !== 204) {
        console.error("deleteFromPortFolioCallback: failure: http:%o", httpStatus);
        this.setState({
          errorMsg: "Failed to delete to PortFolio"
        })
        return;
      }

      console.info("deleteFromPortFolioCallback: json: %o", json);

      //Reloading the PortFolio
      this.loadPortFolio();
    }

    getBackend().deletePortFolio(PortFolioEntry, deleteFromPortFolioCallback.bind(this));
    this.onCloseDetailedViewModal();
  }

  componentDidMount() {
    console.info('componentDidMount..');

    if (!this.state.isPortFolioLoaded) {
      this.loadPortFolio();
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
    if (this.state.deleteFromPortFolio) readOnly = true;
    console.info('showModalForm: formValues=%o', this.state.formValues);

    return (
      <Form onSubmit={this.handleSubmit} >

        { this.showModalFormGroup(true, "update_timestamp", "Update Timestamp", this.state.formValues.update_timestamp) }
        { this.showModalFormGroup(true, "id", "ID", this.state.formValues.id) }
        { this.showModalFormGroup(readOnly, "watchlist_id", "WatchList Id", this.state.formValues.watchlist_id) }
        { this.showModalFormGroup(readOnly, "source", "Source", this.state.formValues.source)}
        { this.showModalFormGroup(readOnly, "transaction_type", "Units", this.state.formValues.transaction_type)}
        { this.showModalFormGroup(readOnly, "entry_datetime", "Entry Date", this.state.formValues.entry_datetime) }
        { this.showModalFormGroup(readOnly, "entry_price", "Entry Price", this.state.formValues.entry_price)}
        { this.showModalFormGroup(readOnly, "units", "Units", this.state.formValues.units)}
        { this.showModalFormGroup(readOnly, "exit_datetime", "Exit Date", this.state.formValues.exit_datetime) }
        { this.showModalFormGroup(readOnly, "exit_price", "Exit Price", this.state.formValues.exit_price) }
        { this.showModalFormGroup(true, "brine_id", "Brine Id", this.state.formValues.brine_id)}

      </Form>
    );
  }

  onModalActionButtonClick() {
    console.info('onModalActionButtonClick: formValues=%o', this.state.formValues);
    let formValues = this.state.formValues;
    // TODO: Validate data. Temporarily setting it to null, needed for add to succeed
    formValues.optionExpiry = null;
    formValues.optionStrike = null;

    if (this.state.addToPortFolio) {
      console.info('onModalActionButtonClick: call add');
      this.addToPortFolio(this.state.formValues);
      return;
    }

    if (this.state.deleteFromPortFolio) {
      console.info('onModalActionButtonClick: call delete');
      this.deleteFromPortFolio(this.state.formValues);
      return;
    }

    console.info('onModalActionButtonClick: call update');
    this.updatePortFolio(this.state.formValues);
  }

  showModalActionButton() {
    if (this.state.addToPortFolio)
      return (
        <Button variant="primary" onClick={this.onModalActionButtonClick}>
          Add
        </Button>
      );

    if (this.state.deleteFromPortFolio) {
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
          <Modal.Title>PortFolio Details</Modal.Title>
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
      console.info('PortFolio:  not authenticated, redirecting to login page');
      return <Redirect to= '/login' />;
    }

    if ( !this.state.isPortFolioLoaded) {
      return <Alert variant="primary"> Loading PortFolio... </Alert>;
    }

    console.info('render: this.showDetailedViewModal=%o...', this.state.showDetailedViewModal)

    const columns = [
      { Action: 'action',  accessor: 'dummy',
          Cell: ({row}) => (
              <ButtonGroup className="mr-2" aria-label="First group">
                <Button onClick={ (e) => this.onEditButtonClick(row.original) }>Edit</Button>
                <Button onClick={ (e) => this.onDeleteButtonClick(row.original) }>Delete</Button>
              </ButtonGroup>
            )},
      { Header: 'ID',  accessor: 'id'},
      { Header: 'WatchList Id', accessor: 'watchlist_id'},
      { Header: 'Type', accessor: 'transaction_type'},
      { Header: 'Entry Date', accessor: 'entry_datetime'},
      { Header: 'Entry Price', accessor: 'entry_price'},
      { Header: 'Units', accessor: 'units'},
      { Header: 'Exit Date', accessor: 'exit_datetime'},
      { Header: 'Exit Price', accessor: 'exit_price'},
      { Header: 'Source', accessor: 'source'},
      { Header: 'Brine Id', accessor: 'brine_id'},
      { Header: 'Update Time', accessor: 'update_timestamp'},
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
      <div className="PortFolio">

        <ButtonToolbar aria-label="Toolbar with button groups">
          <ButtonGroup className="mr-2" aria-label="First group">
            <Button onClick={this.onAddButtonClick}> Add </Button>
          </ButtonGroup>
          <ButtonGroup className="mr-2" aria-label="Second group">
            <Button onClick={this.loadPortFolio}> Refresh </Button>
          </ButtonGroup>
        </ButtonToolbar>
        Welcome PortFolio {this.props.auth.loggedInUser}
        { this.showErrorMsg() }

        <Table columns={columns} data={this.state.PortFolio} getTrProps={onRowClick} />

        { this.showModal() }

      </div>
    );
  }
}

