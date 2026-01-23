/**
 * DD Solver Integration Module
 * Embeds Double Dummy results on hand diagrams
 * Displays optimal tricks for each player/denomination
 */

// Cache for DD results
let ddResultsCache = {};

/**
 * Load DD results from file
 */
async function loadDDResults() {
    try {
        const response = await fetch('/double_dummy/dd_results.json');
        if (!response.ok) throw new Error('Failed to load DD results');
        
        const data = await response.json();
        ddResultsCache = data.boards || {};
        console.log(`✓ Loaded DD data for ${Object.keys(ddResultsCache).length} boards`);
        return ddResultsCache;
    } catch (error) {
        console.error('Error loading DD results:', error);
        return {};
    }
}

/**
 * Get DD data for a specific board
 */
function getDDData(eventId, boardNum) {
    const key = `${eventId}_${boardNum}`;
    return ddResultsCache[key] || null;
}

/**
 * Create DD tricks table for display
 * Shows tricks made by each player in each denomination
 */
function createDDTricksTable(ddData) {
    if (!ddData || !ddData.tricks) {
        return '<div class="dd-unavailable">DD Data Not Available</div>';
    }
    
    const tricks = ddData.tricks;
    const suits = ['S', 'H', 'D', 'C', 'NT'];
    const suitSymbols = { 'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣', 'NT': 'NT' };
    const players = ['N', 'E', 'S', 'W'];
    
    let html = `<div class="dd-tricks-table-wrapper">
        <table class="dd-tricks-table">
            <thead>
                <tr>
                    <th></th>`;
    
    for (let suit of suits) {
        html += `<th class="dd-suit dd-suit-${suit.toLowerCase()}">${suitSymbols[suit]}</th>`;
    }
    html += `</tr>
            </thead>
            <tbody>`;
    
    for (let player of players) {
        const playerData = tricks[player] || {};
        html += `<tr class="dd-player-row dd-player-${player}">
                    <td class="dd-player-label">${player}</td>`;
        
        for (let suit of suits) {
            const trickCount = playerData[suit] || '-';
            const suitClass = suit.toLowerCase();
            html += `<td class="dd-trick-cell dd-suit-${suitClass}">${trickCount}</td>`;
        }
        html += `</tr>`;
    }
    
    html += `</tbody>
        </table>
    </div>`;
    
    return html;
}

/**
 * Create a summary badge showing NS vs EW trick difference
 */
function createDDSummaryBadge(ddData) {
    if (!ddData || !ddData.tricks) return '';
    
    const tricks = ddData.tricks;
    
    // Calculate total tricks for NS and EW at NoTrump
    const nsNT = (tricks.N?.NT || 0) + (tricks.S?.NT || 0);
    const ewNT = (tricks.E?.NT || 0) + (tricks.W?.NT || 0);
    const ntContract = Math.ceil(nsNT / 3);  // 3NT if possible, 4NT, etc.
    
    return `<div class="dd-summary-badge">
        <span class="dd-ns-tricks">${nsNT}</span><span class="dd-separator">-</span><span class="dd-ew-tricks">${ewNT}</span>
        <span class="dd-contract">${ntContract}NT</span>
    </div>`;
}

/**
 * Enhance hand HTML with DD results
 */
function enhanceHandWithDD(handHTML, eventId, boardNum) {
    const ddData = getDDData(eventId, boardNum);
    if (!ddData) return handHTML;
    
    // Create wrapper
    const wrapper = document.createElement('div');
    wrapper.className = 'hand-with-dd-wrapper';
    wrapper.innerHTML = handHTML;
    
    // Add DD section
    const ddSection = document.createElement('div');
    ddSection.className = 'dd-section';
    ddSection.innerHTML = `
        <div class="dd-header">
            <h4>Double Dummy Analysis</h4>
            <small>Optimal Tricks (Perfect Defense)</small>
        </div>
        ${createDDSummaryBadge(ddData)}
        ${createDDTricksTable(ddData)}
    `;
    
    wrapper.appendChild(ddSection);
    return wrapper.innerHTML;
}

/**
 * Display DD info in a modal/popover
 */
function showDDModal(eventId, boardNum) {
    const ddData = getDDData(eventId, boardNum);
    if (!ddData) {
        alert('Double Dummy data not available for this board');
        return;
    }
    
    const modal = document.createElement('div');
    modal.className = 'dd-modal';
    modal.innerHTML = `
        <div class="dd-modal-content">
            <div class="dd-modal-header">
                <h2>Board ${boardNum} - Double Dummy Analysis</h2>
                <button class="dd-modal-close" onclick="this.parentElement.parentElement.remove()">✕</button>
            </div>
            <div class="dd-modal-body">
                <p><strong>Event:</strong> ${eventId}</p>
                <p><strong>Dealer:</strong> ${ddData.dealer || '-'}</p>
                <p><strong>Vulnerability:</strong> ${ddData.vuln || '-'}</p>
                <hr>
                ${createDDTricksTable(ddData)}
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async function() {
    console.log('🔄 Loading DD Solver results...');
    await loadDDResults();
    console.log('✓ DD Solver initialized and ready');
});
