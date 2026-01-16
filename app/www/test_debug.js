// Test script - hands_viewer.html console test
console.log("=== HANDS VIEWER DEBUG ===");

// Simulate loading
async function testLoadHandsViewer() {
    console.log("1. Checking hands_database.json...");
    
    try {
        const response = await fetch('hands_database.json?v=' + Date.now());
        console.log("   Response status:", response.status);
        
        if (!response.ok) {
            console.error("   ERROR: Not OK response");
            return;
        }
        
        const data = await response.json();
        console.log("   Data loaded successfully!");
        console.log("   Events count:", Object.keys(data.events).length);
        
        const eventKeys = Object.keys(data.events);
        if (eventKeys.length > 0) {
            const firstEvent = data.events[eventKeys[0]];
            console.log("   First event:", firstEvent.name);
            console.log("   Date:", firstEvent.date);
            console.log("   Boards count:", Object.keys(firstEvent.boards).length);
            
            const firstBoard = firstEvent.boards['1'];
            if (firstBoard) {
                console.log("   First board dealer:", firstBoard.dealer);
                console.log("   First board vulnerability:", firstBoard.vulnerability);
                console.log("   North hand:", firstBoard.hands.North);
                console.log("   South hand:", firstBoard.hands.South);
                console.log("   East hand:", firstBoard.hands.East);
                console.log("   West hand:", firstBoard.hands.West);
            }
        }
    } catch (error) {
        console.error("ERROR:", error);
    }
}

// Run test
testLoadHandsViewer();
