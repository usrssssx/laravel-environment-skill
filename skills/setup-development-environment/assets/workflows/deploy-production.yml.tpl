name: Deploy production

on:
  push:
    tags: ['v*']
  workflow_dispatch:
    inputs:
      revision:
        description: Commit SHA from main to release
        required: true

permissions:
  contents: read

concurrency:
  group: deploy-production
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    outputs:
      revision: ${{ steps.release.outputs.revision }}
    steps:
      - name: Resolve release revision
        id: release
        env:
          MANUAL_REVISION: ${{ inputs.revision }}
        run: |
          revision="${MANUAL_REVISION:-$GITHUB_SHA}"
          echo "revision=$revision" >> "$GITHUB_OUTPUT"
      - uses: __CHECKOUT_ACTION__
        with:
          ref: ${{ steps.release.outputs.revision }}
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
          REVISION: ${{ steps.release.outputs.revision }}
        run: ./scripts/package-release.sh "$REVISION" ".deploy/release-$REVISION.tar.gz"
      - uses: __UPLOAD_ARTIFACT_ACTION__
        with:
          name: release-${{ steps.release.outputs.revision }}
          path: |
            .deploy/release-${{ steps.release.outputs.revision }}.tar.gz
            .deploy/release-${{ steps.release.outputs.revision }}.tar.gz.sha256
          retention-days: 90

  verify-test:
    needs: build
    runs-on: ubuntu-latest
    timeout-minutes: 20
    environment: test
    steps:
      - uses: __CHECKOUT_ACTION__
        with:
          ref: ${{ needs.build.outputs.revision }}
      - uses: __DOWNLOAD_ARTIFACT_ACTION__
        with:
          name: release-${{ needs.build.outputs.revision }}
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
      - name: Deploy release candidate to test
        env:
          HOST: ${{ vars.DEPLOY_HOST }}
          PORT: ${{ vars.DEPLOY_PORT }}
          USER: ${{ vars.DEPLOY_USER }}
          PATH_ON_SERVER: ${{ vars.DEPLOY_PATH }}
          APP_URL: ${{ vars.APP_URL }}
          REVISION: ${{ needs.build.outputs.revision }}
        run: ./scripts/deploy-ci.sh test "$REVISION" ".deploy/release-$REVISION.tar.gz"
      - name: Verify release candidate
        env:
          APP_URL: ${{ vars.APP_URL }}
        run: curl --fail --show-error --silent --retry 5 "$APP_URL/health"

  deploy-production:
    needs: [build, verify-test]
    runs-on: ubuntu-latest
    timeout-minutes: 30
    environment: production
    steps:
      - uses: __CHECKOUT_ACTION__
        with:
          ref: ${{ needs.build.outputs.revision }}
      - uses: __DOWNLOAD_ARTIFACT_ACTION__
        with:
          name: release-${{ needs.build.outputs.revision }}
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
      - name: Deploy approved artifact
        env:
          HOST: ${{ vars.DEPLOY_HOST }}
          PORT: ${{ vars.DEPLOY_PORT }}
          USER: ${{ vars.DEPLOY_USER }}
          PATH_ON_SERVER: ${{ vars.DEPLOY_PATH }}
          APP_URL: ${{ vars.APP_URL }}
          REVISION: ${{ needs.build.outputs.revision }}
        run: ./scripts/deploy-ci.sh production "$REVISION" ".deploy/release-$REVISION.tar.gz"
      - name: External health check
        env:
          APP_URL: ${{ vars.APP_URL }}
        run: curl --fail --show-error --silent --retry 5 "$APP_URL/health"
