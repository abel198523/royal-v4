// game.js - Corrected logic to show login-screen by default
window.onload = () => {
    console.log("Game initialized");
    showLoginScreen();
};

function showLoginScreen() {
    // Hide all other screens if they exist
    const gameScreen = document.getElementById('game-selection-screen');
    const stakeScreen = document.getElementById('stake-screen');
    const gameBoard = document.getElementById('game-board');
    const appContainer = document.getElementById('app-container');
    const mainContent = document.getElementById('main-content');

    if (gameScreen) gameScreen.style.display = 'none';
    if (stakeScreen) stakeScreen.style.display = 'none';
    if (gameBoard) gameBoard.style.display = 'none';
    
    // Ensure app-container and main-content are NOT hidden
    if (appContainer) appContainer.style.display = 'block';
    if (mainContent) mainContent.style.display = 'block';

    const loginScreen = document.getElementById('login-screen');
    if (loginScreen) {
        loginScreen.style.display = 'block';
    } else {
        console.error("login-screen element not found!");
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

    // For now, redirecting to signup as requested or simulating login
    // In a real scenario, this would be a fetch to /login
    window.location.href = "/signup";
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
