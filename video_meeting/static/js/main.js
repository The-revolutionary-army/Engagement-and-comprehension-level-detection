const labelUsername = document.querySelector('#label-username');
const inputUsername = document.querySelector('#username');
const btnJoin = document.querySelector('#btn-join');
const state = document.querySelector('#state');
const chatContainer = document.querySelector('#chat');
const chat = document.querySelector('#message-list');
const videoContainer = document.querySelector('.video-container');
const localVideo = document.querySelector('#local-video');
const btnToggleAudio = document.querySelector('#btn-toggle-audio');
const btnToggleVideo = document.querySelector('#btn-toggle-video');
// const btnSendMsg = document.querySelector('#btn-send-message');
const account = document.querySelector('select');
const btnShowLocalVideo = document.getElementById('show-me');
var websocket;
var mapPeers = {};
var localStream;
var blob;
const csrftoken = getCookie('csrftoken');
var studentsList = document.getElementById('students-list');

var localStream = new MediaStream();
const constraints = {
    'video': true,
    'audio': true
}

changeAccount();

account.onchange = changeAccount;

btnShowLocalVideo.addEventListener('click', (e)=>{
    if (e.target.innerHTML == 'show me'){
        localVideo.parentNode.style.top = '10px';
        e.target.innerHTML = 'hide'
    } else {
        localVideo.parentNode.style.top = '-500px';
        e.target.innerHTML = 'show me'
    }
});

// join meeting
btnJoin.addEventListener('click', () => {
    if (account.value == 'lecturer' && !inputUsername.value.includes('lecturer: ')) {
        //TODO show participants
        inputUsername.value = 'lecturer: ' + inputUsername.value;
    }
    username = inputUsername.value;
    if (username == '') {
        return;
    }
    // disable join button and username field
    inputUsername.disabled = true;
    btnJoin.disabled = true;
    labelUsername.innerHTML = username;

    var videoLabelUsername = document.querySelector('#local-video + p');
    videoLabelUsername.innerHTML = '(me)';

    // connect to signaling server through websocket
    var url = window.location;
    var wsStart = 'ws://';

    if (url.protocol == 'https:') {
        wsStart = 'wss://';
    }
    var endPoint = wsStart + url.host + url.pathname;

    websocket = new WebSocket(endPoint);

    websocket.addEventListener('open', (e) => {
        showStatus('connected');
        console.log('connection opened');

        sendSignal('new-peer', {});
    });

    websocket.addEventListener('message', websocketOnMessage)

    websocket.addEventListener('close', (e) => {
        console.log('connection closed');
    });

    // if connection failed show the error
    websocket.addEventListener('error', (e) => {
        showStatus('failed to connect');
        console.error('failed to connect');
    });

    // if user is student
    if (account.value == 'student') {
        // create file for user states
        fetch('http://' + window.location.host + '/create/?username=' + labelUsername.innerHTML)
            .then(response => {
                if (response.status == 200) {
                    // showStatus('connected to server');
                }
            }).catch((error) => {
                // showStatus('can\'t connect to server');
                console.error('Error:', error);
            });
        // get video frames 
        getFrames();
    } else {
        studentsList.parentNode.style.display = 'flex';
        // get results
        setInterval(() => getResults(), 1000);
    }

});

// send message in chat
// btnSendMsg.addEventListener('click', sendMsgOnClick);
// var msgInput = document.querySelector('#msg');

// handle websocket operations
function websocketOnMessage(event) {
    var parsedData = JSON.parse(event.data);
    var peerUsername = parsedData['peer'];
    var action = parsedData['action'];

    // if received username is the same as user's skip
    if (username == peerUsername) {
        return;
    }

    var receiver_channel_name = parsedData['message']['receiver_channel_name'];

    if (action == 'new-peer') {
        createOfferer(peerUsername, receiver_channel_name);
        return;
    }

    if (action == 'new-offer') {
        var offer = parsedData['message']['sdp'];
        createAnswerer(offer, peerUsername, receiver_channel_name);
        return;
    }

    if (action == 'new-answer') {
        var answer = parsedData['message']['sdp'];
        var peer = mapPeers[peerUsername][0];

        peer.setRemoteDescription(answer);

        return;
    }
}

function sendMsgOnClick() {
    var message = msgInput.value;
    if (message == '') {
        return;
    }
    var li = document.createElement('li');
    li.appendChild(document.createTextNode('Me: ' + message));
    li.style.backgroundColor = 'rgba(124, 124, 124, 0.781)';
    chat.appendChild(li);

    var dataChannels = getDataChannels();
    //add username to message
    message = username + ': ' + message;

    //send message to peers
    for (index in dataChannels) {
        dataChannels[index].send(message);
    }

    //reset field content
    msgInput.value = '';
    //always scroll chat ro bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function sendSignal(action, message) {
    var jsonStr = JSON.stringify({
        'peer': username,
        'action': action,
        'message': message,
    });
    websocket.send(jsonStr);
}

