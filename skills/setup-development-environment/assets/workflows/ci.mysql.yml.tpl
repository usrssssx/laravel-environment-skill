name: CI

on:
  pull_request:
    branches: [main, test]
  push:
    branches: [main, test]
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    env:
      APP_ENV: testing
      DB_CONNECTION: mysql
      DB_HOST: 127.0.0.1
      DB_PORT: 3306
      DB_DATABASE: laravel_test
      DB_USERNAME: laravel
      DB_PASSWORD: laravel_test_password
      REDIS_HOST: 127.0.0.1
    steps:
      - uses: __CHECKOUT_ACTION__
      - uses: __SETUP_PHP_ACTION__
        with:
          php-version: '__PHP_VERSION__'
          extensions: bcmath, intl, mbstring, pcntl, pdo_mysql, xml, zip
          coverage: none
      - uses: __SETUP_NODE_ACTION__
        with:
          node-version: '__NODE_VERSION__'
          cache: npm
      - name: Install and start MySQL and Redis
        run: |
          sudo apt-get update
          sudo apt-get install -y mysql-server redis-server
          sudo systemctl start mysql
          sudo systemctl start redis-server
          mysql --user=root --password=root --execute="CREATE DATABASE laravel_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
          mysql --user=root --password=root --execute="CREATE USER 'laravel'@'127.0.0.1' IDENTIFIED BY 'laravel_test_password'"
          mysql --user=root --password=root --execute="GRANT ALL PRIVILEGES ON laravel_test.* TO 'laravel'@'127.0.0.1'"
          mysqladmin --host=127.0.0.1 --user=laravel --password=laravel_test_password ping
          redis-cli ping
      - name: Prepare environment
        run: cp .env.example .env
      - name: Install PHP dependencies
        run: composer install --no-interaction --prefer-dist
      - name: Generate application key
        run: php artisan key:generate
      - name: Run migrations
        run: php artisan migrate --force
      - name: Run backend tests
        run: php artisan test
      - name: Install frontend dependencies
        run: npm ci
      - name: Build frontend
        run: npm run build
      - name: Show logs on failure
        if: failure()
        run: sudo journalctl -u mysql -u redis-server --no-pager -n 200
