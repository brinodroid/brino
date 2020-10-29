import React from 'react';
import { Redirect } from 'react-router-dom';
import Alert from 'react-bootstrap/Alert';
import Button from 'react-bootstrap/Button';
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import ButtonToolbar from 'react-bootstrap/ButtonToolbar';
import Modal from 'react-bootstrap/Modal';

import { getBackend } from '../utils/Backend';
import Table from '../utils/Table';

export default class Home extends React.Component {
  constructor(props) {
    super(props);

    this.onEditButtonClick = this.onEditButtonClick.bind(this);
    this.onDeleteButtonClick = this.onDeleteButtonClick.bind(this);
    this.onAddButtonClick = this.onAddButtonClick.bind(this);
    this.loadWatchList = this.loadWatchList.bind(this);
    this.onCloseDetailedViewModal = this.onCloseDetailedViewModal.bind(this);
    this.showErrorMsg = this.showErrorMsg.bind(this);

    this.state = {
      isWatchListLoaded: false,
      errorMsg : '',
      watchList : null,
      showDetailedViewModal: false,
      addToWatchList: false,
      deleteToWatchList: false,
    }
  }

  onCloseDetailedViewModal() {
    console.info('onCloseDetailedViewModal: ...')
    this.setState({
      showDetailedViewModal: false
    });
  }

  onEditButtonClick () {
    console.info('onEditButtonClick: state=%o', this.state)
    this.setState({
      showDetailedViewModal: true
    });
  }

  onAddButtonClick() {
    console.info('onAddButtonClick: ...')
  }

  onDeleteButtonClick() {
    console.info('onDeleteButtonClick: ...')
  }

  showErrorMsg() {
    if (this.state.errorMsg !== "") {
      return <Alert variant={'danger'} > {this.state.errorMsg} </Alert>
    }
  }

  loadWatchList() {
    console.info('loadWatchList: Loading watchlist...')
    let watchListCallback = function (httpStatus, json) {
      if ( httpStatus === 401) {
        this.props.auth.setAuthenticationStatus(false);
        console.error("watchListCallback: authentication expired?");
        return;
      }

      if ( httpStatus !== 200) {
        console.error("watchListCallback: failure: http:%o", httpStatus);
        this.setState({
          errorMsg: "Failed to load watchlist"
        })
        return;
      }

      console.error("watchListCallback: json: %o", json);
      this.setState({
        isWatchListLoaded: true,
        watchList: json,
        errorMsg: ""
      });
    }

    getBackend().getWatchList(watchListCallback.bind(this));
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

    if (!this.state.isWatchListLoaded) {
      this.loadWatchList();
    }
  }

  render() {
    if ( !this.props.auth.isAuthenticated ) {
      console.info('Home:  not authenticated, redirecting to login page');
      return <Redirect to= '/login' />;
    }

    if ( !this.state.isWatchListLoaded) {
      return <Alert variant="primary"> Loading watchlist... </Alert>;
    }

    console.info('render: this.showDetailedViewModal=%o...', this.state.showDetailedViewModal)

    const columns = [
      { Header: 'ID',  accessor: 'id',
          Cell: ({value}) => (
              <ButtonGroup className="mr-2" aria-label="First group">
                <Button onClick={this.onEditButtonClick}>Edit</Button>
                <Button onClick={this.onDeleteButtonClick}>Delete</Button>
              </ButtonGroup>
            )},
      { Header: 'Asset Type', accessor: 'assetType'},
      { Header: 'Ticker', accessor: 'ticker'},
      { Header: 'Strike', accessor: 'optionStrike'},
      { Header: 'Expiry', accessor: 'optionExpiry'},
      { Header: 'Comment', accessor: 'comment'},
      { Header: 'Update Time', accessor: 'updateTimestamp'},
      { Header: 'Create Time', accessor: 'creationTimestamp'},
    ];

    return (
      <div className="home">

        <ButtonToolbar aria-label="Toolbar with button groups">
          <ButtonGroup className="mr-2" aria-label="First group">
            <Button onClick={this.onAddButtonClick}> Add </Button>
          </ButtonGroup>
          <ButtonGroup className="mr-2" aria-label="Second group">
            <Button onClick={this.loadWatchList}> Refresh </Button>
          </ButtonGroup>
        </ButtonToolbar>
        Welcome home {this.props.auth.loggedInUser}
        { this.showErrorMsg() }

        <Table columns={columns} data={this.state.watchList} />

        {/* animation=false added due to warning in console: https://github.com/react-bootstrap/react-bootstrap/issues/5075 */ }
        <Modal show={this.state.showDetailedViewModal} onHide={this.onCloseDetailedViewModal} animation={false}>
        <Modal.Header closeButton>
          <Modal.Title>Modal heading</Modal.Title>
        </Modal.Header>
        <Modal.Body>Woohoo, you're reading this text in a modal!</Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={this.onCloseDetailedViewModal}>
            Close
          </Button>
          <Button variant="primary" onClick={this.onCloseDetailedViewModal}>
            Save Changes
          </Button>
        </Modal.Footer>
      </Modal>
      </div>
    );
  }
}

