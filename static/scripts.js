async function initializeAgent() {
    const agentData = {
        name: document.getElementById('agentName').value,
        system_prompt: document.getElementById('systemPrompt').value,
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
        alert(data.message);
    } catch (error) {
        alert('Error initializing agent');
    }
}

async function sendMessage() {
    const request = {
        agent_data: {
            name: document.getElementById('agentName').value,
            system_prompt: document.getElementById('systemPrompt').value,
            model: document.getElementById('model').value
        },
        msg: document.getElementById('message').value
    };

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(request)
        });
        if (response.ok) {
            const data = await response.json();
            displayMessages(data.response);
        } else {
            alert('Error sending message');
        }
    } catch (error) {
        alert('Error sending message');
    }
}

function displayMessages(messages) {
    const chatOutput = document.getElementById('response');
    chatOutput.innerHTML = '';
    messages.forEach(message => {
        chatOutput.innerHTML += `<p>${message}</p>`;
    });
}


async function getMessages() {
    const threadId = document.getElementById('threadId').value;

    try {
        const response = await fetch(`/messages/${threadId}`);
        const data = await response.json();
        document.getElementById('messages').innerText = JSON.stringify(data.messages, null, 2);
    } catch (error) {
        alert('Error retrieving messages');
    }
}
