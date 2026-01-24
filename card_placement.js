/**
 * Card Placement & Diagram Display Module
 * Handles rendering bridge hand diagrams with PRESET vulnerability calculation
 * Separated from LIN generation logic
 */

/**
 * Get vulnerability based on board number (PRESET - always same for given board)
 * Standard duplicate bridge pattern (repeats every 32 boards)
 * @param {number} boardNum - Board number
 * @returns {string} - Vulnerability type: 'None', 'NS', 'EW', or 'Both'
 */
function getVulnerabilityByBoard(boardNum) {
    // Standard vulnerability pattern (repeats every 32 boards)
    const vulnMap = {
        1: 'None',  2: 'NS',   3: 'EW',   4: 'Both',
        5: 'None',  6: 'NS',   7: 'EW',   8: 'Both',
        9: 'None',  10: 'NS',  11: 'EW',  12: 'Both',
        13: 'None', 14: 'NS',  15: 'EW',  16: 'Both',
        17: 'None', 18: 'NS',  19: 'EW',  20: 'Both',
        21: 'None', 22: 'NS',  23: 'EW',  24: 'Both',
        25: 'None', 26: 'NS',  27: 'EW',  28: 'Both',
        29: 'None', 30: 'NS',  31: 'EW',  32: 'Both'
    };
    
    // For boards beyond 32, use modulo
    const boardPos = ((boardNum - 1) % 32) + 1;
    return vulnMap[boardPos] || 'None';
}

/**
 * Get CSS color for vulnerability display
 * @param {string} vulnerability - Vulnerability type
 * @returns {string} - Hex color code (always red)
 */
function getVulnerabilityColor(vulnerability) {
    return '#cb0000';  // Red for all vulnerabilities
}

/**
 * Parse hand string from compass notation to object
 * Input: "AKQ.JT9.876.543"
 * Output: {S: "AKQ", H: "JT9", D: "876", C: "543"}
 * @param {string} handStr - Hand in format "S.H.D.C"
 * @returns {Object} - Hand object with suit keys
 */
function parseHandString(handStr) {
    const parts = handStr.split('.');
    if (parts.length !== 4) return null;
    return {
        S: parts[0] || '-',
        H: parts[1] || '-',
        D: parts[2] || '-',
        C: parts[3] || '-'
    };
}

/**
 * Calculate HCP (High Card Points) for a hand
 * A=4, K=3, Q=2, J=1
 * @param {Object} hand - Hand object with S, H, D, C properties
 * @returns {number} - Total HCP count
 */
function calculateHCP(hand) {
    if (!hand || !hand.S) return 0;
    let hcp = 0;
    const cards = (hand.S || '') + (hand.H || '') + (hand.D || '') + (hand.C || '');
    for (const c of cards) {
        if (c === 'A') hcp += 4;
        else if (c === 'K') hcp += 3;
        else if (c === 'Q') hcp += 2;
        else if (c === 'J') hcp += 1;
    }
    return hcp;
}

/**
 * Format a single suit row for diagram display
 * @param {string} suitSymbol - Unicode suit symbol (♠, ♥, ♦, ♣)
 * @param {string} cards - Card notation (e.g., "AKQ")
 * @param {boolean} isRed - Whether suit is red (hearts, diamonds)
 * @returns {string} - HTML for suit row
 */
function formatSuitRow(suitSymbol, cards, isRed) {
    const color = isRed ? 'suit-red' : 'suit-black';
    return `
        <div class="suitRowDivStyle">
            <span class="suitSymbol ${color}">${suitSymbol}</span>
            <span class="suitHolding">${cards || '-'}</span>
        </div>
    `;
}

/**
 * Apply suit colors to text (convert S/H/D/C to colored symbols)
 * @param {string} text - Text with suit letters
 * @returns {string} - HTML with colored suit symbols
 */
