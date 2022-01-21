<?php

// autoload_static.php @generated by Composer

namespace Composer\Autoload;

class ComposerStaticInit1529533344b849240b7770723c436585
{
    public static $prefixLengthsPsr4 = array (
        'D' => 
        array (
            'Ds\\' => 3,
        ),
    );

    public static $prefixDirsPsr4 = array (
        'Ds\\' => 
        array (
            0 => __DIR__ . '/..' . '/php-ds/php-ds/src',
        ),
    );

    public static $classMap = array (
        'Composer\\InstalledVersions' => __DIR__ . '/..' . '/composer/InstalledVersions.php',
    );

    public static function getInitializer(ClassLoader $loader)
    {
        return \Closure::bind(function () use ($loader) {
            $loader->prefixLengthsPsr4 = ComposerStaticInit1529533344b849240b7770723c436585::$prefixLengthsPsr4;
            $loader->prefixDirsPsr4 = ComposerStaticInit1529533344b849240b7770723c436585::$prefixDirsPsr4;
            $loader->classMap = ComposerStaticInit1529533344b849240b7770723c436585::$classMap;

        }, null, ClassLoader::class);
    }
}
