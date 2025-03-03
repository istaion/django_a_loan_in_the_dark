// Toggle online users overlay
function toggleOnlineUsers() {
    const overlay = document.getElementById('online-users-overlay');
    overlay.classList.toggle('show');
}

// Format date: converts "DD-MM-YYYY HH:MM" to "DD/MM HH:MM"
function formatDate(dateStr) {
    if (!dateStr) return '';
    const parts = dateStr.split(' ');
    if (parts.length !== 2) return dateStr;
    
    const dateParts = parts[0].split('-');
    if (dateParts.length !== 3) return dateStr;
    
    return `${dateParts[0]}/${dateParts[1]} ${parts[1]}`;
}

// Function to reply to a message
function replyToMessage(messageId, userId, userEmail) {
    document.getElementById('recipient-id').value = userId;
    document.getElementById('reply-to-id').value = messageId;
    
    const username = userEmail.split('@')[0];
    document.getElementById('reply-user').textContent = username;
    document.getElementById('reply-info').style.display = 'block';
    
    // Focus on input field
    document.getElementById('private-input').focus();
}

// Function to cancel reply
function cancelReply() {
    document.getElementById('recipient-id').value = '';
    document.getElementById('reply-to-id').value = '';
    document.getElementById('reply-info').style.display = 'none';
}

// Close the overlay when clicking outside of it
document.addEventListener('click', function(event) {
    const overlay = document.getElementById('online-users-overlay');
    const button = document.querySelector('.online-users-button');
    
    if (overlay.classList.contains('show') && 
        !overlay.contains(event.target) && 
        !button.contains(event.target)) {
        overlay.classList.remove('show');
    }
});

