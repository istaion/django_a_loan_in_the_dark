document.addEventListener("DOMContentLoaded", function () {
    const chatType = chatTypeData; // Cette variable sera définie dans le template
    const userEmail = userEmailData; // Cette variable sera définie dans le template
    const socketUrl = `ws://${window.location.host}/ws/chat/${chatType}/`;
    const chatSocket = new WebSocket(socketUrl);
    
    let replyingTo = null;  // Stocke l'ID du destinataire si réponse
    const replyContainer = document.getElementById("reply-to-container");
    const replyText = document.getElementById("reply-to-text");
    const cancelReplyButton = document.getElementById("cancel-reply");
    const chatMessagesContainer = document.getElementById("chat-messages");
    const chatInput = document.getElementById("chat-input");
    const sendButton = document.getElementById("send-button");
    
    // Fonction pour faire défiler vers le bas
    function scrollToBottom() {
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    }
    
    // Scroll initial vers le bas
    scrollToBottom();

    // Fonction pour envoyer un message
    function sendMessage(message, recipientId = null) {
        chatSocket.send(JSON.stringify({
            'message': message,
            'type': chatType,
            'recipient_id': recipientId
        }));
    }

    // Lorsqu'on reçoit un message
    chatSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        
        const messageContainer = document.createElement('div');
        messageContainer.classList.add('chat-message', 'mb-2');
        
        // Déterminer si le message est de l'utilisateur actuel
        const isCurrentUser = data.user === userEmail;
        if (isCurrentUser) {
            messageContainer.classList.add('text-end');
        }
        
        // Créer la bulle de message
        const messageBubble = document.createElement('div');
        messageBubble.classList.add('message-bubble', 'd-inline-block', 'p-2', 'rounded');
        
        if (isCurrentUser) {
            messageBubble.classList.add('bg-primary', 'text-white');
        } else {
            messageBubble.classList.add('bg-light');
        }
        
        // Ajouter l'en-tête de message (utilisateur + avatar + timestamp)
        const messageHeader = document.createElement('div');
        messageHeader.classList.add('message-header', 'd-flex', 'justify-content-between', 'align-items-center', 'mb-1');
        
        // Container pour l'avatar et le nom
        const userContainer = document.createElement('div');
        userContainer.classList.add('d-flex', 'align-items-center');
        
        // Avatar
        const avatar = document.createElement('img');
        avatar.classList.add('rounded-circle', 'me-2');
        avatar.width = 24;
        avatar.height = 24;
        avatar.alt = "Avatar";
        
        // Utiliser l'avatar fourni dans les données ou une image par défaut
        avatar.src = data.avatar_url || '/static/images/default-avatar.png';
        
        // Nom d'utilisateur
        const userSpan = document.createElement('small');
        userSpan.classList.add('fw-bold');
        userSpan.textContent = data.user;
        
        // Ajouter l'avatar et le nom au container
        userContainer.appendChild(avatar);
        userContainer.appendChild(userSpan);
        
        // Timestamp
        const timeSpan = document.createElement('small');
        timeSpan.classList.add('text-muted', 'ms-2');
        timeSpan.textContent = data.timestamp;
        
        // Assembler l'en-tête
        messageHeader.appendChild(userContainer);
        messageHeader.appendChild(timeSpan);
        messageBubble.appendChild(messageHeader);
        
        // Ajouter le contenu du message
        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');
        messageContent.textContent = data.message;
        messageBubble.appendChild(messageContent);
        
        messageContainer.appendChild(messageBubble);

        // Si c'est un staff, ajouter un bouton "Répondre" pour les utilisateurs non-staff
        if (isStaff === "True" && data.message_type === "private" && !data.is_staff) {
            const replyButton = document.createElement('button');
            replyButton.textContent = "Répondre";
            replyButton.classList.add('btn', 'btn-sm', 'btn-outline-secondary', 'reply-button', 'mt-1');
            
            const replyIcon = document.createElement('i');
            replyIcon.classList.add('bi', 'bi-reply');
            replyButton.prepend(replyIcon, " ");
            
            replyButton.setAttribute('data-recipient', data.user_id); // Utiliser user_id
            replyButton.setAttribute('data-recipient-name', data.user);
            replyButton.onclick = function () {
                setReplyTo(data.user_id, data.user);
            };
            messageContainer.appendChild(replyButton);
        }

        chatMessagesContainer.appendChild(messageContainer);
        scrollToBottom();
    };

    // Lorsqu'on envoie un message
    sendButton.onclick = function () {
        const message = chatInput.value.trim();
        
        if (!message) {
            return; // Ne rien faire si le message est vide
        }
        
        let recipientId = replyingTo;

        if (chatType === 'private' && isStaff === "False") {
            recipientId = currentUserId; // Cette variable sera définie dans le template
        }
        
        sendMessage(message, recipientId);

        // Réinitialise l'input et la réponse sélectionnée
        chatInput.value = '';
        clearReplyTo();
    };
    
    // Envoyer le message lors de l'appui sur Entrée (mais Shift+Entrée pour nouvelle ligne)
    chatInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendButton.click();
        }
    });

    // Gérer le clic sur "Répondre" pour les messages existants
    document.querySelectorAll('.reply-button').forEach(button => {
        button.addEventListener('click', function () {
            const recipientId = this.getAttribute('data-recipient');
            const recipientName = this.getAttribute('data-recipient-name');
            setReplyTo(recipientId, recipientName);
        });
    });

    // Gérer le bouton "Annuler"
    cancelReplyButton.addEventListener("click", function () {
        clearReplyTo();
    });

    // Fonction pour afficher "Répondre à..."
    function setReplyTo(userId, userName) {
        replyingTo = userId;
        replyText.textContent = "Répondre à " + userName;
        replyContainer.classList.remove('d-none');
        replyContainer.classList.add('d-block');
        chatInput.focus();
    }

    // Fonction pour annuler la réponse
    function clearReplyTo() {
        replyingTo = null;
        replyContainer.classList.remove('d-block');
        replyContainer.classList.add('d-none');
        replyText.textContent = "";
    }
    
    // Reconnecter en cas de déconnexion
    chatSocket.onclose = function(e) {
        console.log('Chat socket closed unexpectedly');
        setTimeout(function() {
            console.log('Attempting to reconnect...');
            window.location.reload();
        }, 3000);
    };
});