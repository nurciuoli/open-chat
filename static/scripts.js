
async function initializeAgent() {
    const agentData = {
        system_prompt: document.getElementById('systemPrompt').value,
        name: document.getElementById('agentName').value,
        model: document.getElementById('model').value
    };

    try {
        const response = await fetch('/initialize_agent', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(agentData)
        });

        const data = await response.json();
        if (response.ok) {
            console.log('Agent initialized:', data);
            alert('Agent initialized successfully');
        } else {
            console.error('Failed to initialize agent:', data);
            alert('Failed to initialize agent');
        }
    } catch (error) {
        console.error('Error initializing agent:', error);
        alert('Error initializing agent');
    }
}

async function sendMessage() {
    const agentData = {
        system_prompt: document.getElementById('systemPrompt').value,
        name: document.getElementById('agentName').value,
        model: document.getElementById('model').value
    };

    const message = {
        role: 'user',
        content: [{ text: document.getElementById('message').value }]
    };
    const payload = {
        agent_data: agentData,
        message: message
    };

    try {
        console.log('Sending message payload:', payload);
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        if (response.ok) {
            console.log('Chat response:', data);
            const messagesDiv = document.getElementById('messages');
            messagesDiv.innerHTML += `<div><strong>User:</strong> ${document.getElementById('message').value}</div>`;
            data.responses.forEach(response => {
                messagesDiv.innerHTML += `<div><strong>Assistant:</strong> ${response}</div>`;
            });
            document.getElementById('message').value = ''; // Clear the input field
        } else {
            console.error('Failed to process chat:', data);
            alert('Failed to process chat');
        }
    }catch (error) {
    console.error('Error sending message:', error);
    alert('Error sending message');
}
}

async function getMessages(threadId) {
try {
    const response = await fetch(`/messages/${threadId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    });

    const data = await response.json();
    if (response.ok) {
        console.log('Messages retrieved:', data);
        const messagesDiv = document.getElementById('messages');
        messagesDiv.innerHTML = ''; // Clear previous messages
        data.messages.forEach(message => {
            messagesDiv.innerHTML += `<div><strong>${message.role}:</strong> ${message.content[0].text}</div>`;
        });
    } else {
        console.error('Failed to retrieve messages:', data);
        alert('Failed to retrieve messages');
    }
} catch (error) {
    console.error('Error retrieving messages:', error);
    alert('Error retrieving messages');
}
}

async function getThreads() {
try {
    const response = await fetch('/threads', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    });

    const data = await response.json();
    console.log('Fetched threads data:', data); // Add this line to debug

    if (response.ok) {
        console.log('Threads retrieved:', data);
        const threadsDiv = document.getElementById('threads');
        threadsDiv.innerHTML = ''; // Clear previous threads
        data.threads.forEach(thread => {
            const threadElement = document.createElement('div');
            threadElement.className = 'thread';
            threadElement.innerText = `Thread ID: ${thread.id}`;
            threadElement.onclick = () => getMessages(thread.id);
            threadsDiv.appendChild(threadElement);
        });
    } else {
        console.error('Failed to retrieve threads:', data);
        alert('Failed to retrieve threads');
    }
} catch (error) {
    console.error('Error retrieving threads:', error);
    alert('Error retrieving threads');
}
}

// Fetch threads on page load
window.onload = getThreads;