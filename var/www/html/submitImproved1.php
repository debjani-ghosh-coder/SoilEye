<?php
// submitImproved1.php

// Set the default timezone
date_default_timezone_set("Asia/Kolkata");

// Define paths
$photo_path = '/home/pi/Documents/Debjani/Soil/';
$csv_aggregate_path = '/home/pi/Documents/Debjani/Farmer/farmer_details.csv';
$csv_individual_dir = '/home/pi/Documents/Debjani/Farmer/';
$python_script = '/home/pi/Documents/Debjani/SHC/SHC2.py';
$pdf_output_dir = '/var/www/html/';
$pdf_archive_dir = '/home/pi/Documents/Debjani/SHC/Archive_SHC/';
$testing_csv = '/home/pi/Documents/Debjani/testing.csv';



// Function to sanitize input
function sanitize_input($data) {
    return htmlspecialchars(strip_tags(trim($data)));
}

// Function to validate name
function validate_name($name) {
    $name_parts = explode(" ", $name);
    if (count($name_parts) < 2 || count($name_parts) > 3) {
        return "Please enter First Name and Last Name. Middle Name is optional.";
    }
    foreach ($name_parts as $part) {
        if (!preg_match("/^[A-Za-z]+$/", $part)) {
            return "Name should contain only letters.";
        }
    }
    return "";
}

// Function to validate email
function validate_email($email) {
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        return "Please enter a valid email address.";
    }
    return "";
}

// Function to validate address
function validate_address($address) {
    if (strpos($address, ",") === false) {
        return "Address should contain at least one comma.";
    }
    return "";
}

// Function to validate location
function validate_location($location) {
    $parts = explode(" ", $location);
    if (count($parts) != 2) {
        return "Location should have two numerical values separated by a space.";
    }
    list($lat, $long) = $parts;
    if (!is_numeric($lat) || !is_numeric($long)) {
        return "Latitude and Longitude must be valid numbers.";
    }
    return "";
}

// Function to validate Khasra number
function validate_khasra($khasra) {
    if (empty($khasra)) {
        return "Khasra number cannot be empty.";
    }
    if (!preg_match("/^[A-Za-z0-9\-]+$/", $khasra)) {
        return "Khasra number should contain only letters, numbers, or hyphens.";
    }
    return "";
}

// Function to validate farm size
function validate_farm_size($farm_size) {
    if (empty($farm_size)) {
        return "Farm size cannot be empty.";
    }
    if (!preg_match("/^\d+\s?sqft$/i", $farm_size)) {
        return "Farm size should be a number followed by 'sqft'. Example: 1500 sqft";
    }
    return "";
}

// Function to validate photo
function validate_photo($file) {
    if ($file['error'] !== UPLOAD_ERR_OK) {
        return "Error uploading the photo.";
    }

    // Check MIME type
    $finfo = finfo_open(FILEINFO_MIME_TYPE);
    $mime_type = finfo_file($finfo, $file['tmp_name']);
    finfo_close($finfo);
    if ($mime_type !== 'image/jpeg') {
        return "Only JPEG images are allowed.";
    }

    // Check file extension
    $ext = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
    if (!in_array($ext, ['jpg', 'jpeg'])) {
        return "Only JPEG images are allowed.";
    }

    // Optional: Check file size (e.g., max 5MB)
    $max_size = 5 * 1024 * 1024; // 5MB
    if ($file['size'] > $max_size) {
        return "Photo size should not exceed 5MB.";
    }

    return "";
}

// Initialize variables
$errors = [];
$name = $email = $address = $location = $survey_no = $farm_size = $crop_name = "";

