# Imgura Album

> Built with this framework: https://github.com/mikecao/flight

## Deployment guide

### With docker
```sh
docker-compose up --build
```
That's all.

### Without docker

0. Install PHP 8

1. Install composer & required packages
    
    Ref. https://getcomposer.org/download/
   ```sh
    curl -sS https://getcomposer.org/installer | php
    cd ./src && /path/to/composer.phar install
    ```

2. Run the server
    ```sh
    cd ./src/html && php -S localhost:8000
    ```
