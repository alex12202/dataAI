document.getElementById('send-btn').addEventListener('click', async () => {
    const inputField = document.getElementById('user-input');
    const input = inputField.value.trim();
    if (!input) return;

    const chatBox = document.getElementById('chat-box');

    // Zobraz používateľskú správu
    const userMsg = document.createElement('div');
    userMsg.classList.add('message', 'user');
    userMsg.textContent = input;
    chatBox.appendChild(userMsg);

    try {
        const resp = await fetch('chat.php', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({ message: input })
        });

        const data = await resp.json();
        console.log('Backend response:', data);

        // ✅ Oprava: používame `data.answer` miesto `data.response`
        const botMsg = document.createElement('div');
        botMsg.classList.add('message', 'bot');
        botMsg.textContent = data.answer || '⚠️ Neočakávaná odpoveď';
        chatBox.appendChild(botMsg);
    } catch (error) {
        const errMsg = document.createElement('div');
        errMsg.classList.add('message', 'bot');
        errMsg.textContent = '⚠️ Chyba pri volaní servera.';
        chatBox.appendChild(errMsg);
        console.error('Fetch error:', error);
    }

    inputField.value = '';
    chatBox.scrollTop = chatBox.scrollHeight;
});

document.getElementById('user-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        document.getElementById('send-btn').click();
    }
});
