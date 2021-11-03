<?php
if (!file_exists($_FILES['image_file']['tmp_name']) || !is_uploaded_file($_FILES['image_file']['tmp_name'])) {
    die('Gimme file!');
}

$filename = basename($_FILES['image_file']['name']);
$extension = strtolower(explode(".", $filename)[1]);

if (!in_array($extension, ['png', 'jpeg', 'jpg']) !== false) {
    die("Invalid file extension: $extension.");
}

if ($_FILES['image_file']['size'] > 256000) {
    die('File size is too large.');
}

// check file type
$finfo = finfo_open(FILEINFO_MIME_TYPE);
$type = finfo_file($finfo, $_FILES['image_file']['tmp_name']);
finfo_close($finfo);
if (!in_array($type, ['image/png', 'image/jpeg'])) {
    die('Not an valid image.');
}

// check file width/height
$size = getimagesize($_FILES['image_file']['tmp_name']);
if ($size[0] > 512 || $size[1] > 512) {
    die('Uploaded image is too large.');
}


$content = file_get_contents($_FILES['image_file']['tmp_name']);
if (stripos($content, "<?php") !== false) {
    die("Hacker?");
}

$prefix = bin2hex(random_bytes(4));
move_uploaded_file($_FILES['image_file']['tmp_name'], "images/${prefix}_${filename}");
header("Location: images/${prefix}_${filename}");

