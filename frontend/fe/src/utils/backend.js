

let backendSingleton = null;
class Backend {
    constructor() {
        this.authenticate = this.authenticate.bind(this);
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
                localStorage.setItem('token', json.token);
                callback(httpStatus);
            })
            .catch (error => {
                console.error("authenticate: error %o", error);
                callback(httpStatus);
            });
    }
}

export function getBackend() {
    if (!backendSingleton) {
        backendSingleton = new Backend()
    }
    return backendSingleton;
}