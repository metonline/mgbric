/**
 * LIN Generation Module
 * Handles conversion of bridge hands to LIN format
 * Separated from display/diagram placement logic
 */

/**
 * Convert hand object to LIN format
 * LIN format: SAxxxHxxxDxxxCxxx (suit letter followed by cards)
 * @param {Object} hand - Hand object with S, H, D, C properties
 * @returns {string} - LIN formatted hand string
 */
function handToPBN(hand) {
    if (!hand) return '';
    const suits = ['S', 'H', 'D', 'C'];
    let pbn = '';
    for (let suit of suits) {
        pbn += suit + (hand[suit] || '');
    }
    return pbn;
}

/**
 * Convert compass position hand string (S.H.D.C) to LIN format
 * @param {string} handStr - Hand string in format "AKQ.JT.987.654"
 * @returns {string} - LIN formatted hand string
 */
function handStringToLIN(handStr) {
    if (!handStr) return '';
    const [s, h, d, c] = handStr.split('.');
    return 'S' + (s || '') + 'H' + (h || '') + 'D' + (d || '') + 'C' + (c || '');
}

/**
 * Generate complete LIN string for BBO hand viewer
 * @param {Object} hand - Hand object with N, E, S, W properties (compass positions)
 * @param {string} dealer - Dealer position (N, E, S, W)
 * @param {string} vulnerability - Vulnerability (None, NS, EW, Both)
 * @returns {string} - Complete LIN string for BBO
 */
function generateBBOLIN(hand, dealer, vulnerability) {
    // Map dealer to numeric code (1=N, 2=E, 3=S, 4=W)
    const dealerMap = { 'N': '1', 'E': '2', 'S': '3', 'W': '4' };
    const d = dealerMap[dealer] || '1';
    
    // Map vulnerability to numeric code
    const vulnMap = { 'None': '0', 'NS': '1', 'EW': '2', 'Both': '3' };
    const v = vulnMap[vulnerability] || '0';
    
    // Order hands according to dealer (first 3 hands only, 4th is calculated)
    const dealerOrder = {
        'N': ['N', 'E', 'S'],
        'E': ['E', 'S', 'W'],
        'S': ['S', 'W', 'N'],
        'W': ['W', 'N', 'E']
    };
    
    const ordered = dealerOrder[dealer] || ['N', 'E', 'S'];
    const handStrings = ordered.map(pos => handStringToLIN(hand[pos]));
    const handsStr = handStrings.join(',');
    
    // Format: qx|o1|md|{dealer}{hand1},{hand2},{hand3},|rh||ah|Board {board}|sv|{vuln}|pg||
    return `qx|o1|md|${d}${handsStr},|rh||ah|Board|sv|${v}|pg||`;
}

/**
 * Generate BBO viewer URL from hand data
 * @param {Object} hand - Hand object with N, E, S, W properties
 * @param {string} dealer - Dealer position (N, E, S, W)
 * @param {string} vulnerability - Vulnerability (None, NS, EW, Both)
 * @param {number} boardNum - Board number (for reference)
 * @returns {string} - BBO hand viewer URL
 */
function generateBBOViewerURL(hand, dealer, vulnerability, boardNum = '') {
    const lin = generateBBOLIN(hand, dealer, vulnerability);
    const baseURL = 'https://www.bridgebase.com/tools/handviewer.html';
    return `${baseURL}?lin=${encodeURIComponent(lin)}`;
}

/**
 * Convert hand data to simple comma-separated format for sharing
 * @param {Object} hand - Hand object with N, E, S, W properties
 * @returns {string} - Format: "N hand, E hand, S hand, W hand"
 */
function handToSimpleFormat(hand) {
    const n = hand.N || '-';
    const e = hand.E || '-';
    const s = hand.S || '-';
    const w = hand.W || '-';
    return `${n}, ${e}, ${s}, ${w}`;
}

// Export for Node.js environments (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        handToPBN,
        handStringToLIN,
        generateBBOLIN,
        generateBBOViewerURL,
        handToSimpleFormat
    };
}
