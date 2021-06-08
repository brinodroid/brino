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
import watchlistCache from '../utils/WatchListCache';
import Table from '../utils/Table';

export default class Scan extends React.Component {
  constructor(props) {
    super(props);

    this.onEditButtonClick = this.onEditButtonClick.bind(this);
    this.onDeleteButtonClick = this.onDeleteButtonClick.bind(this);
    this.onAddStockButtonClick = this.onAddStockButtonClick.bind(this);

    this.loadScan = this.loadScan.bind(this);
    this.removeAllMissing = this.removeAllMissing.bind(this);
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

    this.onAutoRefreshButtonPress = this.onAutoRefreshButtonPress.bind(this);
    this.startAutoRefresh = this.startAutoRefresh.bind(this);
    this.stopAutoRefresh = this.stopAutoRefresh.bind(this);


    this.state = {
      isScanLoaded: false,
      errorMsg: '',
      scan: null,
      showDetailedViewModal: false,
      addToScan: false,
      deleteFromScan: false,
      enableAutoRefresh: true,
      formValues: {
        id: "", update_timestamp: "", profile: "", watchlist_id: "", watchListTicker: "",
        support: "", resistance: "", profit_target: "", stopLoss: "", brate_target: "", brifz_target: "",
        rationale: "", current_price: "", volatility: "", short_float: "", status: "", details: ""
      }
    }
  }

  // Class variable to hold the setInterval Id, used to refresh the page every 5 seconds
  intervalID;

  onAutoRefreshButtonPress() {
    let enableAutoRefreshToggled = !this.state.enableAutoRefresh;
    if (enableAutoRefreshToggled) {
      this.startAutoRefresh();
    } else {
      this.stopAutoRefresh();
    }

    this.setState({ enableAutoRefresh: enableAutoRefreshToggled });
  }

  startAutoRefresh() {
    this.intervalID = setInterval(this.loadScan, 30000); // 30s
    console.info('startAutoRefresh: Started auto refresh. intervalID=%o', this.intervalID);
  }

  stopAutoRefresh() {
    console.info('stopAutoRefresh: Started auto refresh. intervalID=%o', this.intervalID);
    clearInterval(this.intervalID);
  }

  onCloseDetailedViewModal() {
    console.info('onCloseDetailedViewModal: ...')
    this.setState({
      showDetailedViewModal: false,
      deleteFromScan: false,
      addToScan: false,
      formValues: {
        id: "", update_timestamp: "", profile: "", watchlist_id: "", watchListTicker: "",
        support: "", resistance: "", profit_target: "", stopLoss: "", brate_target: "", brifz_target: "",
        rationale: "", current_price: "", volatility: "", short_float: "", status: "", details: ""
      }
    });
  }

  onEditButtonClick(rowData) {
    console.info('onEditButtonClick: rowData=%o', rowData);
    this.setState({
      showDetailedViewModal: true,
      formValues: rowData
    });
  }