function formatSuitWithColor(text) {
    if (!text) return '';
    return text
        .replace(/♠/g, '<span class="suit-black">♠</span>')
        .replace(/♣/g, '<span class="suit-black">♣</span>')
        .replace(/♥/g, '<span class="suit-red">♥</span>')
        .replace(/♦/g, '<span class="suit-red">♦</span>');
}

/**
 * Render Double Dummy analysis table
 * @param {Object} ddResult - DD analysis results with structure {N: {S, H, D, C, NT}, ...}
 * @returns {string} - HTML table for DD results
 */
function renderDDTable(ddResult) {
    if (!ddResult) return '';
    
    const suits = ['S', 'H', 'D', 'C', 'NT'];
    const suitSymbols = {
        'S': '<span class="suit-symbol suit-black">♠</span>',
        'H': '<span class="suit-symbol suit-red">♥</span>',
        'D': '<span class="suit-symbol suit-red">♦</span>',
        'C': '<span class="suit-symbol suit-black">♣</span>',
        'NT': 'NT'
    };
    
    // Format tricks: 7+ shows as 1+, below 7 shows as dash
    function formatTricks(tricks) {
        if (tricks === undefined || tricks === null) return '-';
        if (tricks >= 7) return tricks - 6;
        return '-';
    }
    
    let html = '<table class="bh-dd"><tr><th></th>';
    suits.forEach(s => html += `<th>${suitSymbols[s]}</th>`);
    html += '</tr>';
    
    ['N', 'S', 'E', 'W'].forEach(pos => {
        html += `<tr><td>${pos}</td>`;
        suits.forEach(suit => {
            const tricks = ddResult[pos] ? ddResult[pos][suit] : undefined;
            html += `<td>${formatTricks(tricks)}</td>`;
        });
        html += '</tr>';
    });
    
    html += '</table>';
    return html;
}

