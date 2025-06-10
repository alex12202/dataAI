<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $message = $_POST['message'] ?? '';
    $conversationId = $_POST['conversation_id'] ?? 'default-session';
    $systemMessage = "You are a helpful assistant."; // Or allow dynamic input

    $apiUrl = 'http://backend:8000/api/v1/chat_completion';

    $payload = json_encode([
        'user_message' => $message,
        'system_message' => $systemMessage,
        'conversation_id' => $conversationId
    ]);

    $ch = curl_init($apiUrl);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json'
    ]);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);

    $response = curl_exec($ch);
    $error = curl_error($ch);
    curl_close($ch);

    if ($error) {
        http_response_code(500);
        echo "Error calling API: $error";
    } else {
        header('Content-Type: application/json');
        echo $response;
    }
}
