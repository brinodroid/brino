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

export default class Orders extends React.Component {
  constructor(props) {
    super(props);

    this.onEditButtonClick = this.onEditButtonClick.bind(this);
    this.onDeleteButtonClick = this.onDeleteButtonClick.bind(this);
    this.onAddButtonClick = this.onAddButtonClick.bind(this);

    this.loadExecutedOrders = this.loadExecutedOrders.bind(this);
    this.loadCancelledOrders = this.loadCancelledOrders.bind(this);

    this.loadOpenOrders = this.loadOpenOrders.bind(this);
    this.openNewOrder = this.openNewOrder.bind(this);
    this.deleteOrder = this.deleteOrder.bind(this);

    this.onCloseDetailedViewModal = this.onCloseDetailedViewModal.bind(this);
    this.onModalActionButtonClick = this.onModalActionButtonClick.bind(this);
    this.showModalActionButton = this.showModalActionButton.bind(this);
    this.showErrorMsg = this.showErrorMsg.bind(this);
    this.showModal = this.showModal.bind(this);
    this.showModalForm = this.showModalForm.bind(this);
    this.showModalFormGroup = this.showModalFormGroup.bind(this);
    this.onFormValuesChange = this.onFormValuesChange.bind(this);

    let openOrderString = 'Open Order';
    this.state = {
      OPEN_ORDER_STRING: openOrderString,
      EXECUTED_ORDER_STRING: 'Executed Order',
      CANCELLED_ORDER_STRING: 'Cancelled Order',
      isOrdersLoaded: false,
      errorMsg: '',
      orders: null,
      viewType: openOrderString,
      showDetailedViewModal: false,

      openNewOrder: false,
      deleteOrder: false,
      formValues: {}
    }
  }

  onCloseDetailedViewModal() {
    console.info('onCloseDetailedViewModal: ...')
    this.setState({
      showDetailedViewModal: false,
      deleteOrder: false,
      openNewOrder: false,
      formValues: {}
    });
  }

