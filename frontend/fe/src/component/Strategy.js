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

import watchlistCache from '../utils/WatchListCache';
import { getBackend } from '../utils/Backend';
import Table from '../utils/Table';

export default class Strategy extends React.Component {
  constructor(props) {
    super(props);

    this.onEditButtonClick = this.onEditButtonClick.bind(this);
    this.onDeleteButtonClick = this.onDeleteButtonClick.bind(this);
    this.onAddButtonClick = this.onAddButtonClick.bind(this);

    this.loadStrategies = this.loadStrategies.bind(this);
    this.createNewStrategy = this.createNewStrategy.bind(this);
    this.deleteStrategy = this.deleteStrategy.bind(this);
    this.updateStrategy = this.updateStrategy.bind(this);

    this.onCloseDetailedViewModal = this.onCloseDetailedViewModal.bind(this);
    this.onModalActionButtonClick = this.onModalActionButtonClick.bind(this);
    this.showModalActionButton = this.showModalActionButton.bind(this);
    this.showErrorMsg = this.showErrorMsg.bind(this);
    this.showModal = this.showModal.bind(this);
    this.showModalForm = this.showModalForm.bind(this);
    this.showModalFormGroup = this.showModalFormGroup.bind(this);
    this.onFormValuesChange = this.onFormValuesChange.bind(this);
    this.onFormValuesSelection = this.onFormValuesSelection.bind(this);

    this.createDefaultFormValues = this.createDefaultFormValues.bind(this);

    this.state = {
      isStrategyLoaded: watchlistCache.isCached(),
      errorMsg: '',
      strategy_list: null,
      showDetailedViewModal: false,
      createNewStrategy: false,
      deleteStrategy: false,
      formValues: this.createDefaultFormValues()
    }
  }

  createDropDownSelections(options_array) {
    return {selected:options_array[0], options:options_array};
  }

  createDefaultFormValues() {
    let binary_array = ["false", "true"];

    return { id: "",
              strategy_type: "",
              portfolio_id: "",
              stop_loss: "",
              profit_target: "",
              active_track: false,
              active_track_sel: this.createDropDownSelections(binary_array)
            };
  }

  onCloseDetailedViewModal() {
    console.info('onCloseDetailedViewModal: ...')
    this.setState({
      showDetailedViewModal: false,
      deleteStrategy: false,
      createNewStrategy: false,
      formValues: this.createDefaultFormValues()
    });
  }

  updateFormValues(rowData, originalFormValues) {
    let formValues = rowData;
    if (formValues.portfolio_id) {
      formValues.portfolio_id = formValues.portfolio_id.toString();
    }

    // Keep the drop down selections
    formValues.active_track_sel = originalFormValues.active_track_sel;
    formValues.active_track_sel.selected = originalFormValues.active_track_sel.options[rowData.active_track?1:0];
    return formValues;
  }

  onEditButtonClick(rowData) {
    console.info('onEditButtonClick: rowData=%o', rowData);
    this.setState({
      showDetailedViewModal: true,
      formValues: this.updateFormValues(rowData, this.state.formValues)
    });
  }

  onAddButtonClick() {
    console.info('onAddButtonClick: ...')
    this.setState({
      showDetailedViewModal: true,
      createNewStrategy: true
    });
  }

  onDeleteButtonClick(rowData) {
    console.info('onDeleteButtonClick: rowData=%o', rowData);
    
    this.setState({
      showDetailedViewModal: true,
      deleteStrategy: true,
      formValues: this.updateFormValues(rowData, this.state.formValues)
    });
  }

  showErrorMsg() {
    if (this.state.errorMsg !== "") {
      return <Alert variant={'danger'} > {this.state.errorMsg} </Alert>
    }
  }

  loadStrategies() {
    console.info('loadStrategies: Loading strategy_list...')
    let loadStrategiesCallback = function (httpStatus, json) {
      if (httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("loadStrategiesCallback: authentication expired?");
        return;
      }

      if (httpStatus !== 200) {
        console.error("loadStrategiesCallback: failure: http:%o", httpStatus);
        this.setState({
          errorMsg: "Failed to load strategy_list"
        })
        return;
      }

      let updateWatchListTicker = function (strategy) {
        if (this.props.watchListCache) {
          strategy.watchListTicker = this.props.watchListCache.getWatchListTicker(strategy.watchlist_id);
        }
      }

      json.forEach(updateWatchListTicker.bind(this));

      console.info("loadStrategiesCallback: json: %o", json);
      this.setState({
        isStrategyLoaded: true,
        strategy_list: json,
        errorMsg: ""
      });
    }

    getBackend().getStrategies(loadStrategiesCallback.bind(this));
  }

