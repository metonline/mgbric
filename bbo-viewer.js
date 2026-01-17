/**
 * BBO Hands Viewer - Simple iframe embed
 * Uses BridgeBase Online hand viewer
 */

/**
 * Convert bridge hand to LIN format for BBO
 * LIN format: ST|md,<dealer>,<hand1>,<hand2>,<hand3>,<hand4>
 */
function handToLIN(hand, dealerIndex = 0) {
    // Convert hands: {S: "AKQ", H: "654", D: "32", C: "876"}
    // to LIN format: SAKQH654D32C876
    
    function formatHandLIN(h) {
        if (!h) return '';
        let lin = '';
        const suits = ['S', 'H', 'D', 'C'];
        for (let suit of suits) {
            lin += suit + (h[suit] || '');
        }
        return lin;
    }
    
    // Order: S, W, N, E (dealer index determines rotation)
    const positions = ['S', 'W', 'N', 'E'];
    const rotated = positions.slice(dealerIndex).concat(positions.slice(0, dealerIndex));
    
    let hands = '';
    for (let pos of rotated) {
        hands += formatHandLIN(hand[pos]);
    }
    
    // Dealer encoding: 0=N, 1=E, 2=S, 3=W
    const dealerCode = ['n', 'e', 's', 'w'][dealerIndex] || 'n';
    
    return `st|md,${dealerCode},${hands}`;
}

/**
 * Generate BBO iframe URL
 */
function generateBBOURL(hand, dealerIndex = 0) {
    const lin = handToLIN(hand, dealerIndex);
    return `https://www.bridgebase.com/tools/handviewer.html?bbo=y&lin=${lin}`;
}

/**
 * Create HTML for BBO hand viewer
 */
function createBBOHandHTML(boardNum, hand, dealerIndex = 0, dealerName = 'N', vulnerable = 'None') {
    const bboURL = generateBBOURL(hand, dealerIndex);
    
    return `
        <div class="bbo-hand-card">
            <div class="bbo-hand-header">
                <div class="bbo-board-info">
                    <span class="bbo-board-num">Board ${boardNum}</span>
                    <span class="bbo-dealer">Dealer: ${dealerName}</span>
                    <span class="bbo-vulnerable">Vulnerable: ${vulnerable}</span>
                </div>
                <a href="${bboURL}" target="_blank" class="bbo-open-btn" title="Open in new tab">
                    🌐 Open in BBO
                </a>
            </div>
            <div class="bbo-hand-viewer">
                <iframe 
                    src="${bboURL}"
                    allow="clipboard-read; clipboard-write"
                    title="BBO Hand Viewer - Board ${boardNum}"
                    loading="lazy"
                    sandbox="allow-same-origin allow-scripts allow-popups allow-popups-to-escape-sandbox">
                </iframe>
            </div>
        </div>
    `;
}

/**
 * Display all hands for a tournament
 */
async function displayTournamentHands(containerId, tournamentId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    try {
        // Load hands database
        const response = await fetch('/api/hands');
        const handsDB = await response.json();
        
        if (!handsDB || Object.keys(handsDB).length === 0) {
            container.innerHTML = '<p class="no-hands">No hands available for this tournament</p>';
            return;
        }
        
        // Display all hands
        let html = '<div class="bbo-hands-grid">';
        
        for (let boardNum in handsDB) {
            const hand = handsDB[boardNum];
            html += createBBOHandHTML(boardNum, hand);
        }
        
        html += '</div>';
        container.innerHTML = html;
        
        // Add event listeners for external links
        container.querySelectorAll('.bbo-open-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                window.open(btn.href, '_blank', 'width=1200,height=800');
            });
        });
        
    } catch (error) {
        console.error('Error loading hands:', error);
        container.innerHTML = '<p class="error">Error loading hands data</p>';
    }
}

/**
 * Open hands in modal
 */
function showHandsModal(tournamentName) {
    const modal = document.createElement('div');
    modal.className = 'bbo-modal';
    modal.innerHTML = `
        <div class="bbo-modal-content">
            <div class="bbo-modal-header">
                <h2>${tournamentName} - Bridge Hands</h2>
                <button class="bbo-modal-close">&times;</button>
            </div>
            <div class="bbo-modal-body" id="bboHandsContainer">
                <p>Loading hands...</p>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close handlers
    modal.querySelector('.bbo-modal-close').addEventListener('click', () => modal.remove());
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
    });
    
    // Load hands
    displayTournamentHands('bboHandsContainer');
}

// Export
window.BBOViewer = {
    handToLIN,
    generateBBOURL,
    createBBOHandHTML,
    displayTournamentHands,
    showHandsModal
};
