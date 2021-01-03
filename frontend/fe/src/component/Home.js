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

export default class Scan extends React.Component {
  constructor(props) {
    super(props);

    this.onEditButtonClick = this.onEditButtonClick.bind(this);
    this.onDeleteButtonClick = this.onDeleteButtonClick.bind(this);
    this.onAddButtonClick = this.onAddButtonClick.bind(this);

    this.loadWatchList = this.loadWatchList.bind(this);
    this.loadScan = this.loadScan.bind(this);
    this.addToScan = this.addToScan.bind(this);
    this.deleteFromScan = this.deleteFromScan.bind(this);
    this.updateScan = this.updateScan.bind(this);

    this.onCloseDetailedViewModal = this.onCloseDetailedViewModal.bind(this);
    this.onModalActionButtonClick = this.onModalActionButtonClick.bind(this);
    this.showModalActionButton = this.showModalActionButton.bind(this);
    this.showErrorMsg = this.showErrorMsg.bind(this);
    this.showModal = this.showModal.bind(this);
    this.showModalForm = this.showModalForm.bind(this);
    this.showModalFormGroup = this.showModalFormGroup.bind(this);
    this.onFormValuesChange = this.onFormValuesChange.bind(this);

    this.state = {
      isScanLoaded: false,
      errorMsg : '',
      Scan : null,
      showDetailedViewModal: false,
      addToScan: false,
      deleteFromScan: false,
      formValues : {id: "", updateTimestamp: "", profile: "", watchListId: "", watchListTicker: "",
       support: "", resistance: "", profitTarget: "", stopLoss: "", etTargetPrice: "", fvTargetPrice: "",
       rationale: "", currentPrice: "", volatility: "", shortfloat: "", status: "", details: ""}
    }
  }

  // Class variable to hold the setInterval Id, used to refresh the page every 5 seconds
  intervalID;

  onCloseDetailedViewModal() {
    console.info('onCloseDetailedViewModal: ...')
    this.setState({
      showDetailedViewModal: false,
      deleteFromScan: false,
      addToScan: false,
      formValues : {id: "", updateTimestamp: "", profile: "", watchListId: "", watchListTicker: "",
       support: "", resistance: "", profitTarget: "", stopLoss: "", etTargetPrice: "", fvTargetPrice: "",
       rationale: "", currentPrice: "", volatility: "", shortfloat: "", status: "", details: ""}
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
      addToScan: true
    });
  }

