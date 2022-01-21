<?php
function iconv_list_encodings() {
    return array_values(array_filter(preg_split('#//\n#', shell_exec('iconv -l'), -1, PREG_SPLIT_NO_EMPTY), function($s) {
        return !strstr($s, '/') && !strstr($s, "\n") && !strstr($s, ':') && strlen($s) <= 12;
    }));
}

$encodings = iconv_list_encodings();

foreach($encodings as $e) {
    if(strlen(iconv('UTF8', $e, '')) > 0) {
        echo $e . "\n";
        var_dump(bin2hex(iconv('UTF8', $e, '')));
    }
}
