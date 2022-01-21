<?php
if (isset($_POST['filter'])) {
    $filter = $_POST['filter'];
    $result = file_get_contents("php://filter/$filter/resource=empty.txt");
    if ($result === 'gimme flag') {
        echo getenv('FLAG');
    } else {
        echo 'You got: ' . htmlspecialchars($result);
    }
} else {
    highlight_file(__FILE__);
}
?>
<form action="." method="POST">
    <textarea name="filter"></textarea>
    <button type="submit">Submit</button>
</form>
