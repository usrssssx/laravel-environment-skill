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
      DB_CONNECTION: pgsql
      DB_HOST: 127.0.0.1
      DB_PORT: 5432
      DB_DATABASE: laravel_test
      DB_USERNAME: laravel
      DB_PASSWORD: laravel_test_password
      REDIS_HOST: 127.0.0.1
    steps:
      - uses: __CHECKOUT_ACTION__
      - uses: __SETUP_PHP_ACTION__
        with:
          php-version: '__PHP_VERSION__'
          extensions: bcmath, intl, mbstring, pcntl, pdo_pgsql, xml, zip
          coverage: none
      - uses: __SETUP_NODE_ACTION__
        with:
          node-version: '__NODE_VERSION__'
          cache: npm
      - name: Install and start PostgreSQL and Redis
        run: |
          sudo apt-get update
          sudo apt-get install -y postgresql postgresql-client redis-server
          sudo systemctl start postgresql
          sudo systemctl start redis-server
          sudo -u postgres psql -v ON_ERROR_STOP=1 -c "CREATE ROLE laravel LOGIN PASSWORD 'laravel_test_password'"
          sudo -u postgres createdb --owner=laravel laravel_test
          pg_isready -h 127.0.0.1 -p 5432
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
        run: sudo journalctl -u postgresql -u redis-server --no-pager -n 200