function renderHandDiagram(handData, boardNum, ddResult, optimum, lott) {
    if (!handData) {
        return '<div class="hand-diagram-container"><div style="color:#aaa;padding:20px;">Hand data not found</div></div>';
    }

    const handsObj = handData.hands || handData;
    if (!handsObj || !handsObj.N) {
        return '<div class="hand-diagram-container"><div style="color:#aaa;padding:20px;">Invalid hand data</div></div>';
    }

    const n = parseHandString(handsObj.N);
    const s = parseHandString(handsObj.S);
    const e = parseHandString(handsObj.E);
    const w = parseHandString(handsObj.W);

    if (!n || !s || !e || !w) {
        return '<div class="hand-diagram-container"><div style="color:#aaa;padding:20px;">Invalid hand format</div></div>';
    }

    const dealer = handData.dealer || 'N';
    // Calculate vulnerability from board number (PRESET - not from database)
    const vul = getVulnerabilityByBoard(boardNum);
    const date = handData.date || '';

    const hcpN = calculateHCP(n);
    const hcpS = calculateHCP(s);
    const hcpE = calculateHCP(e);
    const hcpW = calculateHCP(w);

    const nDealerClass = dealer === 'N' ? 'dealer-bg' : '';
    const sDealerClass = dealer === 'S' ? 'dealer-bg' : '';
    const eDealerClass = dealer === 'E' ? 'dealer-bg' : '';
    const wDealerClass = dealer === 'W' ? 'dealer-bg' : '';
    
    // Vulnerability styling - color based on vulnerability type (PRESET)
    const vulColor = getVulnerabilityColor(vul);
    const vulClass = 'vul-' + vul.toLowerCase();

    const optimumTextColored = optimum && optimum.text ? formatSuitWithColor(optimum.text) : '';

    const ddTableHtml = ddResult ? `
        <div class="bhDoubleDummy">
            ${renderDDTable(ddResult)}
            ${optimum ? `<div class="par-display"><strong>Par: ${optimum.score || ''}</strong> ${optimumTextColored}</div>` : ''}
        </div>
    ` : '<div class="bhDoubleDummy" style="color:red;text-align:center;padding:10px;">No DD Data</div>';

    const nsFitSuit = lott && lott.ns_fit ? formatSuitWithColor(lott.ns_fit.suit || '?') : '?';
    const ewFitSuit = lott && lott.ew_fit ? formatSuitWithColor(lott.ew_fit.suit || '?') : '?';

    const lottHtml = lott ? `
        <div class="lottDisplay">
            <div class="lott-title">LoTT</div>
            <div class="lott-value">${lott.total_tricks || '?'}</div>
            ${lott.ns_fit ? `
            <div class="lott-detail">
                NS: ${nsFitSuit} (${lott.ns_fit.length || '?'})<br>
                EW: ${ewFitSuit} (${lott.ew_fit?.length || '?'})
            </div>
            ` : ''}
        </div>
    ` : '';

    return `
        <div class="hand-diagram-container">
            <div class="scale-wrapper">
                <div class="mainDivStyle">
                    <!-- Board Info - Left Side -->
                    <div class="board-info-left">
                        <div class="date">${date}</div>
                        <div class="dealer">Dealer: ${dealer}</div>
                        <div class="vul ${vulClass}" style="background-color: ${vulColor} !important; color: white !important; font-weight: bold;">Vuln: ${vul}</div>
                    </div>
                    
                    <!-- HCP Display - Right Side -->
                    <div class="hcp-display">
                        <div class="hcp-north"><span class="hcp-value">${hcpN}</span></div>
                        <div class="hcp-middle">
                            <span class="hcp-value">${hcpW}</span>
                            <span class="hcp-value">${hcpE}</span>
                        </div>
                        <div class="hcp-south"><span class="hcp-value">${hcpS}</span></div>
                    </div>
                
                <!-- North -->
                <div class="nameRowDivStyle pos-n-name ${nDealerClass}" style="background-color: ${vulColor} !important;">
                    <span class="nameInitial">N</span>
                </div>
                <div class="handDivStyle pos-n-hand">
                    ${formatSuitRow('♠', n.S, false)}
                    ${formatSuitRow('♥', n.H, true)}
                    ${formatSuitRow('♦', n.D, true)}
                    ${formatSuitRow('♣', n.C, false)}
                </div>
                
                <!-- West -->
                <div class="nameRowDivStyle pos-w-name ${wDealerClass}" style="background-color: ${vulColor} !important;">
                    <span class="nameInitial">W</span>
                </div>
                <div class="handDivStyle pos-w-hand">
                    ${formatSuitRow('♠', w.S, false)}
                    ${formatSuitRow('♥', w.H, true)}
                    ${formatSuitRow('♦', w.D, true)}
                    ${formatSuitRow('♣', w.C, false)}
                </div>
                
                <!-- Board Number -->
                <div class="vulInnerDivStyle pos-board">${boardNum}</div>
                
                <!-- East -->
                <div class="nameRowDivStyle pos-e-name ${eDealerClass}" style="background-color: ${vulColor} !important;">
                    <span class="nameInitial">E</span>
                </div>
                <div class="handDivStyle pos-e-hand">
                    ${formatSuitRow('♠', e.S, false)}
                    ${formatSuitRow('♥', e.H, true)}
                    ${formatSuitRow('♦', e.D, true)}
                    ${formatSuitRow('♣', e.C, false)}
                </div>
                
                <!-- South -->
                <div class="nameRowDivStyle pos-s-name ${sDealerClass}" style="background-color: ${vulColor} !important;">
                    <span class="nameInitial">S</span>
                </div>
                <div class="handDivStyle pos-s-hand">
                    ${formatSuitRow('♠', s.S, false)}
                    ${formatSuitRow('♥', s.H, true)}
                    ${formatSuitRow('♦', s.D, true)}
                    ${formatSuitRow('♣', s.C, false)}
                </div>
                
                ${ddTableHtml}
                ${lottHtml}
            </div>
            </div>
        </div>
    `;
}

// Export for Node.js environments (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        parseHandString,
        calculateHCP,
        formatSuitRow,
        formatSuitWithColor,
        renderDDTable,
        renderHandDiagram
    };
}