  onEditButtonClick(rowData) {
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
      openNewOrder: true
    });
  }

  onDeleteButtonClick(rowData) {
    console.info('onDeleteButtonClick: rowData=%o', rowData);
    this.setState({
      showDetailedViewModal: true,
      deleteOrder: true,
      formValues: rowData
    });
  }

  showErrorMsg() {
    if (this.state.errorMsg !== "") {
      return <Alert variant={'danger'} > {this.state.errorMsg} </Alert>
    }
  }

  loadOpenOrders() {
    console.info('loadOpenOrders: Loading Open Orders...')
    let loadOpenOrdersCallback = function (httpStatus, json) {
      if (httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("loadOpenOrdersCallback: authentication expired?");
        return;
      }

      if (httpStatus !== 200) {
        console.error("loadOpenOrdersCallback: failure: http:%o", httpStatus);
        this.setState({
          errorMsg: "Failed to load Open Orders"
        })
        return;
      }

      // Update the watchlist ticker to portfolio
      let updateWatchListTicker = function (openOrders) {
        // TODO: Handle list of watchlist Ids
        openOrders.watchListTickerList = watchlistCache.getWatchListTicker(openOrders.watchlist_id_list);
      }

      json.forEach(updateWatchListTicker);

      console.info("loadOpenOrdersCallback: json: %o", json);
      this.setState({
        isOrdersLoaded: true,
        orders: json,
        viewType: this.state.OPEN_ORDER_STRING,
        errorMsg: ""
      });
    }

    getBackend().getOpenOrders(loadOpenOrdersCallback.bind(this));
  }

  loadExecutedOrders() {
    console.info('loadExecutedOrders: Loading executed orders...')
    let loadExecutedOrdersCallback = function (httpStatus, json) {
      if (httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("loadExecutedOrdersCallback: authentication expired?");
        return;
      }

      if (httpStatus !== 200) {
        console.error("loadExecutedOrdersCallback: failure: http:%o", httpStatus);
        this.setState({
          errorMsg: "Failed to load Executed Orders"
        })
        return;
      }

      // Update the watchlist ticker to portfolio
      let updateWatchListTicker = function (openOrders) {
        // TODO: Handle list of watchlist Ids
        openOrders.watchListTickerList = watchlistCache.getWatchListTicker(openOrders.watchlist_id_list);
      }

      json.forEach(updateWatchListTicker);

      console.info("loadExecutedOrdersCallback: json: %o", json);
      this.setState({
        isOrdersLoaded: true,
        orders: json,
        viewType: this.state.EXECUTED_ORDER_STRING,
        errorMsg: ""
      });
    }

    getBackend().getExecutedOrders(loadExecutedOrdersCallback.bind(this));
  }

  loadCancelledOrders () {
    console.info('loadCancelledOrders: Loading cancelled orders...')
    let loadCancelledOrdersCallback = function (httpStatus, json) {
      if (httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("loadCancelledOrdersCallback: authentication expired?");
        return;
      }

      if (httpStatus !== 200) {
        console.error("loadCancelledOrdersCallback: failure: http:%o", httpStatus);
        this.setState({
          errorMsg: "Failed to load Executed Orders"
        })
        return;
      }

      // Update the watchlist ticker to portfolio
      let updateWatchListTicker = function (openOrders) {
        // TODO: Handle list of watchlist Ids
        openOrders.watchListTickerList = watchlistCache.getWatchListTicker(openOrders.watchlist_id_list);
      }

      json.forEach(updateWatchListTicker);

      console.info("loadCancelledOrdersCallback: json: %o", json);
      this.setState({
        isOrdersLoaded: true,
        orders: json,
        viewType: this.state.CANCELLED_ORDER_STRING,
        errorMsg: ""
      });
    }

    getBackend().getCancelledOrders(loadCancelledOrdersCallback.bind(this));
  }


  openNewOrder(newOrder) {
    console.info('openNewOrder: adding entry=%o', newOrder)
  }

  deleteOrder(order) {
    console.info('deleteOrder: adding entry=%o', order)
  }

  componentDidMount() {
    console.info('componentDidMount..');

    if (!watchlistCache.isCached()) {
      // Load the watchlist
      watchlistCache.loadWatchList();
    }

    if (!this.state.isOrdersLoaded) {
      this.loadOpenOrders();
    }
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
    console.info('showModalForm: formValues=%o', this.state.formValues);
    let readOnly = true;
    if (this.state.openNewOrder) {
      readOnly = false;
    }

    return (
      <Form onSubmit={this.handleSubmit} >
        { this.showModalFormGroup(readOnly, "watchlist_id", "WatchList Id", this.state.formValues.watchlist_id_list)}
        { this.showModalFormGroup(readOnly, "transaction_type", "Units", this.state.formValues.transaction_type_list)}
        { this.showModalFormGroup(readOnly, "source", "Source", this.state.formValues.source)}
        { this.showModalFormGroup(readOnly, "price", "Entry Price", this.state.formValues.price)}
        { this.showModalFormGroup(readOnly, "units", "Units", this.state.formValues.units)}
        { this.showModalFormGroup(readOnly, "action", "Action", this.state.formValues.action)}
        { this.showModalFormGroup(readOnly, "submit", "Submit", this.state.formValues.submit)}
        { this.showModalFormGroup(true, "id", "ID", this.state.formValues.id)}
        { this.showModalFormGroup(true, "strategy_id", "Strategy Id", this.state.formValues.strategy_id)}
        { this.showModalFormGroup(true, "brine_id", "Brine Id", this.state.formValues.brine_id)}
        { this.showModalFormGroup(true, "created_timestamp", "Create Timestamp", this.state.formValues.created_datetime)}
        { this.showModalFormGroup(true, "update_timestamp", "Update Timestamp", this.state.formValues.update_timestamp)}

      </Form>
    );
  }

  onModalActionButtonClick() {
    console.info('onModalActionButtonClick: formValues=%o', this.state.formValues);
    let formValues = this.state.formValues;
    // TODO: Validate data. Temporarily setting it to null, needed for add to succeed
    formValues.optionExpiry = null;
    formValues.optionStrike = null;

    if (this.state.openNewOrder) {
      console.info('onModalActionButtonClick: call add');
      this.openNewOrder(this.state.formValues);
      return;
    }

    if (this.state.deleteOrder) {
      console.info('onModalActionButtonClick: call delete');
      this.deleteOrder(this.state.formValues);
      return;
    }

    console.info('onModalActionButtonClick: call update');
    this.updatePortFolio(this.state.formValues);
  }

  showModalActionButton() {
    if (this.state.openNewOrder) {
      return (
          <Button variant="primary" onClick={this.onModalActionButtonClick}>
            Create
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
          <Modal.Title>Order details</Modal.Title>
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
    if (!this.props.auth.isAuthenticated) {
      console.info('PortFolio:  not authenticated, redirecting to login page');
      return <Redirect to='/login' />;
    }

    if (!this.state.isOrdersLoaded) {
      return <Alert variant="primary"> Loading open orders... </Alert>;
    }

    console.info('render: this.showDetailedViewModal=%o...', this.state.showDetailedViewModal)

    const columns = [
      {
        Header: this.state.viewType, Action: 'action', accessor: 'dummy',
        Cell: ({ row }) => (
          <ButtonGroup className="mr-2" aria-label="First group">
            <Button onClick={(e) => this.onEditButtonClick(row.original)}>Edit</Button>
            <Button onClick={(e) => this.onDeleteButtonClick(row.original)}>Delete</Button>
          </ButtonGroup>
        )
      },
      { Header: 'ID', accessor: 'id' },
      { Header: 'WatchList Id list', accessor: 'watchlist_id_list' },
      { Header: 'WL ticker list', accessor: 'watchListTickerList' },
      { Header: 'Type list', accessor: 'transaction_type_list' },
      { Header: 'Price', accessor: 'price' },
      { Header: 'Units', accessor: 'units' },
      { Header: 'Opening strategy', accessor: 'opening_strategy' },
      { Header: 'Closing strategy', accessor: 'closing_strategy' },
      { Header: 'Brine Id', accessor: 'brine_id' },
      { Header: 'Created Time', accessor: 'created_datetime' },
      { Header: 'Update Time', accessor: 'update_timestamp' },
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
      <div className="Orders">
        <ButtonToolbar aria-label="Toolbar with button groups">
          <ButtonGroup className="mr-2" aria-label="Second group">
            <Button onClick={this.onAddButtonClick}> Create Order </Button>
          </ButtonGroup>

          <ButtonGroup className="mr-2" aria-label="Second group">
            <Button onClick={this.loadOpenOrders}> Open </Button>
          </ButtonGroup>
          <ButtonGroup className="mr-2" aria-label="Second group">
            <Button onClick={this.loadExecutedOrders}> Executed </Button>
          </ButtonGroup>
          <ButtonGroup className="mr-2" aria-label="Second group">
            <Button onClick={this.loadCancelledOrders}> Cancelled </Button>
          </ButtonGroup>
        </ButtonToolbar>
        { this.showErrorMsg()}

        <Table columns={columns} data={this.state.orders} getTrProps={onRowClick} />

        { this.showModal()}

      </div>
    );
  }
}

