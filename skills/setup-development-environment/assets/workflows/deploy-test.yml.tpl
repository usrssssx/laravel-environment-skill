name: Deploy test

on:
  push:
    branches: [test]

permissions:
  contents: read

concurrency:
  group: deploy-test
  cancel-in-progress: false

jobs:
  test:
    uses: ./.github/workflows/ci.yml

  build:
    needs: test
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: __CHECKOUT_ACTION__
        with:
          ref: ${{ github.sha }}
      - uses: __SETUP_PHP_ACTION__
        with:
          php-version: '__PHP_VERSION__'
          extensions: bcmath, intl, mbstring, pcntl, pdo_mysql, xml, zip
          coverage: none
      - uses: __SETUP_NODE_ACTION__
        with:
          node-version: '__NODE_VERSION__'
          cache: npm
      - name: Build release contents
        run: |
          cp .env.example .env
          composer install --no-dev --no-interaction --prefer-dist --optimize-autoloader
          npm ci
          npm run build
      - name: Package immutable release
        env:
          REVISION: ${{ github.sha }}
        run: ./scripts/package-release.sh "$REVISION" ".deploy/release-$REVISION.tar.gz"
      - uses: __UPLOAD_ARTIFACT_ACTION__
        with:
          name: release-${{ github.sha }}
          path: |
            .deploy/release-${{ github.sha }}.tar.gz
            .deploy/release-${{ github.sha }}.tar.gz.sha256
          retention-days: 30

  deploy:
    needs: build
    runs-on: ubuntu-latest
    timeout-minutes: 20
    environment: test
    steps:
      - uses: __CHECKOUT_ACTION__
        with:
          ref: ${{ github.sha }}
      - uses: __DOWNLOAD_ARTIFACT_ACTION__
        with:
          name: release-${{ github.sha }}
          path: .deploy
      - name: Configure SSH
        env:
          SSH_KEY: ${{ secrets.DEPLOY_SSH_KEY }}
          KNOWN_HOSTS: ${{ secrets.DEPLOY_KNOWN_HOSTS }}
        run: |
          install -m 700 -d ~/.ssh
          printf '%s\n' "$SSH_KEY" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key
          printf '%s\n' "$KNOWN_HOSTS" > ~/.ssh/known_hosts
      - name: Deploy exact artifact
        env:
          HOST: ${{ vars.DEPLOY_HOST }}
          PORT: ${{ vars.DEPLOY_PORT }}
          USER: ${{ vars.DEPLOY_USER }}
          PATH_ON_SERVER: ${{ vars.DEPLOY_PATH }}
          APP_URL: ${{ vars.APP_URL }}
          REVISION: ${{ github.sha }}
        run: ./scripts/deploy-ci.sh test "$REVISION" ".deploy/release-$REVISION.tar.gz"
      - name: External health check
        env:
          APP_URL: ${{ vars.APP_URL }}
        run: curl --fail --show-error --silent --retry 5 "$APP_URL/health"
