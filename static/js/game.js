// game.js - Corrected logic to show login-screen by default
window.onerror = function(msg, url, lineNo, columnNo, error) {
    console.error("Error: " + msg + "\nAt: " + url + ":" + lineNo);
    return false;
};

window.onload = () => {
    try {
        console.log("Game initialized on " + window.location.hostname);
        
        // Force visibility of main structural elements
        const mainContent = document.getElementById('main-content');
        if (mainContent) {
            mainContent.style.setProperty('display', 'block', 'important');
            mainContent.style.setProperty('visibility', 'visible', 'important');
        }
        
        // If walletBalance exists, it means we are on the game selection screen (index.html)
        // and current_user is authenticated. In this case, we don't show login screen.
        if (document.getElementById('walletBalance')) {
             const gameScreen = document.getElementById('game-selection-screen');
             if (gameScreen) gameScreen.style.setProperty('display', 'block', 'important');
             const loginScreen = document.getElementById('login-screen');
             if (loginScreen) loginScreen.style.setProperty('display', 'none', 'important');
        } else {
            showLoginScreen();
        }
    } catch (e) {
        console.error(e);
    }
};

function showLoginScreen() {
    try {
        // Hide all other screens if they exist
        const gameScreen = document.getElementById('game-selection-screen');
        const stakeScreen = document.getElementById('stake-screen');
        const gameBoard = document.getElementById('game-board');
        const appContainer = document.getElementById('app-container');
        const mainContent = document.getElementById('main-content');

        if (gameScreen) gameScreen.style.setProperty('display', 'none', 'important');
        if (stakeScreen) stakeScreen.style.setProperty('display', 'none', 'important');
        if (gameBoard) gameBoard.style.setProperty('display', 'none', 'important');
        
        // Ensure app-container and main-content are NOT hidden
        if (appContainer) appContainer.style.display = 'block';
        if (mainContent) mainContent.style.display = 'block';

        const loginScreen = document.getElementById('login-screen');
        if (loginScreen) {
            loginScreen.style.setProperty('display', 'block', 'important');
        } else {
            console.error("login-screen element not found!");
            alert("Error: Login screen missing in HTML!");
        }
    } catch (e) {
        alert("showLoginScreen error: " + e.message);
    }
}

async function login() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    const errorMsg = document.getElementById('statusMessage');

    if (!username || !password) {
        if (errorMsg) errorMsg.innerHTML = '<div class="alert alert-danger">Please enter username and password</div>';
        return;
    }

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();
        if (data.success) {
            window.location.href = data.redirect || '/';
        } else {
            if (errorMsg) errorMsg.innerHTML = `<div class="alert alert-danger">${data.message}</div>`;
        }
    } catch (e) {
        if (errorMsg) errorMsg.innerHTML = '<div class="alert alert-danger">Login failed</div>';
    }
}

async function refreshBalance() {
    try {
        const response = await fetch('/api/user/balance');
        const data = await response.json();
        if (data.balance !== undefined) {
            const balanceEl = document.getElementById('walletBalance');
            if (balanceEl) balanceEl.innerText = data.balance.toFixed(2);
        }
    } catch (e) {
        console.error("Balance refresh failed", e);
    }
}

async function buyCard(roomId) {
    const response = await fetch(`/buy-card/${roomId}`, { method: 'POST' });
    const data = await response.json();
    const messageDiv = document.getElementById('statusMessage');
    
    if (data.success) {
        const balanceEl = document.getElementById('walletBalance');
        if (balanceEl) balanceEl.innerText = data.new_balance.toFixed(2);
        
        const playerEl = document.getElementById(`playerCount-${roomId}`);
        if (playerEl && data.players !== undefined) playerEl.innerText = data.players;
        
        const prizeEl = document.getElementById(`prizeAmount-${roomId}`);
        if (prizeEl && data.prize !== undefined) prizeEl.innerText = data.prize.toFixed(2);
        
        if (messageDiv) messageDiv.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
    } else {
        if (messageDiv) messageDiv.innerHTML = `<div class="alert alert-danger">${data.message}</div>`;
    }
}
