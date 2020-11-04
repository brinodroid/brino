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

export default class WatchList extends React.Component {
  constructor(props) {
    super(props);

    this.onEditButtonClick = this.onEditButtonClick.bind(this);
    this.onDeleteButtonClick = this.onDeleteButtonClick.bind(this);
    this.onAddButtonClick = this.onAddButtonClick.bind(this);

    this.loadWatchList = this.loadWatchList.bind(this);
    this.addToWatchList = this.addToWatchList.bind(this);
    this.deleteFromWatchList = this.deleteFromWatchList.bind(this);
    this.updateWatchList = this.updateWatchList.bind(this);

    this.onCloseDetailedViewModal = this.onCloseDetailedViewModal.bind(this);
    this.onModalActionButtonClick = this.onModalActionButtonClick.bind(this);
    this.showModalActionButton = this.showModalActionButton.bind(this);
    this.showErrorMsg = this.showErrorMsg.bind(this);
    this.showModal = this.showModal.bind(this);
    this.showModalForm = this.showModalForm.bind(this);
    this.showModalFormGroup = this.showModalFormGroup.bind(this);
    this.onFormValuesChange = this.onFormValuesChange.bind(this);

    this.state = {
      isWatchListLoaded: false,
      errorMsg : '',
      watchList : null,
      showDetailedViewModal: false,
      addToWatchList: false,
      deleteFromWatchList: false,
      formValues : {id: "", assetType: "", ticker: "", optionStrike: "", optionExpiry: "", comment: ""}
    }
  }

  onCloseDetailedViewModal() {
    console.info('onCloseDetailedViewModal: ...')
    this.setState({
      showDetailedViewModal: false,
      deleteFromWatchList: false,
      addToWatchList: false,
      formValues : {id: "", assetType: "", ticker: "", optionStrike: "", optionExpiry: "", comment: ""}
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
      addToWatchList: true
    });
  }

  onDeleteButtonClick(rowData) {
    console.info('onDeleteButtonClick: rowData=%o', rowData);
    this.setState({
      showDetailedViewModal: true,
      deleteFromWatchList: true,
      formValues: rowData
    });
  }

  showErrorMsg() {
    if (this.state.errorMsg !== "") {
      return <Alert variant={'danger'} > {this.state.errorMsg} </Alert>
    }
  }

  loadWatchList() {
    console.info('loadWatchList: Loading watchlist...')
    let loadWatchListCallback = function (httpStatus, json) {
      if ( httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("loadWatchListCallback: authentication expired?");
        return;
      }

      if ( httpStatus !== 200) {
        console.error("loadWatchListCallback: failure: http:%o", httpStatus);
        this.setState({
          errorMsg: "Failed to load watchlist"
        })
        return;
      }

      console.info("loadWatchListCallback: json: %o", json);
      this.setState({
        isWatchListLoaded: true,
        watchList: json,
        errorMsg: ""
      });
    }

    getBackend().getWatchList(loadWatchListCallback.bind(this));
  }

  addToWatchList(watchListEntry) {
    console.info('addToWatchList: adding entry=%o', watchListEntry)
    let createWatchListEntryCallback = function (httpStatus, json) {
      if ( httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("createWatchListEntryCallback: authentication expired?");
        return;
      }

      if ( httpStatus !== 200) {
        console.error("createWatchListEntryCallback: failure: http:%o", httpStatus);
        this.setState({
          errorMsg: "Failed to add to watchlist"
        })
        return;
      }

      console.info("createWatchListEntryCallback: json: %o", json);

      //Reloading the watchlist
      this.loadWatchList();
    }

    getBackend().createWatchListEntry(watchListEntry, createWatchListEntryCallback.bind(this));
    this.onCloseDetailedViewModal();
  }

  updateWatchList(watchListEntry) {
    console.info('updateWatchList: adding entry=%o', watchListEntry)
    let updateWatchListCallback= function (httpStatus, json) {
      if ( httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("updateWatchListCallback: authentication expired?");
        return;
      }

      if ( httpStatus !== 200) {
        console.error("updateWatchListCallback: failure: http:%o", httpStatus);
        this.setState({
          errorMsg: "Failed to update watchlist"
        })
        return;
      }

      console.info("updateWatchListCallback: json: %o", json);

      //Reloading the watchlist
      this.loadWatchList();
    }

    getBackend().updateWatchList(watchListEntry, updateWatchListCallback.bind(this));
    this.onCloseDetailedViewModal();
  }

