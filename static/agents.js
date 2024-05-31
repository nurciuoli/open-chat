
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