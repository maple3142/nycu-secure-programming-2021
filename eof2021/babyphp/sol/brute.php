<?php
require_once 'vendor/autoload.php';  // composer require php-ds/php-ds

// some *GOOD* encodings that may product what we wants
// mainly taken from https://gist.github.com/loknop/b27422d355ea1fd0d90d6dbc1e278d4d too
$encodings = [
    'UTF8',
    'UTF16LE',
    'ISO2022KR',
    'CSISO2022KR',
    'UCS2',
    'UTF16',
    'EUCTW',
    'MAC',
    'CP1256',
    'BIG5',
    'SHIFTJISX0213',
    '851',
    '852',
    '857',
    '1046',
    'TCVN',
    'ISO-IR-111',
    'SJIS',
    'UCS-2LE',
    'CP1133',
    'L1',
    'L2',
    'L3',
    'L4',
    'L5',
    'L6',
    'L7'
];

// BFS
$table = [];
$queue = new \Ds\Queue();
$queue->push(['abcdefg', []]);
$visited = new \Ds\Set();
$visited->add('abcdefg');
while (!$queue->isEmpty()) {
    [$cur, $path] = $queue->pop();
    // echo "visiting $cur\n";
    $visited->add($cur);
    $cleared = base64_encode(base64_decode($cur));
    if (substr($cleared, 1) === 'abcdefg' && !array_key_exists($cleared[0], $table)) {
        $newpath = array_merge($path, ['convert.base64-decode', 'convert.base64-encode']);
        var_dump($cleared);
        var_dump($newpath);
        echo "\n";
        $table[$cleared[0]] = $newpath;
        file_put_contents("table.json", json_encode($table));
    }
    if (count($path) > 4) {
        // max 4 degree
        continue;
    }
    $cnt = 0; // limit each node to have 100 neighbors at most
    for ($i = 0; $i < count($encodings) && $cnt < 100; $i++) {
        if (rand(0, 10) < 8) continue; // randomly drop some of them
        for ($j = 0; $j < count($encodings) && $cnt < 100; $j++) {
            if ($i === $j) continue;
            $in = $encodings[$i];
            $out = $encodings[$j];
            $t = @iconv($in, $out, $cur);
            if (strlen($t) === 0) continue;
            if ($visited->contains($t)) continue;
            $visited->add($t);
            $queue->push([$t, array_merge($path, ["convert.iconv.$in.$out"])]);

            $cnt++;
        }
    }
}

var_dump(array_keys($table));
file_put_contents("table.json", json_encode($table));