function createOfferer(peerUsername, receiver_channel_name) {
    var peer = new RTCPeerConnection(null);
    addLocalTracks(peer);

    //creat data channel
    var dc = peer.createDataChannel('channel');
    dc.addEventListener('open', () => {
        console.log('connection opened');
    });
    dc.addEventListener('message', dcOnMessage);

    //create video for the received stream
    var remoteVideo = createVideo(peerUsername);
    setOnTrack(peer, remoteVideo);

    mapPeers[peerUsername] = [peer, dc];

    //delete video if peer disconnected
    peer.addEventListener('iceconnectionstatechange', () => {
        var iceConnectionState = peer.iceConnectionState;
        if (iceConnectionState === 'failed' || iceConnectionState === 'disconnected' || iceConnectionState === 'closed') {
            delete mapPeers[peerUsername];

            if (iceConnectionState != 'closed') {
                peer.close();
            }

            removeVideo(remoteVideo);
        }
    });

    peer.addEventListener('icecandidate', (event) => {
        if (event.candidate) {
            console.log('new ice candidate');
            return;
        }

        sendSignal('new-offer', {
            'sdp': peer.localDescription,
            'receiver_channel_name': receiver_channel_name
        });
    });

    peer.createOffer()
        .then(o => peer.setLocalDescription(o))
        .then(() => {
            console.log('local description set successfully')
        });
}

function createAnswerer(offer, peerUsername, receiver_channel_name) {

    var peer = new RTCPeerConnection(null);
    addLocalTracks(peer);

    //create video for received stream
    var remoteVideo = createVideo(peerUsername);
    setOnTrack(peer, remoteVideo);

    peer.addEventListener('datachannel', e => {
        peer.dc = e.channel;
        peer.dc.addEventListener('open', () => {
            console.log('connection opened');
        });
        peer.dc.addEventListener('message', dcOnMessage);

        mapPeers[peerUsername] = [peer, peer.dc];
    });

    //remove video if peer disconnected
    peer.addEventListener('iceconnectionstatechange', () => {
        var iceConnectionState = peer.iceConnectionState;
        if (iceConnectionState === 'failed' || iceConnectionState === 'disconnected' || iceConnectionState === 'closed') {
            delete mapPeers[peerUsername];

            if (iceConnectionState != 'closed') {
                peer.close();
            }

            removeVideo(remoteVideo);
        }
    });

    peer.addEventListener('icecandidate', (event) => {
        if (event.candidate) {
            console.log('new ice candidate');
            return;
        }

        sendSignal('new-answer', {
            'sdp': peer.localDescription,
            'receiver_channel_name': receiver_channel_name
        });
    });

    peer.setRemoteDescription(offer)
        .then(() => {
            console.log('remote description set successfully for %s', peerUsername);

            return peer.createAnswer();
        })
        .then(s => {
            console.log('answer created');
            peer.setLocalDescription(s);
        })

}

function addLocalTracks(peer) {
    localStream.getTracks().forEach(track => {
        peer.addTrack(track, localStream);
    });
    return;
}

function dcOnMessage(event) {
    var msg = event.data;
    var li = document.createElement('li');
    li.appendChild(document.createTextNode(msg));
    chat.appendChild(li);
    //always scroll chat ro bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function createVideo(peerUsername) {
    var remoteVideo = document.createElement('video');
    remoteVideo.id = peerUsername + '-video';
    remoteVideo.autoplay = true;
    remoteVideo.playsInline = true;

    var labelUsername = document.createElement('p');
    labelUsername.classList.add('username');
    labelUsername.appendChild(document.createTextNode(peerUsername));

    var states = document.createElement('p');
    states.id = 'states';
    states.appendChild(document.createTextNode(''));

    var videoWrapper = document.createElement('div');
    videoWrapper.classList.add('remote-video-container');
    videoWrapper.appendChild(remoteVideo);
    videoWrapper.appendChild(labelUsername);
    videoWrapper.appendChild(states);
    if (peerUsername.includes('lecturer: ')) {
        videoContainer.appendChild(videoWrapper);
    }

    return remoteVideo;
}

function setOnTrack(peer, remoteVideo) {
    var remoteStream = new MediaStream();
    remoteVideo.srcObject = remoteStream;
    peer.addEventListener('track', async (event) => {
        remoteStream.addTrack(event.track, remoteStream);
    });
}

function removeVideo(video) {
    var videoWrapper = video.parentNode;
    videoWrapper.parentNode.removeChild(videoWrapper);
}

function getDataChannels() {
    var dataChannels = [];

    for (peerUsername in mapPeers) {
        var dataChannel = mapPeers[peerUsername][1];

        dataChannels.push(dataChannel);
    }

    return dataChannels;
}

