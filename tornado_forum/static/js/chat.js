document.addEventListener('DOMContentLoaded', function() {
    const userList = document.getElementById('user-list');
    const messageList = document.getElementById('message-list');
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const chatHeader = document.getElementById('chat-header');

    let socket;
    let currentRoomId;
    let currentRecipient = '';

    // Fetch users and populate the sidebar
    fetch('/api/users')
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

    function startChat(userId, username) {
        // Close existing socket if open
        if (socket) {
            socket.close();
        }
        
        messageList.innerHTML = ''; // Clear previous messages
        currentRecipient = username;
        chatHeader.textContent = `Chat with ${username}`;

        // Get a room for the DM
        fetch('/api/chat/dm', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Tornado's XSRF protection requires this header.
                'X-XSRFToken': getCookie('_xsrf') 
            },
            body: JSON.stringify({ user_id: userId })
        })
        .then(response => response.json())
        .then(data => {
            currentRoomId = data.room_id;
            connectToWebSocket(currentRoomId);
            messageForm.style.display = 'flex';
        });
    }

    function connectToWebSocket(roomId) {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        socket = new WebSocket(`${wsProtocol}//${window.location.host}/ws`);

        socket.onopen = function() {
            console.log('WebSocket connection established.');
            // Join the room
            socket.send(JSON.stringify({
                type: 'join',
                room_id: roomId
            }));
        };

        socket.onmessage = function(event) {
            const msg = JSON.parse(event.data);
            switch (msg.type) {
                case 'history':
                    messageList.innerHTML = ''; // Clear again before loading history
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

    messageForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const message = messageInput.value;
        if (message && socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({
                type: 'send',
                room_id: currentRoomId,
                content: message // 'content' was fixed on backend
            }));
            // // Optimistically add the message to the UI
            // const currentUserId = document.body.dataset.userId;
            // appendMessage(currentUserId, message, new Date().toISOString());
            messageInput.value = '';
        }
    });

    function appendMessage(senderId, data, timestamp) {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message');
        // This is a simplification. In a real app, you'd get current user's ID.
        // For now, we just show the data.
        msgDiv.innerHTML = `<p>${data}</p><span class="timestamp">${new Date(timestamp).toLocaleTimeString()}</span>`;
        messageList.appendChild(msgDiv);
        messageList.scrollTop = messageList.scrollHeight;
    }
});