  onAddStockButtonClick() {
    console.info('onAddStockButtonClick: ...')
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

  loadScan() {
    console.info('loadScan: Loading Scan...')
    let loadScanCallback = function (httpStatus, json) {
      if (httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("loadScanCallback: authentication expired?");
        return;
      }

      if (httpStatus !== 200) {
        console.error("loadScanCallback: failure: http:%o", httpStatus);
        this.setState({
          errorMsg: "Failed to load Scan"
        })
        return;
      }

      let updateTimeFormat = function (scanEntry) {
        scanEntry.updateTimestampLocal = new Date(scanEntry.update_timestamp).toLocaleString();
        console.info("updateTimeFormat: json: %o", scanEntry.updateTimestampLocal);
      }
      json.forEach(updateTimeFormat);

      let updateWatchListTicker = function (scanEntry) {
        scanEntry.watchListTicker = watchlistCache.getWatchListTicker(scanEntry.watchlist_id);
      }

      json.forEach(updateWatchListTicker);

      console.info("loadScanCallback: json: %o", json);
      this.setState({
        isScanLoaded: true,
        scan: json,
        errorMsg: ""
      });
    }

    getBackend().getScan(loadScanCallback.bind(this));
  }

  removeAllMissing() {
    console.info('removeAllMissing: remove all missing...');

    let iterFunction = function (scanEntry, index, scanArray) {
      if (scanEntry.status === "MISSING" ) {
        let deleteMissingScanCallback = function (httpStatus, json) {
          console.info("deleteMissingScanCallback: remove scanEntry:%o, httpStatus:%o, index:%o", scanEntry, httpStatus, index);

          if (httpStatus === 401) {
            this.props.auth.setAuthenticationStatus(false);
            console.error("deleteMissingScanCallback: authentication expired?");
            return;
          }

          if (httpStatus !== 204) {
            console.error("deleteMissingScanCallback: failure: http:%o", httpStatus);
            this.setState({
              errorMsg: "Failed to delete to Scan"
            })
            return;
          }
        }

        getBackend().deleteScan(scanEntry, deleteMissingScanCallback.bind(this));
      }
    }

    if (this.state.scan !== null) {
      this.state.scan.forEach(iterFunction)

      //Reloading the Scan
      this.loadScan();
    }
  }


  addToScan(ScanEntry) {
    console.info('addToScan: adding entry=%o', ScanEntry)

    let createScanCallback = function (httpStatus, json) {
      if (httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("createScanCallback: authentication expired?");
        return;
      }

      if (httpStatus !== 200) {
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

    // TODO: remove the hardcoding
    ScanEntry.profile = 'BUY_STOCK';

    getBackend().createScan(ScanEntry, createScanCallback.bind(this));
    this.onCloseDetailedViewModal();
  }

  updateScan(ScanEntry) {
    console.info('updateScan: adding entry=%o', ScanEntry)
    let updateScanCallback = function (httpStatus, json) {
      if (httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("updateScanCallback: authentication expired?");
        return;
      }

      if (httpStatus !== 200) {
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
      if (httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("deleteFromScanCallback: authentication expired?");
        return;
      }

      if (httpStatus !== 204) {
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

    if (!watchlistCache.isCached()) {
      // Load the watchlist
      watchlistCache.loadWatchList();
    }

    if (!this.state.isScanLoaded) {
      // Load the scan
      this.loadScan();

      // Start with auto refresh being on
      this.startAutoRefresh();
    }
  }

  componentWillUnmount() {
    console.info("componentWillUnmount: json:%o", this.intervalID);
    this.stopAutoRefresh();
  }

  onFormValuesChange(event) {
    let updatedFormValues = { ...this.state.formValues, [event.target.id]: event.target.value };
    console.info('onFormValuesChange: updatedFormValues=%o ', updatedFormValues);
    this.setState({ formValues: updatedFormValues });
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

    if (this.state.addToScan) {
      // Its called from add stock, just show minimal info
      return (
        <Form onSubmit={this.handleSubmit} >

          { this.showModalFormGroup(readOnly, "watchListTicker", "Ticker", this.state.formValues.watchListTicker)}
          { this.showModalFormGroup(readOnly, "resistance", "Resistance", this.state.formValues.resistance)}
          { this.showModalFormGroup(readOnly, "support", "Support", this.state.formValues.support)}

        </Form>
      );
    } else {
      // Its called from edit or delete, show all parameters
      return (
        <Form onSubmit={this.handleSubmit} >

          { this.showModalFormGroup(true, "update_timestamp", "Update Timestamp", this.state.formValues.updateTimestampLocal)}
          { this.showModalFormGroup(true, "id", "ID", this.state.formValues.id)}
          { this.showModalFormGroup(readOnly, "profile", "Profile", this.state.formValues.profile)}
          { this.showModalFormGroup(readOnly, "watchlist_id", "WatchList Id", this.state.formValues.watchlist_id)}
          { this.showModalFormGroup(readOnly, "watchListTicker", "Ticker", this.state.formValues.watchListTicker)}
          { this.showModalFormGroup(readOnly, "portfolio_id", "Portfolio Id", this.state.formValues.portfolio_id)}
          { this.showModalFormGroup(readOnly, "resistance", "Resistance", this.state.formValues.resistance)}
          { this.showModalFormGroup(readOnly, "support", "Support", this.state.formValues.support)}
          { this.showModalFormGroup(readOnly, "stop_loss", "Stop Loss", this.state.formValues.stop_loss)}
          { this.showModalFormGroup(readOnly, "profit_target", "Profit Target", this.state.formValues.profit_target)}
          { this.showModalFormGroup(readOnly, "brate_target", "Brate Target", this.state.formValues.brate_target)}
          { this.showModalFormGroup(readOnly, "brifz_target", "Brifz Target", this.state.formValues.brifz_target)}
          { this.showModalFormGroup(readOnly, "active_track", "Active Track", this.state.formValues.active_track)}
          { this.showModalFormGroup(readOnly, "order_brine_id", "Brine Order Id", this.state.formValues.order_brine_id)}
          { this.showModalFormGroup(readOnly, "rationale", "Rationale", this.state.formValues.rationale)}
          { this.showModalFormGroup(true, "current_price", "Current Price", this.state.formValues.current_price)}
          { this.showModalFormGroup(true, "volatility", "Volatility", this.state.formValues.volatility)}
          { this.showModalFormGroup(true, "short_float", "Short float", this.state.formValues.short_float)}
          { this.showModalFormGroup(true, "status", "Status", this.state.formValues.status)}
          { this.showModalFormGroup(true, "details", "Details", this.state.formValues.details)}

        </Form>
      );
    }
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
      return (<Alert variant='danger' > {rowData.status} </Alert>);

    return rowData.status;
  }

  getRewardHighlight(rowData) {
    if (rowData.reward_2_risk > 2.5) {
      return (<Alert variant='success' > {rowData.reward_2_risk} </Alert>);
    }

    if (rowData.reward_2_risk !== null && rowData.reward_2_risk < 1.5) {

      // The null check is needed as null has value 0
      return (<Alert variant='danger' > {rowData.reward_2_risk} </Alert>);
    }

    return rowData.reward_2_risk;
  }

  getShortFloatHighlight(rowData) {
    let shortFloatNumber = parseFloat(rowData.short_float);
    if (shortFloatNumber !== null && shortFloatNumber > 15) {
      // Interesting if the shortfloat is more than 15
      return (<Alert variant='success' > {rowData.short_float} </Alert>);
    }

    return rowData.short_float;
  }

  getPotentialHighlight(rowData) {
    if (rowData.potential > 1.2) {
      return (<Alert variant='success' > {rowData.potential} </Alert>);
    }

    if (rowData.potential !== null && rowData.potential < 0.8) {
      // The null check is needed as null has value 0
      return (<Alert variant='danger' > {rowData.potential} </Alert>);
    }

    return rowData.potential;
  }

  render() {
    if (!this.props.auth.isAuthenticated) {
      console.info('Scan:  not authenticated, redirecting to login page');
      return <Redirect to='/login' />;
    }

    if (!this.state.isScanLoaded) {
      return <Alert variant="primary"> Loading Scan... </Alert>;
    }

    console.info('render: this.showDetailedViewModal=%o...', this.state.showDetailedViewModal)

    const columns = [
      {
        Header: 'Action', accessor: 'dummy',
        Cell: ({ row }) => (
          <ButtonGroup className="mr-2" aria-label="First group">
            <Button onClick={(e) => this.onEditButtonClick(row.original)}>Edit</Button>
            <Button onClick={(e) => this.onDeleteButtonClick(row.original)}>Delete</Button>
          </ButtonGroup>
        )
      },
      { Header: 'profile', accessor: 'profile' },
      { Header: 'WL ticker', accessor: 'watchListTicker' },
      { Header: 'Current Price', accessor: 'current_price' },
      { Header: 'Brate Target', accessor: 'brate_target' },
      { Header: 'Brifz Target', accessor: 'brifz_target' },
      { Header: 'Rationale', accessor: 'rationale' },
      { Header: 'Volatility', accessor: 'volatility' },
      {
        Header: 'Short float', accessor: 'short_float',
        Cell: ({ row }) => (
          <> {this.getShortFloatHighlight(row.original)} </>
        )
      },
      {
        Header: 'Potential', accessor: 'potential',
        Cell: ({ row }) => (
          <> {this.getPotentialHighlight(row.original)} </>
        )
      },
      {
        Header: 'Reward', accessor: 'reward_2_risk',
        Cell: ({ row }) => (
          <> {this.getRewardHighlight(row.original)} </>
        )
      },
      {
        Header: 'Status', accessor: 'status',
        Cell: ({ row }) => (
          <> {this.getStatusHighlight(row.original)} </>
        )
      },
      { Header: 'Details', accessor: 'details' },
      { Header: 'Update Time', accessor: 'updateTimestampLocal' },
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
      <div className="Home">

        <ButtonToolbar aria-label="Toolbar with button groups">
          <ButtonGroup className="mr-2" aria-label="First group">
            <Button onClick={this.onAddStockButtonClick}> Add Stock </Button>
          </ButtonGroup>
          <ButtonGroup className="mr-2" aria-label="Second group">
            <Button onClick={this.loadScan}> Refresh </Button>
          </ButtonGroup>
          <ButtonGroup className="mr-2" aria-label="Second group">
            <Button onClick={this.removeAllMissing}> Remove Missing </Button>
          </ButtonGroup>
          <ButtonGroup className="mr-2" aria-label="Second group">
            <Button onClick={this.onAutoRefreshButtonPress}> {this.state.enableAutoRefresh ? "Disable Auto Refresh" : "Enable Auto Refresh"} </Button>
          </ButtonGroup>
        </ButtonToolbar>
        { this.showErrorMsg()}

        <Table columns={columns} data={this.state.scan} getTrProps={onRowClick} />

        { this.showModal()}

      </div>
    );
  }
}