// Check if the form has been submitted via POST
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Sanitize inputs
    $name = sanitize_input($_POST['name'] ?? '');
    $email = sanitize_input($_POST['email'] ?? '');
    $address = sanitize_input($_POST['address'] ?? '');
    $location = sanitize_input($_POST['location'] ?? '');
    $survey_no = sanitize_input($_POST['survey_no'] ?? '');
    $farm_size = sanitize_input($_POST['farm_size'] ?? '');
    $crop_checkbox = isset($_POST['crop_checkbox']) ? true : false;
    $crop_name = sanitize_input($_POST['crop_name'] ?? '');

    // Validate inputs
    $name_error = validate_name($name);
    if ($name_error !== "") {
        $errors['name'] = $name_error;
    }

    $email_error = validate_email($email);
    if ($email_error !== "") {
        $errors['email'] = $email_error;
    }

    $address_error = validate_address($address);
    if ($address_error !== "") {
        $errors['address'] = $address_error;
    }

    $location_error = validate_location($location);
    if ($location_error !== "") {
        $errors['location'] = $location_error;
    }

    $khasra_error = validate_khasra($survey_no);
    if ($khasra_error !== "") {
        $errors['survey_no'] = $khasra_error;
    }

    $farm_size_error = validate_farm_size($farm_size);
    if ($farm_size_error !== "") {
        $errors['farm_size'] = $farm_size_error;
    }

    if ($crop_checkbox) {
        if (empty($crop_name)) {
            $errors['crop_name'] = "Crop name cannot be empty.";
        }
    } else {
        $crop_name = ""; // Ensure it's empty if not selected
    }

    // Validate photo
    if (isset($_FILES['photo'])) {
        $photo_error = validate_photo($_FILES['photo']);
        if ($photo_error !== "") {
            $errors['photo'] = $photo_error;
        }
    } else {
        $errors['photo'] = "Photo is required.";
    }

    // If there are errors, display them to the user
    if (!empty($errors)) {
        echo '<!DOCTYPE html>
        <html>
        <head>
            <title>Submission Errors</title>
            <style>
                body { background-color: #000; color: #0eff00; font-family: Arial, sans-serif; padding: 20px; }
                .error { color: #f00; }
                a { color: #2cb814; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>There were errors in your submission:</h1>
            <ul>';
        foreach ($errors as $field => $error) {
            echo '<li><strong>' . ucfirst($field) . ':</strong> ' . $error . '</li>';
        }
        echo '</ul>
            <a href="index.html">Go Back to the Form</a>
        </body>
        </html>';
        exit;
    }

    // At this point, all validations have passed

    // Prepare data for CSV
    $date_collected = date("d-m-Y");

    // Sanitize name for filename
    $sanitized_name = preg_replace('/[^A-Za-z0-9\-]/', '', str_replace(" ", "_", $name));
    $timestamp = time();
    $pdf_filename = "SoilHealthCard_" . $sanitized_name . "_" . $survey_no . "_" . $timestamp . ".pdf";

    // Handle photo upload
    if (isset($_FILES['photo']) && $_FILES['photo']['error'] === UPLOAD_ERR_OK) {
        // Generate a unique filename to prevent overwriting
        $photo_ext = strtolower(pathinfo($_FILES['photo']['name'], PATHINFO_EXTENSION));
        $unique_photo_name = $survey_no . "_" . $timestamp . "." . $photo_ext;
        $destination = $photo_path . $unique_photo_name;

        // Ensure the upload directory exists
        if (!is_dir($photo_path)) {
            mkdir($photo_path, 0755, true);
        }

        // Move the uploaded file to the designated folder
        if (!move_uploaded_file($_FILES['photo']['tmp_name'], $destination)) {
            echo '<!DOCTYPE html>
            <html>
            <head>
                <title>Upload Error</title>
                <style>
                    body { background-color: #000; color: #f00; font-family: Arial, sans-serif; padding: 20px; }
                    a { color: #2cb814; text-decoration: none; }
                    a:hover { text-decoration: underline; }
                </style>
            </head>
            <body>
                <h1>Failed to upload the photo.</h1>
                <a href="index.html">Go Back to the Form</a>
            </body>
            </html>';
            exit;
        }
    }

    // Prepare CSV data
    // Escape double quotes by doubling them and wrap fields in quotes to handle commas
    function escape_csv_field($field) {
        $field = str_replace('"', '""', $field);
        return '"' . $field . '"';
    }

    $csv_data = [
        $name,
        $email,
        $address,
        $location,
        $date_collected,
        $survey_no,
        $farm_size,
        //$crop_name
    ];

    $csv_line = implode(",", array_map('escape_csv_field', $csv_data)) . "\n";

    // Save to individual CSV file based on survey_no
    $individual_csv_path = $csv_individual_dir . $survey_no . '.csv';
    if (!file_put_contents($individual_csv_path, $csv_line, FILE_APPEND | LOCK_EX)) {
        echo '<!DOCTYPE html>
        <html>
        <head>
            <title>File Write Error</title>
            <style>
                body { background-color: #000; color: #f00; font-family: Arial, sans-serif; padding: 20px; }
                a { color: #2cb814; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>Failed to write data to the individual CSV file.</h1>
            <a href="index.html">Go Back to the Form</a>
        </body>
        </html>';
        exit;
    }

    // Save to aggregate CSV file
    if (!file_put_contents($csv_aggregate_path, $csv_line, FILE_APPEND | LOCK_EX)) {
        echo '<!DOCTYPE html>
        <html>
        <head>
            <title>File Write Error</title>
            <style>
                body { background-color: #000; color: #f00; font-family: Arial, sans-serif; padding: 20px; }
                a { color: #2cb814; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>Failed to write data to the aggregate CSV file.</h1>
            <a href="index.html">Go Back to the Form</a>
        </body>
        </html>';
        exit;
    }

    // Execute the Python script to generate the PDF
    // Construct the command with proper escaping
    // $command = escapeshellcmd("/home/pi/shc_env/bin/python $python_script \"$csv_aggregate_path\" \"$testing_csv\" \"$destination\" \"$pdf_filename\"");
       $command = "/var/www/html/shc_env_apache/bin/python /home/pi/Documents/Debjani/SHC/SHC2.py "
     . escapeshellarg($csv_aggregate_path) . " "
     . escapeshellarg($testing_csv) . " "
     . escapeshellarg($destination) . " "
     . escapeshellarg($pdf_filename);
     
   // exec($command, $output, $status);
    // Optional: Log the command for debugging
    // file_put_contents('/home/ggpi/Documents/Debjani/SHC/command_log.txt', $command . "\n", FILE_APPEND);

    // Execute the command and capture output and return status
    $output = [];
    $return_var = 0;
    exec($command, $output, $return_var);
    $start_time = time();

    if ($return_var !== 0) {
        // Log the error for debugging
        file_put_contents('/home/pi/Documents/Debjani/SHC/error_log.txt', date("d-m-Y H:i:s") . " - Command failed: $command\nOutput: " . implode("\n", $output) . "\n", FILE_APPEND);
        echo '<!DOCTYPE html>
        <html>
        <head>
            <title>Processing Error</title>
            <style>
                body { background-color: #000; color: #f00; font-family: Arial, sans-serif; padding: 20px; }
                a { color: #2cb814; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>There was an error processing your request.</h1>
            <a href="index.html">Go Back to the Form</a>
        </body>
        </html>';
        exit;
    }

    // Define the source and archive PDF paths
    $source_pdf = $pdf_output_dir . $pdf_filename;
    $archive_pdf = $pdf_archive_dir . $sanitized_name . "_" . $survey_no . "_SoilHealthCard_" . $timestamp . ".pdf";

    // Check if the PDF was generated successfully
    if (file_exists($source_pdf)) {
       
        // End time for loading symbol
        $end_time = time();
        // Calculate the time taken and display it
        $time_taken = $end_time - $start_time;
       
        if (!is_dir($pdf_archive_dir)) {
            mkdir($pdf_archive_dir, 0755, true);
        }

        // Copy the PDF to the archive folder
        if (!copy($source_pdf, $archive_pdf)) {
            echo '<!DOCTYPE html>
            <html>
            <head>
                <title>Archival Error</title>
                <style>
                    body { background-color: #000; color: #f00; font-family: Arial, sans-serif; padding: 20px; }
                    a { color: #2cb814; text-decoration: none; }
                    a:hover { text-decoration: underline; }
                </style>
            </head>
            <body>
                <h1>PDF generated but failed to archive.</h1>
                <a href="/' . htmlspecialchars($pdf_filename) . '" download>Download PDF</a>
            </body>
            </html>';
            exit;
        }

        // Set appropriate permissions for the PDF
        chmod($source_pdf, 0644);

        // Provide the download link to the user
        echo '<!DOCTYPE html>
        <html>
        <head>
            <title>Submission Successful</title>
            <style>
                body { background-color: #000; color: #0eff00; font-family: Arial, sans-serif; padding: 20px; text-align: center; }
                a { color: #2cb814; text-decoration: none; }
                a:hover { text-decoration: underline; }
                h1 { color: #2cb814; }
            </style>
        </head>
        <body>
            <h1>Your data has been uploaded successfully!</h1>
            <p>Please wait while we generate your PDF...</p>
            <p>PDF generated successfully in seconds.</p>
            
            
            <p><a href="/' . htmlspecialchars($pdf_filename) . '" download>Download PDF</a></p>
            <!-- Embed the PDF in an iframe -->
            <iframe src="/' . htmlspecialchars($pdf_filename) . '" width="800" height="600">
                This browser does not support PDFs. Please download the PDF to view it: <a href="/' . htmlspecialchars($pdf_filename) . '">Download PDF</a>
            </iframe>
            <p><a href="index.html">Submit Another Response</a></p>
        </body>
        </html>';
    } else {
        echo '<!DOCTYPE html>
        <html>
        <head>
            <title>PDF Generation Error</title>
            <style>
                body { background-color: #000; color: #f00; font-family: Arial, sans-serif; padding: 20px; }
                a { color: #2cb814; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>PDF was not generated successfully.</h1>
            <a href="index.html">Go Back to the Form</a>
        </body>
        </html>';
    }

} else {
    // If the form hasn't been submitted, redirect to the form page
    header("Location: index.html");
    exit;
}
?>
