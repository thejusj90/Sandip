<?php
// FullChoice Breath — contact form handler for Hostinger (PHP mail())
header('Content-Type: application/json');

// EDIT THIS: where the consultation requests should be sent
$to = "you@yourdomain.com";

$data = json_decode(file_get_contents("php://input"), true);
$email = isset($data['email']) ? trim($data['email']) : '';

if (!$email || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(400);
    echo json_encode(["ok" => false, "error" => "Invalid email"]);
    exit;
}

$subject = "New FullChoice Breath consultation request";
$message = "A visitor requested a consultation.\n\nEmail: $email\n\nSubmitted: " . date("Y-m-d H:i:s");
$headers = "From: no-reply@" . $_SERVER['HTTP_HOST'] . "\r\n" .
           "Reply-To: $email\r\n" .
           "Content-Type: text/plain; charset=UTF-8";

$sent = mail($to, $subject, $message, $headers);

if ($sent) {
    echo json_encode(["ok" => true]);
} else {
    http_response_code(500);
    echo json_encode(["ok" => false, "error" => "Mail could not be sent"]);
}