function getCookie(name) { //getting csrf token from cookies to use in ajax
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function getFrames() {
    var canvas = document.createElement('canvas');
    canvas.width = localVideo.videoWidth;
    canvas.height = localVideo.videoHeight;
    var ctx = canvas.getContext('2d');
    setInterval(() => {
        ctx.drawImage(localVideo, 0, 0, canvas.width, canvas.height);
        canvas.toBlob(uploadFrame, 'image/jpeg');
    }, 1000 / 25)
}

function uploadFrame(frame) {
    var url = 'http://' + window.location.host + '/model/';
    // upload file to server
    var fd = new FormData();
    fd.append(labelUsername.innerHTML, frame);
    fetch(url, {
        method: 'POST',
        mode: 'cors',
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': csrftoken
        },
        body: fd
    }).then(response => {
        if (response.status == 200) {
            // console.log('uploaded')
            // showStatus('connected');
        }
    }).catch((error) => {
        // showStatus('can\'t connect to server');
        console.error('Error:', error);
    });
}

function changeAccount() {
    if (account.value == 'lecturer') {
        btnToggleVideo.style.display = 'inline';
        // set stream to screen
        var userMedia = navigator.mediaDevices.getUserMedia({ 'audio': true, 'video': { mediaSource: "screen" } })
            .then(stream => {
                localStream = stream;
                localVideo.srcObject = localStream;
                localVideo.muted = true;

                var audioTracks = stream.getAudioTracks();
                var videoTracks = stream.getVideoTracks();

                audioTracks[0].enabled = true;
                videoTracks[0].enabled = true;

                // toggle audio
                btnToggleAudio.addEventListener('click', () => {
                    audioTracks[0].enabled = !audioTracks[0].enabled;

                    if (audioTracks[0].enabled) {
                        btnToggleAudio.innerHTML = 'mute';
                        btnToggleAudio.style.color = 'green';
                        return;
                    }
                    btnToggleAudio.innerHTML = 'unmute';

                });

                //toggle video
                btnToggleVideo.addEventListener('click', () => {
                    videoTracks[0].enabled = !videoTracks[0].enabled;

                    if (videoTracks[0].enabled) {
                        btnToggleVideo.innerHTML = 'stop sharing';
                        btnToggleVideo.style.color = 'green';
                        return;
                    }
                    btnToggleVideo.innerHTML = 'share screen';

                });
            }).catch(error => {
                showStatus('can\'t have permission to share screen');
                console.log(error);
            });
    } else {
        btnToggleVideo.style.display = 'none';
        navigator.mediaDevices.getUserMedia(constraints)
            .then(stream => {
                localStream = stream;
                localVideo.srcObject = localStream;
                localVideo.muted = true;

                var audioTracks = stream.getAudioTracks();
                var videoTracks = stream.getVideoTracks();

                audioTracks[0].enabled = true;
                videoTracks[0].enabled = true;

                // toggle audio
                btnToggleAudio.addEventListener('click', () => {
                    audioTracks[0].enabled = !audioTracks[0].enabled;

                    if (audioTracks[0].enabled) {
                        btnToggleAudio.innerHTML = 'mute';
                        btnToggleAudio.style.color = 'green';
                        return;
                    }
                    btnToggleAudio.innerHTML = 'unmute';

                });
            }).catch(error => {
                showStatus('error accessing camera or mic');
                console.log(error)
            });
    }
}

function getResults() {
    fetch('http://' + window.location.host + '/states/', {
        method: 'GET',
        mode: 'cors',
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': csrftoken
        }
    }).then(response => {
        if (response.status == 200) {
            // showStatus('connected to server');
            return response.json();
        }
    }).then(data => {
        if (data) {
            studentsList.innerHTML = '';
            for (usr of data) {
		var studentStates = document.createElement('li');
                studentStates.innerHTML = `
                    <div class="user-img"><img src="../static/images/user.svg" alt="user-image"></div>
                    <div class="states-card">
                        <p class="capitalize">${usr.username}</p>
                        <div class="states-values">
                            <span class="state">${(usr.engagement * 100).toFixed(2)}</span>
                            <span class="state">${(usr.confusion * 100).toFixed(2)}</span>
                            <span class="state">${(usr.boredom * 100).toFixed(2)}</span>
                            <span class="state">${(usr.frustration * 100).toFixed(2)}</span>
                            <span class="state">${(usr.comprehension * 100).toFixed(2)}</span>
                        </div>
                    </div>
                    <div class="user-img"><img src="../static/images/msg.svg" alt="message"></div>
                    `;
                studentsList.appendChild(studentStates);

            }
        }
    }).catch((error) => {
        // showStatus('can\'t connect to server');
        console.error('Error:', error);
    });
}

function showStatus(msg) {
    state.innerHTML = msg;
    state.style.height = 'unset';
    state.style.padding = '2px';
    setTimeout(() => {
        state.innerHTML = '';
        state.style.height = 0;
        state.style.padding = 0;
    }, 4000)
}