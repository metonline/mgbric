/**
 * BBO Hand Display Component
 * Displays bridge hands in BBO standard format
 */

// Suit symbols
const SUITS = {
    'S': '♠',
    'H': '♥',
    'D': '♦',
    'C': '♣'
};

// Suit colors for BBO style
const SUIT_COLORS = {
    'S': '#000000',  // Black
    'H': '#FF0000',  // Red
    'D': '#FF0000',  // Red
    'C': '#000000'   // Black
};

/**
 * Format a single hand in BBO style
 * Input: {S: "AKJ", H: "Q542", D: "987", C: "T64"}
 * Output: "♠AKJ ♥Q542 ♦987 ♣T64"
 */
function formatHandBBO(hand) {
    if (!hand) return '';
    
    let result = '';
    const suits = ['S', 'H', 'D', 'C'];
    
    for (let suit of suits) {
        const cards = hand[suit] || '';
        if (result) result += ' ';
        result += `${SUITS[suit]}${cards}`;
    }
    
    return result;
}

/**
 * Format complete deal in BBO style for display
 * Shows all 4 hands in proper layout
 */
function formatDealBBO(deal) {
    if (!deal) return '';
    
    const n = formatHandBBO(deal.N);
    const s = formatHandBBO(deal.S);
    const e = formatHandBBO(deal.E);
    const w = formatHandBBO(deal.W);
    
    return {
        N: n,
        S: s,
        E: e,
        W: w
    };
}

/**
 * Create HTML for BBO hand display
 */
function createHandHTML(dealNumber, deal) {
    const formatted = formatDealBBO(deal);
    
    const html = `
        <div class="bbo-hand-display">
            <div class="bbo-board-number">Board ${dealNumber}</div>
            <table class="bbo-hand-table">
                <tr>
                    <td colspan="3" class="bbo-north">${formatted.N}</td>
                </tr>
                <tr>
                    <td class="bbo-west">${formatted.W}</td>
                    <td class="bbo-center">
                        <div class="bbo-compass">N</div>
                        <div class="bbo-compass">W E</div>
                        <div class="bbo-compass">S</div>
                    </td>
                    <td class="bbo-east">${formatted.E}</td>
                </tr>
                <tr>
                    <td colspan="3" class="bbo-south">${formatted.S}</td>
                </tr>
            </table>
        </div>
    `;
    
    return html;
}

/**
 * Load hands and display them
 */
async function loadAndDisplayHands(tournamentId) {
    try {
        const response = await fetch('/api/hands');
        const hands = await response.json();
        
        if (!hands || Object.keys(hands).length === 0) {
            return '<p>No hands available for this tournament</p>';
        }
        
        let html = '<div class="bbo-hands-container">';
        
        for (let boardNum in hands) {
            html += createHandHTML(boardNum, hands[boardNum]);
        }
        
        html += '</div>';
        
        return html;
    } catch (error) {
        console.error('Error loading hands:', error);
        return '<p>Error loading hands</p>';
    }
}

/**
 * Show hands in a modal
 */
function showHandsModal(tournamentId, tournamentName) {
    const modal = document.createElement('div');
    modal.className = 'hands-modal';
    modal.innerHTML = `
        <div class="hands-modal-content">
            <div class="hands-modal-header">
                <h2>${tournamentName} - Hands</h2>
                <button class="hands-modal-close">&times;</button>
            </div>
            <div class="hands-modal-body" id="handsContainer">
                <p>Loading hands...</p>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close button
    modal.querySelector('.hands-modal-close').addEventListener('click', () => {
        modal.remove();
    });
    
    // Load hands
    loadAndDisplayHands(tournamentId).then(html => {
        document.getElementById('handsContainer').innerHTML = html;
    });
    
    // Close on background click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// Export functions
window.BBOHands = {
    formatHandBBO,
    formatDealBBO,
    createHandHTML,
    loadAndDisplayHands,
    showHandsModal
};
