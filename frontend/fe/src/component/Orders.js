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
    this.onCreateOrder = this.onCreateOrder.bind(this);

    this.loadExecutedOrders = this.loadExecutedOrders.bind(this);
    this.loadCancelledOrders = this.loadCancelledOrders.bind(this);

    this.loadOpenOrders = this.loadOpenOrders.bind(this);
    this.submitNewOrder = this.submitNewOrder.bind(this);
    this.deleteOrder = this.deleteOrder.bind(this);

    this.onCloseDetailedViewModal = this.onCloseDetailedViewModal.bind(this);
    this.onModalActionButtonClick = this.onModalActionButtonClick.bind(this);
    this.showModalActionButton = this.showModalActionButton.bind(this);
    this.showErrorMsg = this.showErrorMsg.bind(this);
    this.showModal = this.showModal.bind(this);
    this.showModalForm = this.showModalForm.bind(this);
    this.showCreateModalForm = this.showCreateModalForm.bind(this);
    this.showModalFormGroup = this.showModalFormGroup.bind(this);

    this.onFormValuesChange = this.onFormValuesChange.bind(this);
    this.onFormValuesSelection = this.onFormValuesSelection.bind(this);

    this.createDefaultFormValues = this.createDefaultFormValues.bind(this);


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

      createNewOrder: false,
      deleteOrder: false,
      form_values: this.createDefaultFormValues()
    }
  }


  createDropDownSelections(options_array) {
    return {selected:options_array[0], options:options_array};
  }

  createDefaultFormValues() {

    let asset_type_array = ["STOCK", "CALL", "PUT"];
    let transaction_type_list_array = ["BUY", "SELL"];
    let action_array = ["OPEN", "CLOSE"];
    let binary_array = ["true", "false"];

    let formValueDefaults = {asset_type_sel: this.createDropDownSelections(asset_type_array),
          ticker:"", option_strike:"", option_expiry:"",
          strategy_type:"", stop_loss:"", profit_target:"",
          active_track_sel: this.createDropDownSelections(binary_array),
          transaction_type_list_sel: this.createDropDownSelections(transaction_type_list_array),
          price:"", units:"", action_sel: this.createDropDownSelections(action_array),
          source:"BRINE", submit_sel: this.createDropDownSelections(binary_array)
          }

    return formValueDefaults
  }


  onCloseDetailedViewModal() {
    console.info('onCloseDetailedViewModal: ...')
    this.setState({
      showDetailedViewModal: false,
      deleteOrder: false,
      createNewOrder: false,
      form_values: {}
    });
  }

  onEditButtonClick(rowData) {
    console.info('onEditButtonClick: rowData=%o', rowData);
    this.setState({
      showDetailedViewModal: true,
      form_values: rowData
    });
  }

  onCreateOrder() {
    console.info('onCreateOrder: ...')
    this.setState({
      showDetailedViewModal: true,
      createNewOrder: true,
      // Put the form with some defaults
      form_values: this.createDefaultFormValues()
    });
  }

  onDeleteButtonClick(rowData) {
    console.info('onDeleteButtonClick: rowData=%o', rowData);
    this.setState({
      showDetailedViewModal: true,
      deleteOrder: true,
      form_values: rowData
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

      if (!json) {
        console.error("loadOpenOrdersCallback: empty json: http:%o", httpStatus);
        this.setState({
          errorMsg: "Got empty json"
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


  submitNewOrder(form_values) {
    console.info('submitNewOrder: adding entry=%o', form_values);
    let submitOrderStrategyCallback = function (httpStatus, json) {
      if (httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("submitOrderStrategyCallback: authentication expired?");
        return;
      }

      if (httpStatus !== 200) {
        console.error("submitOrderStrategyCallback: failure: http:%o", httpStatus);
        this.setState({
          errorMsg: "Failed to submit order"
        })
        return;
      }

      console.info("submitOrderStrategyCallback: json: %o", json);
      this.setState({
        isOrdersLoaded: true,
        orders: json,
        viewType: this.state.CANCELLED_ORDER_STRING,
        errorMsg: ""
      });
    }

    let watchlist = {};
    watchlist.asset_type = form_values.asset_type_sel.selected
    watchlist.ticker = form_values.ticker;
    watchlist.option_strike = form_values.option_strike;
    watchlist.option_expiry = form_values.option_expiry;

    let strategy = {};
    strategy.strategy_type = form_values.strategy_type;
    strategy.stop_loss = form_values.stop_loss;
    strategy.profit_target = form_values.profit_target;
    strategy.active_track = form_values.active_track_sel.selected;

    let newOrder = {};
    newOrder.transaction_type_list = form_values.transaction_type_list_sel.selected;
    newOrder.price = form_values.price;
    newOrder.units = form_values.units;
    newOrder.action = form_values.action_sel.selected;
    newOrder.source = form_values.source;
    newOrder.submit = form_values.submit;

    getBackend().submitOrderStrategy(watchlist, newOrder, strategy, submitOrderStrategyCallback.bind(this));
  }

  deleteOrder(order) {
    console.info('deleteOrder: adding entry=%o', order);
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
    let updated_form_values = { ...this.state.form_values, [event.target.id]: event.target.value };
    console.info('onFormValuesChange: updated_form_values=%o ', updated_form_values);
    this.setState({ form_values: updated_form_values });
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

  onFormValuesSelection(event) {
    let updated_selection = this.state.form_values[event.target.id];
    updated_selection.selected = updated_selection.options[event.target.options.selectedIndex];

    let updated_form_values = { ...this.state.form_values, [event.target.id]: updated_selection};
    console.info('onFormValuesChange: updated_form_values=%o ', updated_form_values);
    this.setState({ form_values: updated_form_values });
  }

  showDropDown(controlId, label, dropdown_selection) {
    return (
      <Form.Group as={Row} controlId={controlId}>
        <Form.Label column sm="4"> {label} </Form.Label>
        <Col sm="8">

        <Form.Control as="select" onChange={this.onFormValuesSelection}>
          {dropdown_selection.options.map((item, index) => {
            return (
              <option value={index}>{item}</option>
            );
          })}
        </Form.Control>

        </Col>
      </Form.Group>

    );
  }

  showCreateModalForm() {
    console.info('showCreateModalForm: form_value=%o', this.state.form_values);
    return (
      <Form onSubmit={this.handleSubmit} >
        { this.showDropDown("asset_type_sel", "Asset Type", this.state.form_values.asset_type_sel)}
        { this.showModalFormGroup(false, "ticker", "Ticker", this.state.form_values.ticker)}
        { this.showModalFormGroup(false, "option_strike", "Strike", this.state.form_values.option_strike)}
        { this.showModalFormGroup(false, "option_expiry", "Expiry", this.state.form_values.option_expiry)}
        { this.showDropDown("transaction_type_list_sel", "Transaction type", this.state.form_values.transaction_type_list_sel)}
        { this.showDropDown("action_sel", "Action", this.state.form_values.action_sel)}
        { this.showModalFormGroup(false, "price", "Price", this.state.form_values.price)}
        { this.showModalFormGroup(false, "units", "Units", this.state.form_values.units)}
        { this.showModalFormGroup(false, "strategy_type", "Strategy Type", this.state.form_values.strategy_type)}
        { this.showDropDown("submit", "Submit", this.state.form_values.submit_sel)}
        { this.showDropDown("active_track", "Active Track", this.state.form_values.active_track_sel)}
        { this.showModalFormGroup(false, "stop_loss", "Stop Loss", this.state.form_values.stop_loss)}
        { this.showModalFormGroup(false, "profit_target", "Profit Target", this.state.form_values.profit_target)}
        { this.showModalFormGroup(false, "source", "Source", this.state.form_values.source)}
      </Form>
    )
  }

  showModalForm() {
    if (this.state.createNewOrder) {
      return this.showCreateModalForm()
    }

    console.info('showModalForm: form_value=%o', this.state.form_values);
    return (
      <Form onSubmit={this.handleSubmit} >
        { this.showModalFormGroup(true, "watchlist_id", "WatchList Id", this.state.form_values.watchlist_id_list)}
        { this.showModalFormGroup(true, "transaction_type_list", "Transaction type", this.state.form_values.transaction_type_list)}
        { this.showModalFormGroup(true, "source", "Source", this.state.form_values.source)}
        { this.showModalFormGroup(true, "price", "Price", this.state.form_values.price)}
        { this.showModalFormGroup(true, "units", "Units", this.state.form_values.units)}
        { this.showModalFormGroup(true, "action", "Action", this.state.form_values.action)}
        { this.showModalFormGroup(true, "submit", "Submit", this.state.form_values.submit)}
        { this.showModalFormGroup(true, "id", "ID", this.state.form_values.id)}
        { this.showModalFormGroup(true, "strategy_id", "Strategy Id", this.state.form_values.strategy_id)}
        { this.showModalFormGroup(true, "brine_id", "Brine Id", this.state.form_values.brine_id)}
        { this.showModalFormGroup(true, "created_timestamp", "Create Timestamp", this.state.form_values.created_datetime)}
        { this.showModalFormGroup(true, "update_timestamp", "Update Timestamp", this.state.form_values.update_timestamp)}

      </Form>
    );
  }

  onModalActionButtonClick() {
    console.info('onModalActionButtonClick: form_value=%o', this.state.form_value);

    if (this.state.createNewOrder) {
      console.info('onModalActionButtonClick: call add');
      this.submitNewOrder(this.state.form_values);
      return;
    }

    if (this.state.deleteOrder) {
      console.info('onModalActionButtonClick: call delete');
      this.deleteOrder(this.state.form_values);
      return;
    }

    console.info('onModalActionButtonClick: call update');
    this.updatePortFolio(this.state.form_values);
  }

  showModalActionButton() {
    if (this.state.createNewOrder) {
      return (
          <Button variant="primary" onClick={this.onModalActionButtonClick}>
            Submit
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
            <Button onClick={this.onCreateOrder}> Create Order </Button>
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

