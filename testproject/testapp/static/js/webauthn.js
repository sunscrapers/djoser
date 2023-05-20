function b64enc(buf) {
    return base64js.fromByteArray(buf)
       .replace(/\+/g, "-")
       .replace(/\//g, "_")
       .replace(/=/g, "");
}

function b64RawEnc(buf) {
    return base64js.fromByteArray(buf)
        .replace(/\+/g, "-")
        .replace(/\//g, "_");
}

function hexEncode(buf) {
    return Array.from(buf)
        .map(function(x) {
            return ("0" + x.toString(16)).substr(-2);
        })
        .join("");
}

const transformCredentialRequestOptions = (credentialRequestOptionsFromServer) => {
    let {challenge, allowCredentials} = credentialRequestOptionsFromServer;

    challenge = Uint8Array.from(
        atob(challenge), c => c.charCodeAt(0));

    allowCredentials = allowCredentials.map(credentialDescriptor => {
        let {id} = credentialDescriptor;
        id = id.replace(/\_/g, "/").replace(/\-/g, "+");
        id = Uint8Array.from(atob(id), c => c.charCodeAt(0));
        return Object.assign({}, credentialDescriptor, {id});
    });

    const transformedCredentialRequestOptions = Object.assign(
        {},
        credentialRequestOptionsFromServer,
        {challenge, allowCredentials});

    return transformedCredentialRequestOptions;
};

const transformCredentialCreateOptions = (credentialCreateOptionsFromServer) => {
    let {challenge, user} = credentialCreateOptionsFromServer;
    user.id = Uint8Array.from(
        atob(credentialCreateOptionsFromServer.user.id), c => c.charCodeAt(0));

    challenge = Uint8Array.from(
        atob(credentialCreateOptionsFromServer.challenge), c => c.charCodeAt(0));

    const transformedCredentialCreateOptions = Object.assign(
            {}, credentialCreateOptionsFromServer,
            {challenge, user});

    return transformedCredentialCreateOptions;
}

const transformNewAssertionForServer = (newAssertion) => {
    const attObj = new Uint8Array(
        newAssertion.response.attestationObject);
    const clientDataJSON = new Uint8Array(
        newAssertion.response.clientDataJSON);
    const rawId = new Uint8Array(
        newAssertion.rawId);

    const registrationClientExtensions = newAssertion.getClientExtensionResults();

    return {
        id: newAssertion.id,
        rawId: b64enc(rawId),
        type: newAssertion.type,
        attObj: b64enc(attObj),
        clientData: b64enc(clientDataJSON),
        registrationClientExtensions: JSON.stringify(registrationClientExtensions)
    };
}

const transformAssertionForServer = (newAssertion) => {
    const authData = new Uint8Array(newAssertion.response.authenticatorData);
    const clientDataJSON = new Uint8Array(newAssertion.response.clientDataJSON);
    const rawId = new Uint8Array(newAssertion.rawId);
    const sig = new Uint8Array(newAssertion.response.signature);
    const assertionClientExtensions = newAssertion.getClientExtensionResults();

    return {
        id: newAssertion.id,
        rawId: b64enc(rawId),
        type: newAssertion.type,
        authData: b64RawEnc(authData),
        clientData: b64RawEnc(clientDataJSON),
        signature: hexEncode(sig),
        assertionClientExtensions: JSON.stringify(assertionClientExtensions)
    };
};

async function post(path, data) {
    const response = await fetch(path, {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
    });
    if (!response.ok) {
        if (response.status == 400) {
            const errors = await response.json();
            alert('Bad request:\n' + JSON.stringify(errors));
        } else {
            alert('Something went wrong.');
        }
    } else {
        return await response.json();
    }
}

/* webauthn signup */
let userKey;

async function getCredentialOptions(username, displayName) {
    const rawCredentialOptions = await post('/webauthn/signup_request/', {
        username: username,
        display_name: displayName,
    });
    userKey = rawCredentialOptions.user.id;
    return transformCredentialCreateOptions(rawCredentialOptions);
}

async function confirmAssertionForServer(assertionForServer) {
    return await post('/webauthn/signup/' + userKey + '/', assertionForServer);
}

async function handleSignup(e) {
    e.preventDefault();

    const username = document.getElementById('signup-username').value;
    const displayName = document.getElementById('signup-displayname').value;

    const credentialOptions = await getCredentialOptions(username, displayName);

    const rawAssertionForServer = await navigator.credentials.create({
        publicKey: credentialOptions,
    });
    let assertionForServer = transformNewAssertionForServer(rawAssertionForServer);
    assertionForServer.username = username;
    const response = await confirmAssertionForServer(assertionForServer);

    if (!!response) {
        alert('Successfully signed up!\nYou can now log in using your username: ' + username);
    }
}

/* webauthn login */
async function getAssertionOptions(username) {
    const rawAssertionOptions = await post('/webauthn/login_request/', {
        username: username,
    });
    return transformCredentialRequestOptions(rawAssertionOptions);
}

async function handleLogin(e) {
    e.preventDefault();

    const username = document.getElementById('login-username').value;

    const assertionOptions = await getAssertionOptions(username);

    const assertion = await navigator.credentials.get({
        publicKey: assertionOptions,
    });

    const rawAssertion = transformAssertionForServer(assertion);

    let data = rawAssertion;
    data.username = username

    const response = await post('/webauthn/login/', rawAssertion);
    if (!!response) {
        alert("Successfully logged in! Your token is: " + response.auth_token);
    }
}

document.getElementById('signup-form').addEventListener('submit', handleSignup);
document.getElementById('login-form').addEventListener('submit', handleLogin);