  deleteFromWatchList(watchListEntry) {
    console.info('deleteFromWatchList: adding entry=%o', watchListEntry)
    let deleteFromWatchListCallback = function (httpStatus, json) {
      if ( httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("deleteFromWatchListCallback: authentication expired?");
        return;
      }

      if ( httpStatus !== 204) {
        console.error("deleteFromWatchListCallback: failure: http:%o", httpStatus);
        this.setState({
          errorMsg: "Failed to delete to watchlist"
        })
        return;
      }

      console.info("deleteFromWatchListCallback: json: %o", json);

      //Reloading the watchlist
      this.loadWatchList();
    }

    getBackend().deleteFromWatchList(watchListEntry, deleteFromWatchListCallback.bind(this));
    this.onCloseDetailedViewModal();
  }

  componentDidMount() {
    console.info('componentDidMount..');

    if (!this.state.isWatchListLoaded) {
      this.loadWatchList();
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
    if (this.state.deleteFromWatchList) readOnly = true;
    console.info('showModalForm: formValues=%o', this.state.formValues);

    return (
      <Form onSubmit={this.handleSubmit} >

        { this.showModalFormGroup(true, "creationTimestamp", "Create Timestamp", this.state.formValues.creationTimestamp) }
        { this.showModalFormGroup(true, "updateTimestamp", "Update Timestamp", this.state.formValues.updateTimestamp) }
        { this.showModalFormGroup(true, "id", "ID", this.state.formValues.id) }
        { this.showModalFormGroup(readOnly, "assetType", "Asset Type", this.state.formValues.assetType) }
        { this.showModalFormGroup(readOnly, "ticker", "Ticker", this.state.formValues.ticker) }
        { this.showModalFormGroup(readOnly, "optionStrike", "Strike", this.state.formValues.optionStrike? this.state.formValues.optionStrike: "") }
        { this.showModalFormGroup(readOnly, "optionExpiry", "Expiry", this.state.formValues.optionExpiry? this.state.formValues.optionExpiry:"" ) }
        { this.showModalFormGroup(readOnly, "comment", "Comment", this.state.formValues.comment) }

      </Form>
    );
  }

  onModalActionButtonClick() {
    console.info('onModalActionButtonClick: formValues=%o', this.state.formValues);
    let formValues = this.state.formValues;

    if (this.state.addToWatchList) {
      console.info('onModalActionButtonClick: call add');
      this.addToWatchList(this.state.formValues);
      return;
    }

    if (this.state.deleteFromWatchList) {
      console.info('onModalActionButtonClick: call delete');
      this.deleteFromWatchList(this.state.formValues);
      return;
    }

    console.info('onModalActionButtonClick: call update');
    this.updateWatchList(this.state.formValues);
  }

  showModalActionButton() {
    if (this.state.addToWatchList)
      return (
        <Button variant="primary" onClick={this.onModalActionButtonClick}>
          Add
        </Button>
      );

    if (this.state.deleteFromWatchList) {
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
      console.info('WatchList:  not authenticated, redirecting to login page');
      return <Redirect to= '/login' />;
    }

    if ( !this.state.isWatchListLoaded) {
      return <Alert variant="primary"> Loading watchlist... </Alert>;
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
      { Header: 'Asset Type', accessor: 'assetType'},
      { Header: 'Ticker', accessor: 'ticker'},
      { Header: 'Strike', accessor: 'optionStrike'},
      { Header: 'Expiry', accessor: 'optionExpiry'},
      { Header: 'Comment', accessor: 'comment'},
      { Header: 'Update Time', accessor: 'updateTimestamp'},
      { Header: 'Create Time', accessor: 'creationTimestamp'},
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
      <div className="WatchList">

        <ButtonToolbar aria-label="Toolbar with button groups">
          <ButtonGroup className="mr-2" aria-label="First group">
            <Button onClick={this.onAddButtonClick}> Add </Button>
          </ButtonGroup>
          <ButtonGroup className="mr-2" aria-label="Second group">
            <Button onClick={this.loadWatchList}> Refresh </Button>
          </ButtonGroup>
        </ButtonToolbar>
        Welcome WatchList {this.props.auth.loggedInUser}
        { this.showErrorMsg() }

        <Table columns={columns} data={this.state.watchList} getTrProps={onRowClick} />

        { this.showModal() }

      </div>
    );
  }
}

