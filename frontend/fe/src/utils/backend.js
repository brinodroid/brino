

let backendSingleton = null;
class Backend {
    constructor() {
        this.authenticate = this.authenticate.bind(this);
        this.isAuthenticated = this.isAuthenticated.bind(this);
        this.clearAuthentication = this.clearAuthentication.bind(this);
        this.getLoggedInUser = this.getLoggedInUser.bind(this);
        this.getConfiguration = this.getConfiguration.bind(this);
    }

    authenticate(username, password, callback) {
        let httpStatus;
        let authenticateRequest = {};
        authenticateRequest.username = username;
        authenticateRequest.password = password;

        fetch('http://localhost:8000/token-auth/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
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
        let httpStatus;

        fetch('http://localhost:8000/brAuth/user', {
            headers: {
                Authorization: `JWT ${localStorage.getItem('token')}`
            }
            })
            .then(response => {
                httpStatus = response.status;
                return response.json();
            })
            .then(json => {
                if (httpStatus !== 200) {
                    console.error("getLoggedInUser: json=%o", json);
                    callback(httpStatus, undefined);
                    return;
                }
                callback(httpStatus, json.username);
            })
            .catch (error => {
                console.error("getLoggedInUser: error=%o", error);
                callback(httpStatus, undefined);
            });
    }

    getConfiguration(callback) {
        let httpStatus;

        fetch('http://localhost:8000/brSetting/config', {
            headers: {
                Authorization: `JWT ${localStorage.getItem('token')}`
            }
            })
            .then(response => {
                httpStatus = response.status;
                return response.json();
            })
            .then(json => {
                if (httpStatus !== 200) {
                    console.error("getConfiguration: json=%o", json);
                    callback(httpStatus, undefined);
                    return;
                }
                callback(httpStatus, json);
            })
            .catch (error => {
                console.error("getConfiguration: error=%o", error);
                callback(httpStatus, undefined);
            });
    }

}

export function getBackend() {
    if (!backendSingleton) {
        backendSingleton = new Backend()
    }
    return backendSingleton;
}