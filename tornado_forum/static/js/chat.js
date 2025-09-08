let socket;
let currentRoomId;
let currentRecipient = '';

const fetchPreviousConversation = ()=>{
    const userList = document.getElementById('user-list')
    const currentUserID = document.querySelector('.main-chat-content').dataset.userId;
    console.log(currentUserID)
    fetch(`/api/users/${currentUserID}`)
        .then(response => response.json())
        .then(data => {
            data.users.forEach(user => {
                const li = document.createElement('li');
                li.textContent = user.username;
                li.dataset.userId = user.id;
                li.dataset.username = user.username;
                li.addEventListener('click', () => startChat(user.id, user.username));
                userList.appendChild(li);
            });
        });
}

function startChat(userId, username) {
    console.log(`The value of _xsrf cookie is ${getCookie('csrftoken')}`)
    fetch('/api/chat/dm', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-XSRFToken': getCookie('_xsrf') 
        },
        body: JSON.stringify({ user_id: userId })
    })
    .then(response => response.json())
    .then(data => {
        window.location.href = '/chat/' + data.room_name;
    });
}

function connectToWebSocket(roomId) {
    const messageList = document.getElementById('message-list');
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    socket = new WebSocket(`${wsProtocol}//${window.location.host}/ws`);

    socket.onopen = function() {
        console.log('WebSocket connection established.');
        currentRoomId = roomId;
        socket.send(JSON.stringify({
            type: 'join',
            room_id: roomId
        }));
    };

    socket.onmessage = function(event) {
        const msg = JSON.parse(event.data);
        switch (msg.type) {
            case 'history':
                messageList.innerHTML = '';
                msg.messages.forEach(m => {
                    appendMessage(m.sender_id, m.data, m.created_on);
                });
                break;
            case 'chat':
                appendMessage(msg.user_id, msg.data, new Date().toISOString());
                break;
            case 'joined':
                console.log(`Joined room ${msg.room_id}`);
                break;
            default:
                console.log('Received unknown message type:', msg.type);
        }
    };

    socket.onclose = function() {
        console.log('WebSocket connection closed.');
    };

    socket.onerror = function(error) {
        console.error('WebSocket error:', error);
    };
}

function appendMessage(senderId, data, timestamp) {
    const messageList = document.getElementById('message-list');
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message');
    msgDiv.innerHTML = `<p>${data}</p><span class="timestamp">${new Date(timestamp).toLocaleTimeString()}</span>`;
    messageList.appendChild(msgDiv);
    messageList.scrollTop = messageList.scrollHeight;
}

function getCookie(name) {
    let r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


document.addEventListener('DOMContentLoaded', function() {
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');

    messageForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const message = messageInput.value;
        if (message && socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({
                type: 'send',
                room_id: currentRoomId,
                content: message
            }));
            messageInput.value = '';
        }
    });
});