  createNewStrategy(form_values) {
    console.info('createNewStrategy: adding entry=%o', form_values)
    let createStrategyCallback = function (httpStatus, json) {
      if (httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("createStrategyCallback: authentication expired?");
        return;
      }

      if (httpStatus !== 200) {
        console.error("createStrategyCallback: failure: http:%o", httpStatus);
        this.setState({
          errorMsg: "Failed to add to strategy"
        })
        return;
      }

      console.info("createStrategyCallback: json: %o", json);

      //Reloading the strategy
      this.loadStrategies();
    }

    let strategy = {};
    strategy.strategy_type = form_values.strategy_type;
    strategy.active_track = form_values.active_track_sel.selected;

    // Below are optional values
    if (form_values.stop_loss.length) {
      // Send as float
      strategy.stop_loss = parseFloat(form_values.stop_loss);
    }

    if (form_values.profit_target.length) {
      // Send as float
      strategy.profit_target = parseFloat(form_values.profit_target);
    }
    if (form_values.portfolio_id.length) {
      // Send as int
      strategy.portfolio_id = parseInt(form_values.portfolio_id);
    }

    getBackend().createStrategy(strategy, createStrategyCallback.bind(this));
    this.onCloseDetailedViewModal();
  }

  updateStrategy(form_values) {
    console.info('updateStrategy: adding entry=%o', form_values)
    let updateStrategyCallback = function (httpStatus, json) {
      if (httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("updateStrategyCallback: authentication expired?");
        return;
      }

      if (httpStatus !== 200) {
        console.error("updateStrategyCallback: failure: http:%o", httpStatus);
        this.setState({
          errorMsg: "Failed to update strategy"
        })
        return;
      }

      console.info("updateStrategyCallback: json: %o", json);

      //Reloading the strategy
      this.loadStrategies();
    }

    let strategy = {};
    strategy.id = form_values.id;
    strategy.strategy_type = form_values.strategy_type;
    strategy.active_track = form_values.active_track_sel.selected;


    // Below are optional values
    if (form_values.stop_loss.length) {
      // Send as float
      strategy.stop_loss = parseFloat(form_values.stop_loss);
    }

    if (form_values.profit_target.length) {
      // Send as float
      strategy.profit_target = parseFloat(form_values.profit_target);
    }

    if (form_values.portfolio_id && form_values.portfolio_id.length) {
      // Send as int
      strategy.portfolio_id = parseInt(form_values.portfolio_id);
    } else {
      strategy.portfolio_id = null;
    }


    getBackend().updateStrategy(strategy, updateStrategyCallback.bind(this));
    this.onCloseDetailedViewModal();
  }

  deleteStrategy(strategy) {
    console.info('deleteStrategy: adding entry=%o', strategy)
    let deleteStrategyCallback = function (httpStatus, json) {
      if (httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("deleteStrategyCallback: authentication expired?");
        return;
      }

      if (httpStatus !== 200) {
        console.error("deleteStrategyCallback: failure: http:%o", httpStatus);
        this.setState({
          errorMsg: "Failed to delete to strategy"
        })
        return;
      }

      console.info("deleteStrategyCallback: json: %o", json);

      //Reloading the strategy
      this.loadStrategies();
    }

    getBackend().deleteStrategy(strategy, deleteStrategyCallback.bind(this));
    this.onCloseDetailedViewModal();
  }

  componentDidUpdate(prevProps) {
    console.info('componentDidUpdate..');

    if (this.props.watchListCache && !this.state.isStrategyLoaded) {
      // Load the scan
      this.loadStrategies();
      console.info('componentDidUpdate: loading strategies async');
    }
  }


  onFormValuesChange(event) {
    let updatedFormValues = { ...this.state.formValues, [event.target.id]: event.target.value };
    console.info('onFormValuesChange: updatedFormValues=%o ', updatedFormValues);
    this.setState({ formValues: updatedFormValues });
  }

  onFormValuesSelection(event) {
    let updatedSelection = this.state.formValues[event.target.id];
    updatedSelection.selected = updatedSelection.options[event.target.options.selectedIndex];

    let updatedFormValues = { ...this.state.formValues, [event.target.id]: updatedSelection};
    console.info('onFormValuesChange: updated_form_values=%o ', updatedFormValues);
    this.setState({ formValues: updatedFormValues });
  }

  showModalFormGroup(readOnly, controlId, label, value) {
    if (!value) value = "";

    return (
      <Form.Group as={Row} controlId={controlId}>
        <Form.Label column sm="4"> {label} </Form.Label>
        <Col sm="8">
          <Form.Control readOnly={readOnly} value={value} onChange={this.onFormValuesChange} />
        </Col>
      </Form.Group>
    );
  }