  onDeleteButtonClick(rowData) {
    console.info('onDeleteButtonClick: rowData=%o', rowData);
    this.setState({
      showDetailedViewModal: true,
      deleteFromScan: true,
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

      // Converting watchList json array to a map
      console.info("loadWatchListCallback: json: %o", json);
      let watchListMap = json.reduce(function(map, obj) {
        map[obj.id] = obj;
        return map;
        }, {});

      console.info("loadWatchListCallback: watListMap: %o", watchListMap);
      let scanArray= this.state.scan;
      let updateWatchListTicker = function (scanEntry) {
        let watchListItem = watchListMap[scanEntry.watchListId];
        let watchListTicker = '';
        console.info("loadWatchListCallback: item: %o", watchListItem);
        if (!watchListItem) {
            watchListTicker = 'NOT FOUND. Stale?';
        } else if (watchListItem.assetType === 'STOCK') {
            watchListTicker = watchListItem.ticker;
        } else {
            watchListTicker = watchListItem.ticker + ' ' + watchListItem.assetType + ' ' + watchListItem.optionStrike + ' ' + watchListItem.optionExpiry;
        }

        scanEntry.watchListTicker = watchListTicker;
      }
      scanArray.forEach(updateWatchListTicker);
      console.info("loadWatchListCallback: scanArray: %o", scanArray);

      // This update is needed to refresh the UI
      this.setState({
        scan: scanArray
      });
    }

    getBackend().getWatchList(loadWatchListCallback.bind(this));
  }

  loadScan() {
    console.info('loadScan: Loading Scan...')
    let loadScanCallback = function (httpStatus, json) {
      if ( httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("loadScanCallback: authentication expired?");
        return;
      }

      if ( httpStatus !== 200) {
        console.error("loadScanCallback: failure: http:%o", httpStatus);
        this.setState({
          errorMsg: "Failed to load Scan"
        })
        return;
      }

      let updateTimeFormat = function (scanEntry) {
        scanEntry.updateTimestampLocal = new Date(scanEntry.updateTimestamp).toLocaleString();
        console.info("updateTimeFormat: json: %o", scanEntry.updateTimestampLocal);
      }
      json.forEach(updateTimeFormat);

      console.info("loadScanCallback: json: %o", json);
      this.setState({
        isScanLoaded: true,
        scan: json,
        errorMsg: ""
      });

      // Update the ticker
      this.loadWatchList();
    }

    getBackend().getScan(loadScanCallback.bind(this));
  }

  addToScan(ScanEntry) {
    console.info('addToScan: adding entry=%o', ScanEntry)
    let createScanCallback = function (httpStatus, json) {
      if ( httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("createScanCallback: authentication expired?");
        return;
      }

      if ( httpStatus !== 200) {
        console.error("createScanCallback: failure: http:%o", httpStatus);
        this.setState({
          errorMsg: "Failed to add to Scan"
        })
        return;
      }

      console.info("createScanCallback: json: %o", json);

      //Reloading the Scan
      this.loadScan();
    }

    getBackend().createScan(ScanEntry, createScanCallback.bind(this));
    this.onCloseDetailedViewModal();
  }

  updateScan(ScanEntry) {
    console.info('updateScan: adding entry=%o', ScanEntry)
    let updateScanCallback= function (httpStatus, json) {
      if ( httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("updateScanCallback: authentication expired?");
        return;
      }

      if ( httpStatus !== 200) {
        console.error("updateScanCallback: failure: http:%o", httpStatus);
        this.setState({
          errorMsg: "Failed to update Scan"
        })
        return;
      }

      console.info("updateScanCallback: json: %o", json);

      //Reloading the Scan
      this.loadScan();
    }

    getBackend().updateScan(ScanEntry, updateScanCallback.bind(this));
    this.onCloseDetailedViewModal();
  }

  deleteFromScan(ScanEntry) {
    console.info('deleteFromScan: adding entry=%o', ScanEntry)
    let deleteFromScanCallback = function (httpStatus, json) {
      if ( httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("deleteFromScanCallback: authentication expired?");
        return;
      }

      if ( httpStatus !== 204) {
        console.error("deleteFromScanCallback: failure: http:%o", httpStatus);
        this.setState({
          errorMsg: "Failed to delete to Scan"
        })
        return;
      }

      console.info("deleteFromScanCallback: json: %o", json);

      //Reloading the Scan
      this.loadScan();
    }

    getBackend().deleteScan(ScanEntry, deleteFromScanCallback.bind(this));
    this.onCloseDetailedViewModal();
  }

  componentDidMount() {
    console.info('componentDidMount..');

    if (!this.state.isScanLoaded) {
      this.loadScan();
      this.intervalID = setInterval(this.loadScan, 30000); // 30s
    }
  }

  componentWillUnmount() {
    console.info("componentWillUnmount: json:%o", this.intervalID);
    clearInterval(this.intervalID);
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
    if (this.state.deleteFromScan) readOnly = true;
    console.info('showModalForm: formValues=%o', this.state.formValues);

    return (
      <Form onSubmit={this.handleSubmit} >

        { this.showModalFormGroup(true, "updateTimestamp", "Update Timestamp", this.state.formValues.updateTimestampLocal) }
        { this.showModalFormGroup(true, "id", "ID", this.state.formValues.id) }
        { this.showModalFormGroup(readOnly, "profile", "Profile", this.state.formValues.profile) }
        { this.showModalFormGroup(readOnly, "watchListId", "WatchList Id", this.state.formValues.watchListId) }
        { this.showModalFormGroup(readOnly, "support", "Support", this.state.formValues.support)}
        { this.showModalFormGroup(readOnly, "resistance", "Resistance", this.state.formValues.resistance)}
        { this.showModalFormGroup(readOnly, "profitTarget", "Profit Target", this.state.formValues.profitTarget) }
        { this.showModalFormGroup(readOnly, "stopLoss", "Stop Loss", this.state.formValues.stopLoss) }
        { this.showModalFormGroup(readOnly, "etTargetPrice", "ET Target", this.state.formValues.etTargetPrice) }
        { this.showModalFormGroup(readOnly, "fvTargetPrice", "FV Target", this.state.formValues.fvTargetPrice) }
        { this.showModalFormGroup(readOnly, "rationale", "Rationale", this.state.formValues.rationale) }
        { this.showModalFormGroup(true, "currentPrice", "Current Price", this.state.formValues.currentPrice) }
        { this.showModalFormGroup(true, "volatility", "Volatility", this.state.formValues.volatility) }
        { this.showModalFormGroup(true, "shortfloat", "Short float", this.state.formValues.shortfloat) }
        { this.showModalFormGroup(true, "status", "Status", this.state.formValues.status) }
        { this.showModalFormGroup(true, "details", "Details", this.state.formValues.details) }

      </Form>
    );
  }

  onModalActionButtonClick() {
    console.info('onModalActionButtonClick: formValues=%o', this.state.formValues);
    let formValues = this.state.formValues;
    // TODO: Validate data. Temporarily setting it to null, needed for add to succeed
    formValues.optionExpiry = null;
    formValues.optionStrike = null;

    if (this.state.addToScan) {
      console.info('onModalActionButtonClick: call add');
      this.addToScan(this.state.formValues);
      return;
    }

    if (this.state.deleteFromScan) {
      console.info('onModalActionButtonClick: call delete');
      this.deleteFromScan(this.state.formValues);
      return;
    }

    console.info('onModalActionButtonClick: call update');
    this.updateScan(this.state.formValues);
  }

  showModalActionButton() {
    if (this.state.addToScan)
      return (
        <Button variant="primary" onClick={this.onModalActionButtonClick}>
          Add
        </Button>
      );

    if (this.state.deleteFromScan) {
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
          <Modal.Title>Scan Details</Modal.Title>
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

  getStatusHighlight(rowData) {
    if (rowData.status === "ATTN")
      return "danger";

    return "info"
  }

  render() {
    if ( !this.props.auth.isAuthenticated ) {
      console.info('Scan:  not authenticated, redirecting to login page');
      return <Redirect to= '/login' />;
    }

    if ( !this.state.isScanLoaded) {
      return <Alert variant="primary"> Loading Scan... </Alert>;
    }

    console.info('render: this.showDetailedViewModal=%o...', this.state.showDetailedViewModal)

    const columns = [
      { Header: 'Action',  accessor: 'dummy',
          Cell: ({row}) => (
              <ButtonGroup className="mr-2" aria-label="First group">
                <Button onClick={ (e) => this.onEditButtonClick(row.original) }>Edit</Button>
                <Button onClick={ (e) => this.onDeleteButtonClick(row.original) }>Delete</Button>
              </ButtonGroup>
            )},
      { Header: 'ID',  accessor: 'id'},
      { Header: 'profile', accessor: 'profile'},
      { Header: 'WL Id', accessor: 'watchListId'},
      { Header: 'WL ticker', accessor: 'watchListTicker'},
      { Header: 'Support', accessor: 'support'},
      { Header: 'Resistance', accessor: 'resistance'},
      { Header: 'Profit Target', accessor: 'profitTarget'},
      { Header: 'Stop Loss', accessor: 'stopLoss'},
      { Header: 'ET Target', accessor: 'etTargetPrice'},
      { Header: 'FV Target', accessor: 'fvTargetPrice'},
      { Header: 'Rationale', accessor: 'rationale'},
      { Header: 'Current Price', accessor: 'currentPrice'},
      { Header: 'Volatility', accessor: 'volatility'},
      { Header: 'Short float', accessor: 'shortfloat'},
      { Header: 'Status', accessor: 'status',
          Cell: ({row}) => (
            <Alert variant={this.getStatusHighlight(row.original)} > {row.original.status} </Alert>
          )},
      { Header: 'Details', accessor: 'details'},
      { Header: 'Update Time', accessor: 'updateTimestampLocal'},
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
      <div className="Scan">

        <ButtonToolbar aria-label="Toolbar with button groups">
          <ButtonGroup className="mr-2" aria-label="First group">
            <Button onClick={this.onAddButtonClick}> Add </Button>
          </ButtonGroup>
          <ButtonGroup className="mr-2" aria-label="Second group">
            <Button onClick={this.loadScan}> Refresh </Button>
          </ButtonGroup>
        </ButtonToolbar>
        Welcome Scan {this.props.auth.loggedInUser}
        { this.showErrorMsg() }

        <Table columns={columns} data={this.state.scan} getTrProps={onRowClick} />

        { this.showModal() }

      </div>
    );
  }
}

