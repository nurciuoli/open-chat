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