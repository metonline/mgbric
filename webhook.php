<?php
/**
 * Webhook Bridge for GitHub - Shared Hosting
 * Handles: https://mgbric.info/hosgoru/webhook.php
 */

// Webhook secret
$SECRET = '1440e61bb914225c5e80bb0e5aba7fec';

// Get headers
$payload = file_get_contents('php://input');
$signature = $_SERVER['HTTP_X_HUB_SIGNATURE_256'] ?? '';

// Verify signature
if (!empty($signature)) {
    $expected = 'sha256=' . hash_hmac('sha256', $payload, $SECRET);
    if (!hash_equals($signature, $expected)) {
        http_response_code(401);
        die(json_encode(['error' => 'Invalid signature']));
    }
}

// Log file path
$log_file = __DIR__ . '/webhook.log';

// Log function
function log_msg($msg) {
    global $log_file;
    $timestamp = date('Y-m-d H:i:s');
    file_put_contents($log_file, "[$timestamp] $msg\n", FILE_APPEND);
}

log_msg("Webhook received");

// Parse payload
$data = json_decode($payload, true);

if (!$data) {
    http_response_code(400);
    log_msg("Invalid JSON payload");
    die(json_encode(['error' => 'Invalid JSON']));
}

// Check if it's a push event
if (isset($data['ref']) && $data['ref'] === 'refs/heads/main') {
    log_msg("Push to main branch detected");
    
    // Run update script
    $script = __DIR__ . '/auto_update_vugraph.py';
    if (file_exists($script)) {
        $cmd = '/usr/bin/python3 ' . escapeshellarg($script) . ' >> ' . escapeshellarg($log_file) . ' 2>&1 &';
        shell_exec($cmd);
        
        log_msg("Update script triggered");
        http_response_code(200);
        echo json_encode(['status' => 'ok', 'message' => 'Database update in progress']);
    } else {
        log_msg("ERROR: auto_update_vugraph.py not found at $script");
        http_response_code(500);
        echo json_encode(['error' => 'Script not found']);
    }
} else {
    http_response_code(200);
    log_msg("Event received but not a push to main");
    echo json_encode(['status' => 'ok', 'message' => 'Event logged']);
}
?>
