<?php 
session_start(); // Start the session at the beginning of the script

if (isset($_POST['submitFileUpload']) && isset($_FILES['fileToUpload'])) {
    $target_dir = '/opt/lampp/htdocs/vulnerable_app/uploads'; 
    $photo_path = explode(".", $_FILES['fileToUpload']['name']);
    $basename = $photo_path[0];
    $extension = $photo_path[1];
    $target_file = $target_dir . DIRECTORY_SEPARATOR  .  $basename  . "." . $extension;

    if (move_uploaded_file($_FILES['fileToUpload']['tmp_name'], $target_file)) { 
        $_SESSION['file_upload_success_message'] = "File Uploaded Successfully";
    } else {
        $_SESSION['file_upload_success_message'] = "There was an error while uploading your file";
        }

    // Redirect back to the same page
    header('Location: index.php');
    exit;
}


?>
<!DOCTYPE html>
<html>
<head>
    <title>Vulnerable web app</title>
</head>
<body>
    <h1>Welcome to Facebook</h1>

    <form action="index.php" method="POST" enctype="multipart/form-data">
        Select file to upload:
        <input type="file" name="fileToUpload" id="fileToUpload">
        <input type="submit" value="Upload File" name="submitFileUpload" id="submitFileUpload">
    </form>
        <?php
    if(isset($_SESSION['file_upload_success_message'])) {
        echo $_SESSION['file_upload_success_message'];
        unset($_SESSION['file_upload_success_message']); 
    }
    ?>
</body>
</html>
