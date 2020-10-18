

let backendSingleton = null;
class Backend {
    constructor() {
        this.authenticate = this.authenticate.bind(this);
        this.isAuthenticated = this.isAuthenticated.bind(this);
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
                    callback(httpStatus, );
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
}

export function getBackend() {
    if (!backendSingleton) {
        backendSingleton = new Backend()
    }
    return backendSingleton;
}