
let backendSingleton = null;
class Backend {
  constructor() {
    this.authenticate = this.authenticate.bind(this);
    this.isAuthenticated = this.isAuthenticated.bind(this);
    this.clearAuthentication = this.clearAuthentication.bind(this);

    this.getLoggedInUser = this.getLoggedInUser.bind(this);
    this.getConfiguration = this.getConfiguration.bind(this);

    this.getWatchList = this.getWatchList.bind(this);
    this.createWatchListEntry = this.createWatchListEntry.bind(this);
    this.deleteFromWatchList = this.deleteFromWatchList.bind(this);
    this.updateWatchList = this.updateWatchList.bind(this);

    this.getBgtask = this.getBgtask.bind(this);
    this.createBgtask = this.createBgtask.bind(this);
    this.deleteBgtask = this.deleteBgtask.bind(this);
    this.updateBgtask = this.updateBgtask.bind(this);

    this.getPortFolio = this.getPortFolio.bind(this);
    this.createPortFolio = this.createPortFolio.bind(this);
    this.deletePortFolio = this.deletePortFolio.bind(this);
    this.updatePortFolio = this.updatePortFolio.bind(this);

    this.getWithToken = this.getWithToken.bind(this);
    this.postWithToken = this.postWithToken.bind(this);
    this.deleteWithToken = this.deleteWithToken.bind(this);
    this.putWithToken = this.putWithToken.bind(this);
    this.getURL = this.getURL.bind(this);
  }

  authenticate(username, password, callback) {
    let httpStatus;
    let authenticateRequest = {};
    authenticateRequest.username = username;
    authenticateRequest.password = password;

    fetch( this.getURL() + 'token-auth/', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(authenticateRequest)
    })
    .then(response => {
      httpStatus = response.status;
      return response.json();
    })
    .then(json => {
      if (httpStatus !== 200) {
        console.error("authenticate: json=%o", json);
        callback(httpStatus);
        return;
      }
      localStorage.setItem('token', json.token);
      callback(httpStatus);
    })
    .catch (error => {
      console.error("authenticate: error %o", error);
      callback(httpStatus);
    });
  }

  isAuthenticated() {
    let token = localStorage.getItem('token');
    if (!token || 0 === token.length) {
      return false;
    }
    return true;
  }

  clearAuthentication() {
    localStorage.removeItem('token');
  }

  getLoggedInUser(callback) {
    this.getWithToken('brAuth/user', callback);
  }

  getConfiguration(callback) {
    this.getWithToken('brSetting/config', callback);
  }

  getWatchList(callback) {
    this.getWithToken('brCore/watchlist', callback);
  }

  createWatchListEntry(watchListEntry, callback) {
    this.postWithToken('brCore/watchlist/', watchListEntry, callback);
  }

  deleteFromWatchList(watchListEntry, callback) {
    this.deleteWithToken('brCore/watchlist/'+watchListEntry.id, callback);
  }

  updateWatchList(watchListEntry, callback) {
    this.putWithToken('brCore/watchlist/'+watchListEntry.id, watchListEntry, callback);
  }

  getBgtask(callback) {
    this.getWithToken('brCore/bgtask', callback);
  }

  createBgtask(bgtask, callback) {
    // These are readonly fields and hence need not be passed during creation
    delete bgtask.updateTimestamp;
    delete bgtask.actionResult;
    delete bgtask.status;
    this.postWithToken('brCore/bgtask/', bgtask, callback);
  }

  deleteBgtask(bgtask, callback) {
    this.deleteWithToken('brCore/bgtask/'+bgtask.id, callback);
  }

  updateBgtask(bgtask, callback) {
    this.putWithToken('brCore/bgtask/'+bgtask.id, bgtask, callback);
  }

  getPortFolio(callback) {
    this.getWithToken('brCore/portfolio', callback);
  }

  createPortFolio(portfolio, callback) {
    // The below fields are not relavent during creation
    delete portfolio.updateTimestamp;
    delete portfolio.exitDate;
    delete portfolio.exitPrice;
    this.postWithToken('brCore/portfolio/', portfolio, callback);
  }

  deletePortFolio(portfolio, callback) {
    this.deleteWithToken('brCore/portfolio/'+portfolio.id, callback);
  }

  updatePortFolio(portfolio, callback) {
    this.putWithToken('brCore/portfolio/'+portfolio.id, portfolio, callback);
  }

  deleteWithToken(api, callback) {
    let httpStatus;
    let url = this.getURL() + api;

    fetch(url, {
      method: 'DELETE',
      headers: {'Content-Type': 'application/json', Authorization: `JWT ${localStorage.getItem('token')}`},
    })
    .then(response => {
      httpStatus = response.status;
      callback(httpStatus, undefined);
    })
    .catch (error => {
      console.error("deleteWithToken: url=%o error=%o", url, error);
      callback(httpStatus, undefined);
    });
  }

  putWithToken(api, data, callback) {
    let httpStatus;
    let url = this.getURL() + api;

    fetch(url, {
      method: 'PUT',
      headers: {'Content-Type': 'application/json', Authorization: `JWT ${localStorage.getItem('token')}`},
      body: JSON.stringify(data)
    })
    .then(response => {
      httpStatus = response.status;
      return response.json();
    })
    .then(json => {
      if (httpStatus !== 200) {
        console.error("putWithToken: url=%o json=%o", url, json);
        callback(httpStatus, json);
        return;
      }
      callback(httpStatus);
    })
    .catch (error => {
      console.error("putWithToken: url=%o error=%o", url, error);
      callback(httpStatus, undefined);
    });
  }

  postWithToken(api, data, callback) {
    let httpStatus;
    let url = this.getURL() + api;

    fetch(url, {
      method: 'POST',
      headers: {'Content-Type': 'application/json', Authorization: `JWT ${localStorage.getItem('token')}`},
      body: JSON.stringify(data)
    })
    .then(response => {
      httpStatus = response.status;
      return response.json();
    })
    .then(json => {
      if (httpStatus !== 200) {
        console.error("postWithToken: url=%o json=%o", url, json);
        callback(httpStatus, json);
        return;
      }
      callback(httpStatus);
    })
    .catch (error => {
      console.error("postWithToken: url=%o error=%o", url, error);
      callback(httpStatus, undefined);
    });
  }

  getWithToken(api, callback) {
    let httpStatus;
    let url = this.getURL() + api;

    fetch(url, {
      headers: {Authorization: `JWT ${localStorage.getItem('token')}`}
    })
    .then(response => {
      httpStatus = response.status;
      return response.json();
    })
    .then(json => {
      if (httpStatus !== 200) {
        console.error("getWithToken: url=%o json=%o", url, json);
        callback(httpStatus, undefined);
        return;
      }
      callback(httpStatus, json);
    })
    .catch (error => {
      console.error("getWithToken: url=%o error=%o", url, error);
      callback(httpStatus, undefined);
    });
  }

  getURL() {
    return window.location.protocol + '//' + window.location.hostname + ':8000/';
  }
}

export function getBackend() {
  if (!backendSingleton) {
    backendSingleton = new Backend()
  }
  return backendSingleton;
}