document.addEventListener('DOMContentLoaded', function() {
    console.log("Chat script initialized");
    
    // DOM elements
    const generalMessages = document.getElementById('general-messages');
    const generalForm = document.getElementById('general-form');
    const generalInput = document.getElementById('general-input');
    
    const privateMessages = document.getElementById('private-messages');
    const privateForm = document.getElementById('private-form');
    const privateInput = document.getElementById('private-input');
    const recipientId = document.getElementById('recipient-id');
    const replyToId = document.getElementById('reply-to-id');
    const replyInfo = document.getElementById('reply-info');
    const replyUser = document.getElementById('reply-user');
    
    const onlineUsers = document.getElementById('online-users');
    const onlineCount = document.getElementById('online-count');
    const chatContainer = document.getElementById('chat-container');
    
    // User data
    const currentUserEmail = chatContainer.dataset.userEmail;
    const currentUserId = chatContainer.dataset.userId;
    const isStaff = chatContainer.dataset.isStaff === 'true';
    
    console.log("User info:", currentUserEmail, isStaff);
    
    // Scroll to bottom of messages
    generalMessages.scrollTop = generalMessages.scrollHeight;
    privateMessages.scrollTop = privateMessages.scrollHeight;
    
    // Format existing usernames
    function formatExistingUsernames() {
        document.querySelectorAll('.message strong').forEach(element => {
            const text = element.childNodes[0].textContent.trim();
            if (text.includes('@')) {
                const username = text.split('@')[0];
                element.childNodes[0].textContent = username + ' ';
            }
        });
    }
    
    formatExistingUsernames();
    
    // Online users list
    const onlineUsersList = new Set();
    
    // Add current user
    if (currentUserEmail) {
        onlineUsersList.add(currentUserEmail);
        updateOnlineUsersList();
    }
    
    // Connect WebSocket with error handling and reconnection
    let chatSocket;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5;
    
    function connectWebSocket() {
        console.log("Connecting to WebSocket...");
        
        try {
            // Create new WebSocket connection
            chatSocket = new WebSocket(
                'ws://' + window.location.host + '/ws/chat/'
            );
            
            chatSocket.onopen = function(e) {
                console.log('WebSocket connection established');
                reconnectAttempts = 0; // Reset attempt counter
                
                // Announce user joining chat
                if (currentUserEmail) {
                    try {
                        chatSocket.send(JSON.stringify({
                            'type': 'user_join',
                            'user': currentUserEmail
                        }));
                    } catch (error) {
                        console.error("Error sending join event:", error);
                    }
                }
            };
            
            chatSocket.onmessage = function(e) {
                try {
                    const data = JSON.parse(e.data);
                    
                    if (data.type === 'message') {
                        // Public message
                        const message = data.message;
                        const username = message.user_email.split('@')[0];
                        const formattedDate = formatDate(message.timestamp);
                        
                        const messageElement = document.createElement('div');
                        messageElement.className = `message ${message.is_staff ? 'staff-message' : 'user-message'} p-2 mb-2`;
                        messageElement.dataset.messageId = message.id;
                        
                        messageElement.innerHTML = `
                            <strong class="text-white">
                                ${username} 
                                ${message.is_staff ? 
                                    '<span class="badge bg-warning text-dark">conseiller</span>' : 
                                    '<span class="role-badge">utilisateur</span>'
                                }
                            </strong>
                            <span class="message-timestamp">${formattedDate}</span>
                            <div class="text-white">${message.content}</div>
                        `;
                        
                        generalMessages.appendChild(messageElement);
                        generalMessages.scrollTop = generalMessages.scrollHeight;
                    }
                    else if (data.type === 'private_message') {
                        // Private message
                        const message = data.message;
                        const username = message.user_email.split('@')[0];
                        const formattedDate = formatDate(message.timestamp);
                        
                        // Check if this message concerns us
                        if (isStaff || message.user_email === currentUserEmail || 
                            message.recipient_email === currentUserEmail) {
                            
                            const messageElement = document.createElement('div');
                            messageElement.className = `message ${message.is_staff ? 'staff-message' : 'user-message'} p-2 mb-2`;
                            messageElement.dataset.messageId = message.id;
                            messageElement.dataset.userId = message.user_id;
                            messageElement.dataset.userEmail = message.user_email;
                            
                            let replyButton = '';
                            if (isStaff && !message.is_staff) {
                                replyButton = `
                                    <div class="reply-actions mt-1">
                                        <button class="reply-btn btn btn-sm btn-outline-light" onclick="replyToMessage('${message.id}', '${message.user_id}', '${message.user_email}')">Répondre</button>
                                    </div>
                                `;
                            }
                            
                            messageElement.innerHTML = `
                                <strong class="text-white">
                                    ${username} 
                                    ${message.is_staff ? 
                                        '<span class="badge bg-warning text-dark">conseiller</span>' : 
                                        '<span class="role-badge">utilisateur</span>'
                                    }
                                </strong>
                                <span class="message-timestamp">${formattedDate}</span>
                                <div class="text-white">${message.content}</div>
                                ${replyButton}
                            `;
                            
                            privateMessages.appendChild(messageElement);
                            privateMessages.scrollTop = privateMessages.scrollHeight;
                        }
                    }
                    else if (data.type === 'user_join') {
                        // User joining
                        if (!onlineUsersList.has(data.user)) {
                            onlineUsersList.add(data.user);
                            updateOnlineUsersList();
                            
                            const username = data.user.split('@')[0];
                            const joinMessage = document.createElement('div');
                            joinMessage.className = 'text-center text-muted small my-2';
                            joinMessage.textContent = `${username} a rejoint le chat`;
                            generalMessages.appendChild(joinMessage);
                            generalMessages.scrollTop = generalMessages.scrollHeight;
                        }
                    }
                    else if (data.type === 'user_leave') {
                        // User leaving
                        if (onlineUsersList.has(data.user)) {
                            onlineUsersList.delete(data.user);
                            updateOnlineUsersList();
                            
                            const username = data.user.split('@')[0];
                            const leaveMessage = document.createElement('div');
                            leaveMessage.className = 'text-center text-muted small my-2';
                            leaveMessage.textContent = `${username} a quitté le chat`;
                            generalMessages.appendChild(leaveMessage);
                            generalMessages.scrollTop = generalMessages.scrollHeight;
                        }
                    }
                } catch (error) {
                    console.error("Error processing WebSocket message:", error);
                }
            };
            
            chatSocket.onclose = function(e) {
                console.error('WebSocket closed unexpectedly. Code:', e.code, 'Reason:', e.reason);
                
                // Reconnection attempt with exponential back-off
                if (reconnectAttempts < maxReconnectAttempts) {
                    reconnectAttempts++;
                    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
                    console.log(`Reconnecting in ${delay/1000} seconds... (Attempt ${reconnectAttempts})`);
                    
                    setTimeout(() => {
                        connectWebSocket();
                    }, delay);
                } else {
                    console.error(`Failed to reconnect after ${maxReconnectAttempts} attempts.`);
                    // Show message to user
                    const connectionError = document.createElement('div');
                    connectionError.className = 'alert alert-danger m-3';
                    connectionError.innerHTML = `
                        <strong>Problème de connexion</strong>
                        <p>Impossible de se connecter au serveur de chat. Veuillez recharger la page.</p>
                        <button class="btn btn-sm btn-outline-danger" onclick="window.location.reload()">Recharger</button>
                    `;
                    generalMessages.prepend(connectionError);
                }
            };
            
            chatSocket.onerror = function(e) {
                console.error('WebSocket error:', e);
            };
            
            return chatSocket;
        } catch (error) {
            console.error('Error creating WebSocket connection:', error);
            return null;
        }
    }
    
    // Initialize WebSocket connection
    chatSocket = connectWebSocket();
    
    // General chat form
    generalForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = generalInput.value.trim();
        if (!message) return;
        
        // Send via WebSocket if possible
        if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
            try {
                chatSocket.send(JSON.stringify({
                    'message': message
                }));
            } catch (error) {
                console.error("Error sending via WebSocket:", error);
            }
        } else {
            console.warn('WebSocket not connected. Using HTTP fallback.');
        }
        
        // Always send via HTTP to ensure delivery
        fetch('/chat/api/send/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: `content=${encodeURIComponent(message)}`
        })
        .then(response => {
            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = '/accounts/login/?next=/chat/';
                }
                throw new Error('Sending error');
            }
            return response.json();
        })
        .catch(error => console.error('Error:', error));
        
        generalInput.value = '';
    });
    
    // Private chat form
    privateForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = privateInput.value.trim();
        if (!message) return;
        
        const recipient = recipientId.value;
        const replyTo = replyToId.value;
        
        // Build form data
        const formData = new FormData();
        formData.append('content', message);
        if (recipient) formData.append('recipient_id', recipient);
        if (replyTo) formData.append('reply_to_id', replyTo);
        
        // Convert FormData to URLEncoded
        const urlEncodedData = new URLSearchParams(formData).toString();
        
        // Send private message via WebSocket if possible
        if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
            try {
                chatSocket.send(JSON.stringify({
                    'type': 'private_message',
                    'message': message,
                    'recipient_id': recipient,
                    'reply_to_id': replyTo
                }));
            } catch (error) {
                console.error("Error sending private message via WebSocket:", error);
            }
        }
        
        // Always send via HTTP
        fetch('/chat/api/private/send/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: urlEncodedData
        })
        .then(response => {
            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = '/accounts/login/?next=/chat/';
                }
                throw new Error('Sending error');
            }
            return response.json();
        })
        .then(data => {
            console.log("Private message sent:", data);
            // Reset form
            privateInput.value = '';
            recipientId.value = '';
            replyToId.value = '';
            replyInfo.style.display = 'none';
        })
        .catch(error => console.error('Error:', error));
    });
    
    // Permettre l'envoi par touche Entrée pour le chat général
    generalInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            generalForm.querySelector('button[type="submit"]').click();
        }
    });

    // Permettre l'envoi par touche Entrée pour le chat privé
    privateInput.addEventListener('keypress', function(e) {
        if (    e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            privateForm.querySelector('button[type="submit"]').click();
        }
    });

    // Update online users list
    function updateOnlineUsersList() {
        onlineUsers.innerHTML = '';
        onlineCount.textContent = onlineUsersList.size;
        
        onlineUsersList.forEach(user => {
            const username = user.split('@')[0];
            
            const userElement = document.createElement('li');
            userElement.className = 'list-group-item d-flex align-items-center';
            userElement.style.backgroundColor = '#252525';
            userElement.style.border = '1px solid #333';
            userElement.style.marginBottom = '5px';
            userElement.style.color = '#fff';
            
            if (user === currentUserEmail) {
                userElement.innerHTML = `
                    <div class="d-flex align-items-center">
                        <div class="avatar bg-primary me-2">
                            ${username.charAt(0).toUpperCase()}
                        </div>
                        <div>
                            <strong>${username}</strong>
                            <small class="text-muted d-block">(vous)</small>
                        </div>
                        <span class="role-badge ms-auto">
                            ${isStaff ? 'conseiller' : 'utilisateur'}
                        </span>
                    </div>
                `;
            } else {
                userElement.innerHTML = `
                    <div class="d-flex align-items-center w-100">
                        <div class="avatar bg-secondary me-2">
                            ${username.charAt(0).toUpperCase()}
                        </div>
                        <div>
                            ${username}
                        </div>
                        <span class="role-badge ms-auto">utilisateur</span>
                    </div>
                `;
            }
            
            onlineUsers.appendChild(userElement);
        });
    }
    
    // Get cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Refresh general messages
    function refreshGeneralMessages() {
        fetch('/chat/api/messages/')
            .then(response => {
                if (!response.ok) {
                    if (response.status === 401) {
                        window.location.href = '/accounts/login/?next=/chat/';
                    }
                    throw new Error('Error retrieving messages');
                }
                return response.json();
            })
            .then(data => {
                // Refresh only if user is not typing
                if (document.activeElement !== generalInput) {
                    // Get current message IDs
                    const currentMessageIds = Array.from(generalMessages.querySelectorAll('.message'))
                        .map(el => el.dataset.messageId);
                        
                    // Check for new messages
                    const newMessages = data.messages.filter(msg => 
                        !currentMessageIds.includes(msg.id.toString())
                    );
                    
                    if (newMessages.length > 0) {
                        const wasScrolledToBottom = generalMessages.scrollHeight - generalMessages.clientHeight <= generalMessages.scrollTop + 10;
                        
                        // Append only new messages
                        newMessages.forEach(message => {
                            const username = message.user_email.split('@')[0];
                            const formattedDate = formatDate(message.timestamp);
                            
                            const messageElement = document.createElement('div');
                            messageElement.className = `message ${message.is_staff ? 'staff-message' : 'user-message'} p-2 mb-2`;
                            messageElement.dataset.messageId = message.id;
                            
                            messageElement.innerHTML = `
                                <strong class="text-white">
                                    ${username} 
                                    ${message.is_staff ? 
                                        '<span class="badge bg-warning text-dark">conseiller</span>' : 
                                        '<span class="role-badge">utilisateur</span>'
                                    }
                                </strong>
                                <span class="message-timestamp">${formattedDate}</span>
                                <div class="text-white">${message.content}</div>
                            `;
                            
                            generalMessages.appendChild(messageElement);
                        });
                        
                        // Auto-scroll if was at bottom
                        if (wasScrolledToBottom) {
                            generalMessages.scrollTop = generalMessages.scrollHeight;
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error retrieving messages:', error);
            });
    }
    
// Refresh private messages
function refreshPrivateMessages() {
    fetch('/chat/api/private/messages/')
    .then(response => {
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = '/accounts/login/?next=/chat/';
            }
            throw new Error('Error retrieving private messages');
        }
        return response.json();
    })
    .then(data => {
        // Refresh only if user is not typing
        if (document.activeElement !== privateInput) {
            // Get current message IDs
            const currentMessageIds = Array.from(privateMessages.querySelectorAll('.message'))
                .map(el => el.dataset.messageId);
                
            // Check for new messages
            const newMessages = data.messages.filter(msg => 
                !currentMessageIds.includes(msg.id.toString())
            );
            
            if (newMessages.length > 0) {
                const wasScrolledToBottom = privateMessages.scrollHeight - privateMessages.clientHeight <= privateMessages.scrollTop + 10;
                
                // Append only new messages
                newMessages.forEach(message => {
                    const username = message.user_email.split('@')[0];// Toggle online users overlay
                    function toggleOnlineUsers() {
                        const overlay = document.getElementById('online-users-overlay');
                        overlay.classList.toggle('show');
                    }
                    
                    // Format date: converts "DD-MM-YYYY HH:MM" to "DD/MM HH:MM"
                    function formatDate(dateStr) {
                        if (!dateStr) return '';
                        const parts = dateStr.split(' ');
                        if (parts.length !== 2) return dateStr;
                        
                        const dateParts = parts[0].split('-');
                        if (dateParts.length !== 3) return dateStr;
                        
                        return `${dateParts[0]}/${dateParts[1]} ${parts[1]}`;
                    }
                    
                    // Function to reply to a message
                    function replyToMessage(messageId, userId, userEmail) {
                        document.getElementById('recipient-id').value = userId;
                        document.getElementById('reply-to-id').value = messageId;
                        
                        const username = userEmail.split('@')[0];
                        document.getElementById('reply-user').textContent = username;
                        document.getElementById('reply-info').style.display = 'block';
                        
                        // Focus on input field
                        document.getElementById('private-input').focus();
                    }
                    
                    // Function to cancel reply
                    function cancelReply() {
                        document.getElementById('recipient-id').value = '';
                        document.getElementById('reply-to-id').value = '';
                        document.getElementById('reply-info').style.display = 'none';
                    }
                    
                    // Close the overlay when clicking outside of it
                    document.addEventListener('click', function(event) {
                        const overlay = document.getElementById('online-users-overlay');
                        const button = document.querySelector('.online-users-button');
                        
                        if (overlay.classList.contains('show') && 
                            !overlay.contains(event.target) && 
                            !button.contains(event.target)) {
                            overlay.classList.remove('show');
                        }
                    });
                    
                    document.addEventListener('DOMContentLoaded', function() {
                        console.log("Chat script initialized");
                        
                        // DOM elements
                        const generalMessages = document.getElementById('general-messages');
                        const generalForm = document.getElementById('general-form');
                        const generalInput = document.getElementById('general-input');
                        
                        const privateMessages = document.getElementById('private-messages');
                        const privateForm = document.getElementById('private-form');
                        const privateInput = document.getElementById('private-input');
                        const recipientId = document.getElementById('recipient-id');
                        const replyToId = document.getElementById('reply-to-id');
                        const replyInfo = document.getElementById('reply-info');
                        const replyUser = document.getElementById('reply-user');
                        
                        const onlineUsers = document.getElementById('online-users');
                        const onlineCount = document.getElementById('online-count');
                        const chatContainer = document.getElementById('chat-container');
                        
                        // User data
                        const currentUserEmail = chatContainer.dataset.userEmail;
                        const currentUserId = chatContainer.dataset.userId;
                        const isStaff = chatContainer.dataset.isStaff === 'true';
                        
                        console.log("User info:", currentUserEmail, isStaff);
                        
                        // Scroll to bottom of messages
                        generalMessages.scrollTop = generalMessages.scrollHeight;
                        privateMessages.scrollTop = privateMessages.scrollHeight;
                        
                        // Format existing usernames
                        function formatExistingUsernames() {
                            document.querySelectorAll('.message strong').forEach(element => {
                                const text = element.childNodes[0].textContent.trim();
                                if (text.includes('@')) {
                                    const username = text.split('@')[0];
                                    element.childNodes[0].textContent = username + ' ';
                                }
                            });
                        }
                        
                        formatExistingUsernames();
                        
                        // Online users list
                        const onlineUsersList = new Set();
                        
                        // Add current user
                        if (currentUserEmail) {
                            onlineUsersList.add(currentUserEmail);
                            updateOnlineUsersList();
                        }
                        
                        // Connect WebSocket with error handling and reconnection
                        let chatSocket;
                        let reconnectAttempts = 0;
                        const maxReconnectAttempts = 5;
                        
                        function connectWebSocket() {
                            console.log("Connecting to WebSocket...");
                            
                            try {
                                // Create new WebSocket connection
                                chatSocket = new WebSocket(
                                    'ws://' + window.location.host + '/ws/chat/'
                                );
                                
                                chatSocket.onopen = function(e) {
                                    console.log('WebSocket connection established');
                                    reconnectAttempts = 0; // Reset attempt counter
                                    
                                    // Announce user joining chat
                                    if (currentUserEmail) {
                                        try {
                                            chatSocket.send(JSON.stringify({
                                                'type': 'user_join',
                                                'user': currentUserEmail
                                            }));
                                        } catch (error) {
                                            console.error("Error sending join event:", error);
                                        }
                                    }
                                };
                                
                                chatSocket.onmessage = function(e) {
                                    try {
                                        const data = JSON.parse(e.data);
                                        
                                        if (data.type === 'message') {
                                            // Public message
                                            const message = data.message;
                                            const username = message.user_email.split('@')[0];
                                            const formattedDate = formatDate(message.timestamp);
                                            
                                            const messageElement = document.createElement('div');
                                            messageElement.className = `message ${message.is_staff ? 'staff-message' : 'user-message'} p-2 mb-2`;
                                            messageElement.dataset.messageId = message.id;
                                            
                                            messageElement.innerHTML = `
                                                <strong class="text-white">
                                                    ${username} 
                                                    ${message.is_staff ? 
                                                        '<span class="badge bg-warning text-dark">conseiller</span>' : 
                                                        '<span class="role-badge">utilisateur</span>'
                                                    }
                                                </strong>
                                                <span class="message-timestamp">${formattedDate}</span>
                                                <div class="text-white">${message.content}</div>
                                            `;
                                            
                                            generalMessages.appendChild(messageElement);
                                            generalMessages.scrollTop = generalMessages.scrollHeight;
                                        }
                                        else if (data.type === 'private_message') {
                                            // Private message
                                            const message = data.message;
                                            const username = message.user_email.split('@')[0];
                                            const formattedDate = formatDate(message.timestamp);
                                            
                                            // Check if this message concerns us
                                            if (isStaff || message.user_email === currentUserEmail || 
                                                message.recipient_email === currentUserEmail) {
                                                
                                                const messageElement = document.createElement('div');
                                                messageElement.className = `message ${message.is_staff ? 'staff-message' : 'user-message'} p-2 mb-2`;
                                                messageElement.dataset.messageId = message.id;
                                                messageElement.dataset.userId = message.user_id;
                                                messageElement.dataset.userEmail = message.user_email;
                                                
                                                let replyButton = '';
                                                if (isStaff && !message.is_staff) {
                                                    replyButton = `
                                                        <div class="reply-actions mt-1">
                                                            <button class="reply-btn btn btn-sm btn-outline-light" onclick="replyToMessage('${message.id}', '${message.user_id}', '${message.user_email}')">Répondre</button>
                                                        </div>
                                                    `;
                                                }
                                                
                                                messageElement.innerHTML = `
                                                    <strong class="text-white">
                                                        ${username} 
                                                        ${message.is_staff ? 
                                                            '<span class="badge bg-warning text-dark">conseiller</span>' : 
                                                            '<span class="role-badge">utilisateur</span>'
                                                        }
                                                    </strong>
                                                    <span class="message-timestamp">${formattedDate}</span>
                                                    <div class="text-white">${message.content}</div>
                                                    ${replyButton}
                                                `;
                                                
                                                privateMessages.appendChild(messageElement);
                                                privateMessages.scrollTop = privateMessages.scrollHeight;
                                            }
                                        }
                                        else if (data.type === 'user_join') {
                                            // User joining
                                            if (!onlineUsersList.has(data.user)) {
                                                onlineUsersList.add(data.user);
                                                updateOnlineUsersList();
                                                
                                                const username = data.user.split('@')[0];
                                                const joinMessage = document.createElement('div');
                                                joinMessage.className = 'text-center text-muted small my-2';
                                                joinMessage.textContent = `${username} a rejoint le chat`;
                                                generalMessages.appendChild(joinMessage);
                                                generalMessages.scrollTop = generalMessages.scrollHeight;
                                            }
                                        }
                                        else if (data.type === 'user_leave') {
                                            // User leaving
                                            if (onlineUsersList.has(data.user)) {
                                                onlineUsersList.delete(data.user);
                                                updateOnlineUsersList();
                                                
                                                const username = data.user.split('@')[0];
                                                const leaveMessage = document.createElement('div');
                                                leaveMessage.className = 'text-center text-muted small my-2';
                                                leaveMessage.textContent = `${username} a quitté le chat`;
                                                generalMessages.appendChild(leaveMessage);
                                                generalMessages.scrollTop = generalMessages.scrollHeight;
                                            }
                                        }
                                    } catch (error) {
                                        console.error("Error processing WebSocket message:", error);
                                    }
                                };
                                
                                chatSocket.onclose = function(e) {
                                    console.error('WebSocket closed unexpectedly. Code:', e.code, 'Reason:', e.reason);
                                    
                                    // Reconnection attempt with exponential back-off
                                    if (reconnectAttempts < maxReconnectAttempts) {
                                        reconnectAttempts++;
                                        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
                                        console.log(`Reconnecting in ${delay/1000} seconds... (Attempt ${reconnectAttempts})`);
                                        
                                        setTimeout(() => {
                                            connectWebSocket();
                                        }, delay);
                                    } else {
                                        console.error(`Failed to reconnect after ${maxReconnectAttempts} attempts.`);
                                        // Show message to user
                                        const connectionError = document.createElement('div');
                                        connectionError.className = 'alert alert-danger m-3';
                                        connectionError.innerHTML = `
                                            <strong>Problème de connexion</strong>
                                            <p>Impossible de se connecter au serveur de chat. Veuillez recharger la page.</p>
                                            <button class="btn btn-sm btn-outline-danger" onclick="window.location.reload()">Recharger</button>
                                        `;
                                        generalMessages.prepend(connectionError);
                                    }
                                };
                                
                                chatSocket.onerror = function(e) {
                                    console.error('WebSocket error:', e);
                                };
                                
                                return chatSocket;
                            } catch (error) {
                                console.error('Error creating WebSocket connection:', error);
                                return null;
                            }
                        }
                        
                        // Initialize WebSocket connection
                        chatSocket = connectWebSocket();
                        
                        // General chat form
                        generalForm.addEventListener('submit', function(e) {
                            e.preventDefault();
                            
                            const message = generalInput.value.trim();
                            if (!message) return;
                            
                            // Send via WebSocket if possible
                            if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
                                try {
                                    chatSocket.send(JSON.stringify({
                                        'message': message
                                    }));
                                } catch (error) {
                                    console.error("Error sending via WebSocket:", error);
                                }
                            } else {
                                console.warn('WebSocket not connected. Using HTTP fallback.');
                            }
                            
                            // Always send via HTTP to ensure delivery
                            fetch('/chat/api/send/', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/x-www-form-urlencoded',
                                    'X-CSRFToken': getCookie('csrftoken')
                                },
                                body: `content=${encodeURIComponent(message)}`
                            })
                            .then(response => {
                                if (!response.ok) {
                                    if (response.status === 401) {
                                        window.location.href = '/accounts/login/?next=/chat/';
                                    }
                                    throw new Error('Sending error');
                                }
                                return response.json();
                            })
                            .catch(error => console.error('Error:', error));
                            
                            generalInput.value = '';
                        });
                        
                        // Private chat form
                        privateForm.addEventListener('submit', function(e) {
                            e.preventDefault();
                            
                            const message = privateInput.value.trim();
                            if (!message) return;
                            
                            const recipient = recipientId.value;
                            const replyTo = replyToId.value;
                            
                            // Build form data
                            const formData = new FormData();
                            formData.append('content', message);
                            if (recipient) formData.append('recipient_id', recipient);
                            if (replyTo) formData.append('reply_to_id', replyTo);
                            
                            // Convert FormData to URLEncoded
                            const urlEncodedData = new URLSearchParams(formData).toString();
                            
                            // Send private message via WebSocket if possible
                            if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
                                try {
                                    chatSocket.send(JSON.stringify({
                                        'type': 'private_message',
                                        'message': message,
                                        'recipient_id': recipient,
                                        'reply_to_id': replyTo
                                    }));
                                } catch (error) {
                                    console.error("Error sending private message via WebSocket:", error);
                                }
                            }
                            
                            // Always send via HTTP
                            fetch('/chat/api/private/send/', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/x-www-form-urlencoded',
                                    'X-CSRFToken': getCookie('csrftoken')
                                },
                                body: urlEncodedData
                            })
                            .then(response => {
                                if (!response.ok) {
                                    if (response.status === 401) {
                                        window.location.href = '/accounts/login/?next=/chat/';
                                    }
                                    throw new Error('Sending error');
                                }
                                return response.json();
                            })
                            .then(data => {
                                console.log("Private message sent:", data);
                                // Reset form
                                privateInput.value = '';
                                recipientId.value = '';
                                replyToId.value = '';
                                replyInfo.style.display = 'none';
                            })
                            .catch(error => console.error('Error:', error));
                        });
                        
                        // Permettre l'envoi par touche Entrée pour le chat général
                        generalInput.addEventListener('keypress', function(e) {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                generalForm.querySelector('button[type="submit"]').click();
                            }
                        });
                    
                        // Permettre l'envoi par touche Entrée pour le chat privé
                        privateInput.addEventListener('keypress', function(e) {
                            if (    e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                privateForm.querySelector('button[type="submit"]').click();
                            }
                        });
                    
                        // Update online users list
                        function updateOnlineUsersList() {
                            onlineUsers.innerHTML = '';
                            onlineCount.textContent = onlineUsersList.size;
                            
                            onlineUsersList.forEach(user => {
                                const username = user.split('@')[0];
                                
                                const userElement = document.createElement('li');
                                userElement.className = 'list-group-item d-flex align-items-center';
                                userElement.style.backgroundColor = '#252525';
                                userElement.style.border = '1px solid #333';
                                userElement.style.marginBottom = '5px';
                                userElement.style.color = '#fff';
                                
                                if (user === currentUserEmail) {
                                    userElement.innerHTML = `
                                        <div class="d-flex align-items-center">
                                            <div class="avatar bg-primary me-2">
                                                ${username.charAt(0).toUpperCase()}
                                            </div>
                                            <div>
                                                <strong>${username}</strong>
                                                <small class="text-muted d-block">(vous)</small>
                                            </div>
                                            <span class="role-badge ms-auto">
                                                ${isStaff ? 'conseiller' : 'utilisateur'}
                                            </span>
                                        </div>
                                    `;
                                } else {
                                    userElement.innerHTML = `
                                        <div class="d-flex align-items-center w-100">
                                            <div class="avatar bg-secondary me-2">
                                                ${username.charAt(0).toUpperCase()}
                                            </div>
                                            <div>
                                                ${username}
                                            </div>
                                            <span class="role-badge ms-auto">utilisateur</span>
                                        </div>
                                    `;
                                }
                                
                                onlineUsers.appendChild(userElement);
                            });
                        }
                        
                        // Get cookie
                        function getCookie(name) {
                            let cookieValue = null;
                            if (document.cookie && document.cookie !== '') {
                                const cookies = document.cookie.split(';');
                                for (let i = 0; i < cookies.length; i++) {
                                    const cookie = cookies[i].trim();
                                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                        break;
                                    }
                                }
                            }
                            return cookieValue;
                        }
                        
                        // Refresh general messages
                        function refreshGeneralMessages() {
                            fetch('/chat/api/messages/')
                                .then(response => {
                                    if (!response.ok) {
                                        if (response.status === 401) {
                                            window.location.href = '/accounts/login/?next=/chat/';
                                        }
                                        throw new Error('Error retrieving messages');
                                    }
                                    return response.json();
                                })
                                .then(data => {
                                    // Refresh only if user is not typing
                                    if (document.activeElement !== generalInput) {
                                        // Get current message IDs
                                        const currentMessageIds = Array.from(generalMessages.querySelectorAll('.message'))
                                            .map(el => el.dataset.messageId);
                                            
                                        // Check for new messages
                                        const newMessages = data.messages.filter(msg => 
                                            !currentMessageIds.includes(msg.id.toString())
                                        );
                                        
                                        if (newMessages.length > 0) {
                                            const wasScrolledToBottom = generalMessages.scrollHeight - generalMessages.clientHeight <= generalMessages.scrollTop + 10;
                                            
                                            // Append only new messages
                                            newMessages.forEach(message => {
                                                const username = message.user_email.split('@')[0];
                                                const formattedDate = formatDate(message.timestamp);
                                                
                                                const messageElement = document.createElement('div');
                                                messageElement.className = `message ${message.is_staff ? 'staff-message' : 'user-message'} p-2 mb-2`;
                                                messageElement.dataset.messageId = message.id;
                                                
                                                messageElement.innerHTML = `
                                                    <strong class="text-white">
                                                        ${username} 
                                                        ${message.is_staff ? 
                                                            '<span class="badge bg-warning text-dark">conseiller</span>' : 
                                                            '<span class="role-badge">utilisateur</span>'
                                                        }
                                                    </strong>
                                                    <span class="message-timestamp">${formattedDate}</span>
                                                    <div class="text-white">${message.content}</div>
                                                `;
                                                
                                                generalMessages.appendChild(messageElement);
                                            });
                                            
                                            // Auto-scroll if was at bottom
                                            if (wasScrolledToBottom) {
                                                generalMessages.scrollTop = generalMessages.scrollHeight;
                                            }
                                        }
                                    }
                                })
                                .catch(error => {
                                    console.error('Error retrieving messages:', error);
                                });
                        }
                        
                    // Refresh private messages
                    function refreshPrivateMessages() {
                        fetch('/chat/api/private/messages/')
                        .then(response => {
                            if (!response.ok) {
                                if (response.status === 401) {
                                    window.location.href = '/accounts/login/?next=/chat/';
                                }
                                throw new Error('Error retrieving private messages');
                            }
                            return response.json();
                        })
                        .then(data => {
                            // Refresh only if user is not typing
                            if (document.activeElement !== privateInput) {
                                // Get current message IDs
                                const currentMessageIds = Array.from(privateMessages.querySelectorAll('.message'))
                                    .map(el => el.dataset.messageId);
                                    
                                // Check for new messages
                                const newMessages = data.messages.filter(msg => 
                                    !currentMessageIds.includes(msg.id.toString())
                                );
                                
                                if (newMessages.length > 0) {
                                    const wasScrolledToBottom = privateMessages.scrollHeight - privateMessages.clientHeight <= privateMessages.scrollTop + 10;
                                    
                                    // Append only new messages
                                    newMessages.forEach(message => {
                                        const username = message.user_email.split('@')[0];
                                        const formattedDate = formatDate(message.timestamp);
                                        
                                        const messageElement = document.createElement('div');
                                        messageElement.className = `message ${message.is_staff ? 'staff-message' : 'user-message'} p-2 mb-2`;
                                        messageElement.dataset.messageId = message.id;
                                        messageElement.dataset.userId = message.user_id;
                                        messageElement.dataset.userEmail = message.user_email;
                                        
                                        let replyButton = '';
                                        if (isStaff && !message.is_staff) {
                                            replyButton = `
                                                <div class="reply-actions mt-1">
                                                    <button class="reply-btn btn btn-sm btn-outline-light" onclick="replyToMessage('${message.id}', '${message.user_id}', '${message.user_email}')">Répondre</button>
                                                </div>
                                            `;
                                        }
                                        
                                        messageElement.innerHTML = `
                                            <strong class="text-white">
                                                ${username} 
                                                ${message.is_staff ? 
                                                    '<span class="badge bg-warning text-dark">conseiller</span>' : 
                                                    '<span class="role-badge">utilisateur</span>'
                                                }
                                            </strong>
                                            <span class="message-timestamp">${formattedDate}</span>
                                            <div class="text-white">${message.content}</div>
                                            ${replyButton}
                                        `;
                                        
                                        privateMessages.appendChild(messageElement);
                                    });
                                    
                                    // Auto-scroll if was at bottom
                                    if (wasScrolledToBottom) {
                                        privateMessages.scrollTop = privateMessages.scrollHeight;
                                    }
                                }
                            }
                        })
                        .catch(error => {
                            console.error('Error retrieving private messages:', error);
                        });
                    }
                    
                    // Function to simulate online users for testing
                    function simulateOnlineUsers() {
                        // Add current user if not already in list
                        if (currentUserEmail && !onlineUsersList.has(currentUserEmail)) {
                            onlineUsersList.add(currentUserEmail);
                        }
                        
                        // Check if we need to add test users
                        if (onlineUsersList.size < 1) {
                            console.log("Adding test users to online list");
                            // Add some test users for demonstration
                            onlineUsersList.add(currentUserEmail || "vous@example.com");
                        }
                        
                        updateOnlineUsersList();
                    }
                    
                    // Call once to ensure there are users shown
                    simulateOnlineUsers();
                    
                    // Refresh messages regularly
                    setInterval(refreshGeneralMessages, 1000);
                    setInterval(refreshPrivateMessages, 1000);
                    
                    // Refresh online users list
                    setInterval(simulateOnlineUsers, 30000);
                    
                    // Initial message refresh
                    refreshGeneralMessages();
                    refreshPrivateMessages();
                    });
                    const formattedDate = formatDate(message.timestamp);
                    
                    const messageElement = document.createElement('div');
                    messageElement.className = `message ${message.is_staff ? 'staff-message' : 'user-message'} p-2 mb-2`;
                    messageElement.dataset.messageId = message.id;
                    messageElement.dataset.userId = message.user_id;
                    messageElement.dataset.userEmail = message.user_email;
                    
                    let replyButton = '';
                    if (isStaff && !message.is_staff) {
                        replyButton = `
                            <div class="reply-actions mt-1">
                                <button class="reply-btn btn btn-sm btn-outline-light" onclick="replyToMessage('${message.id}', '${message.user_id}', '${message.user_email}')">Répondre</button>
                            </div>
                        `;
                    }
                    
                    messageElement.innerHTML = `
                        <strong class="text-white">
                            ${username} 
                            ${message.is_staff ? 
                                '<span class="badge bg-warning text-dark">conseiller</span>' : 
                                '<span class="role-badge">utilisateur</span>'
                            }
                        </strong>
                        <span class="message-timestamp">${formattedDate}</span>
                        <div class="text-white">${message.content}</div>
                        ${replyButton}
                    `;
                    
                    privateMessages.appendChild(messageElement);
                });
                
                // Auto-scroll if was at bottom
                if (wasScrolledToBottom) {
                    privateMessages.scrollTop = privateMessages.scrollHeight;
                }
            }
        }
    })
    .catch(error => {
        console.error('Error retrieving private messages:', error);
    });
}

// Function to simulate online users for testing
function simulateOnlineUsers() {
    // Add current user if not already in list
    if (currentUserEmail && !onlineUsersList.has(currentUserEmail)) {
        onlineUsersList.add(currentUserEmail);
    }
    
    // Check if we need to add test users
    if (onlineUsersList.size < 1) {
        console.log("Adding test users to online list");
        // Add some test users for demonstration
        onlineUsersList.add(currentUserEmail || "vous@example.com");
    }
    
    updateOnlineUsersList();
}

// Call once to ensure there are users shown
simulateOnlineUsers();

// Refresh messages regularly
setInterval(refreshGeneralMessages, 1000);
setInterval(refreshPrivateMessages, 1000);

// Refresh online users list
setInterval(simulateOnlineUsers, 30000);

// Initial message refresh
refreshGeneralMessages();
refreshPrivateMessages();
});