  showDropDown(controlId, label, dropdown_selection) {
    return (
      <Form.Group as={Row} controlId={controlId}>
        <Form.Label column sm="4"> {label} </Form.Label>
        <Col sm="8">

        <Form.Control as="select" selectedIndex={1} onChange={this.onFormValuesSelection}>
          {dropdown_selection.options.map((item, index) => {
            if (item === dropdown_selection.selected ) {
              // Show as the default value
              return (
                <option key={index} value={index} selected={"selected"}>{item}</option>
              )
            }

            return (<option key={index} value={index}>{item}</option>);
          })}
        </Form.Control>

        </Col>
      </Form.Group>

    );
  }

  showModalForm() {
    /*if (!this.state.formValues) {
      return <Alert variant={'danger'} > No row selected? </Alert>
    }*/
    let readOnly = false;
    if (this.state.deleteStrategy) readOnly = true;
    console.info('showModalForm: formValues=%o', this.state.formValues);
    //{ id: "", strategy_type: "", portfolio_id: "", stop_loss: "", profit_target: "", active_track: "" }
    return (
      <Form onSubmit={this.handleSubmit} >

        { this.showModalFormGroup(true, "creation_timestamp", "Create Timestamp", this.state.formValues.creation_timestamp)}
        { this.showModalFormGroup(true, "id", "ID", this.state.formValues.id)}
        { this.showModalFormGroup(readOnly, "strategy_type", "Strategy Type", this.state.formValues.strategy_type)}
        { this.showModalFormGroup(readOnly, "portfolio_id", "Portfolio id", this.state.formValues.portfolio_id)}
        { this.showModalFormGroup(readOnly, "stop_loss", "Stop Loss", this.state.formValues.stop_loss)}
        { this.showModalFormGroup(readOnly, "profit_target", "Profit target", this.state.formValues.profit_target)}
        { this.showDropDown("active_track_sel", "Active Track", this.state.formValues.active_track_sel)}


      </Form>
    );
  }

  onModalActionButtonClick() {
    console.info('onModalActionButtonClick: formValues=%o', this.state.formValues);

    if (this.state.createNewStrategy) {
      console.info('onModalActionButtonClick: call add');
      this.createNewStrategy(this.state.formValues);
      return;
    }

    if (this.state.deleteStrategy) {
      console.info('onModalActionButtonClick: call delete');
      this.deleteStrategy(this.state.formValues);
      return;
    }

    console.info('onModalActionButtonClick: call update');
    this.updateStrategy(this.state.formValues);
  }

  showModalActionButton() {
    if (this.state.createNewStrategy)
      return (
        <Button variant="primary" onClick={this.onModalActionButtonClick}>
          Add
        </Button>
      );

    if (this.state.deleteStrategy) {
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

  getActiveTrackString(rowData) {
    if (rowData.active_track)
      return 'true';

    return 'false';
  }

  render() {
    if (!this.props.auth.isAuthenticated) {
      console.info('Strategy:  not authenticated, redirecting to login page');
      return <Redirect to='/login' />;
    }

    if (!this.state.isStrategyLoaded) {
      return <Alert variant="primary"> Loading strategy_list... </Alert>;
    }

    console.info('render: this.showDetailedViewModal=%o...', this.state.showDetailedViewModal)

    const columns = [
      {
        Action: 'action', accessor: 'dummy',
        Cell: ({ row }) => (
          <ButtonGroup className="mr-2" aria-label="First group">
            <Button onClick={(e) => this.onEditButtonClick(row.original)}>Edit</Button>
            <Button onClick={(e) => this.onDeleteButtonClick(row.original)}>Delete</Button>
          </ButtonGroup>
        )
      },
      { Header: 'ID', accessor: 'id' },
      { Header: 'Strategy Type', accessor: 'strategy_type' },
      { Header: 'Portfolio Id', accessor: 'portfolio_id' },
      { Header: 'Watchlist Id', accessor: 'watchlist_id' },
      { Header: 'WL ticker', accessor: 'watchListTicker' },
      {
        Header: 'Active track', accessor: 'active_track',
        Cell: ({ row }) => (
          <> {this.getActiveTrackString(row.original)} </>
        )
      },
      { Header: 'Stop loss', accessor: 'stop_loss' },
      { Header: 'Profit target', accessor: 'profit_target' },
      { Header: 'Highest price', accessor: 'highest_price' },
      { Header: 'Lowest price', accessor: 'lowest_price' },
      { Header: 'Create Time', accessor: 'creation_timestamp' },
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
      <div className="Strategy">

        <ButtonToolbar aria-label="Toolbar with button groups">
          <ButtonGroup className="mr-2" aria-label="First group">
            <Button onClick={this.onAddButtonClick}> Add </Button>
          </ButtonGroup>
          <ButtonGroup className="mr-2" aria-label="Second group">
            <Button onClick={this.loadStrategies}> Refresh </Button>
          </ButtonGroup>
        </ButtonToolbar>

        { this.showErrorMsg()}

        <Table columns={columns} data={this.state.strategy_list} getTrProps={onRowClick} />

        { this.showModal()}

      </div>
    );
  }
}

