# Bitrix24 browser gate

Use this gate for every newly scaffolded application. For an existing Laravel application, preserve its architecture and adapt the same security properties instead of overwriting files.

## Required behavior

- Configure the Bitrix24 application URL as `https://<application-host>/bitrix24/launch`, the installation URL as `https://<application-host>/bitrix24/install`, and the settings URL as `https://<application-host>/bitrix24/settings`.
- `GET /` and direct `GET` requests to all three Bitrix24 endpoints show the branded access screen with `Приложение доступно только внутри Битрикс24`, the bundled official `База Бизнеса` logo sourced from `bazabz.ru`, and `Вас приветствует команда База Бизнеса`.
- Bundle the logo locally at `public/brand/business-base-logo.png`; do not hotlink it. The current source asset is `https://bazabz.ru/_mirror_external/i.1.creatium.io/disk2/0d/09/e3/b4485a110a2df458268cb82526126adb71/logotip_baza_biznesa.png`.
- `POST /bitrix24/launch` accepts the launch payload sent by Bitrix24, validates `DOMAIN`, `AUTH_ID`, and `member_id`, and verifies the token server-side with `POST https://<DOMAIN>/rest/app.info.json`.
- `POST /bitrix24/install` accepts the same validated context, permits `app.info` with `INSTALLED: false`, and renders a nonce-protected page that calls `BX24.installFinish()` after the empty starter has completed its required setup. Never call `installFinish` before project-specific installation work succeeds.
- Never reference the bare `BX24` global immediately after a static SDK tag. Load an official SDK URL with an explicit `onload` handler, verify `window.BX24` and `window.BX24.init`, then call `window.BX24.installFinish()`. Provide the second official SDK hostname as a fallback and allow both hosts in CSP. If both fail, render a controlled retry message instead of raising `ReferenceError`.
- `POST /bitrix24/settings` uses the same installed-application verification as the launch URL.
- Create a short-lived server-side session only when `app.info` returns an application result with an ID, code, and installed state.
- Store only the verified portal hostname, application identifiers, member identifier, and session timestamps. Do not store the access or refresh token in the session.
- Render the empty application shell only for the verified, unexpired session and an iframe navigation. Opening `/` in a top-level browser tab must still show the denied screen even if that browser has a recent application session.

The authoritative method documentation is `https://apidocs.bitrix24.ru/api-reference/common/system/app-info.html`. Bitrix24 sends launch authorization data when opening an application inside its interface. Treat that data as credentials until the server validates it.

## Security requirements

1. Do not authorize from `Referer`, `Origin`, `Sec-Fetch-*`, iframe detection, JavaScript state, `DOMAIN`, or `member_id` alone. `Sec-Fetch-Dest: iframe` may enforce the presentation context only after server-side OAuth verification.
2. Exempt only `bitrix24/launch`, `bitrix24/install`, and `bitrix24/settings` from CSRF verification. Compensate with strict payload validation, a rate limit, server-side OAuth verification, and session ID rotation where a session is created.
3. Require HTTPS for the application and portal REST endpoint. Set `SESSION_SECURE_COOKIE=true`, `SESSION_HTTP_ONLY=true`, and `SESSION_SAME_SITE=none` on test and production because the application is embedded cross-site.
4. Prevent SSRF before calling a supplied portal hostname. Reject malformed hosts, explicit ports, localhost, IP literals, and hostnames resolving to private, loopback, link-local, or reserved addresses. Pin the validated public address for the outbound request and disable redirects. An administrator may explicitly allow a known boxed portal with `BITRIX24_ALLOWED_PORTAL_HOSTS`.
5. Use short connect and request timeouts. Return a generic denied screen for all validation and REST failures.
6. Never include OAuth tokens in URLs, logs, exceptions, redirects, flashed input, HTML, JavaScript, local storage, or Git-tracked files.
7. For an authorized response, set `Content-Security-Policy: frame-ancestors https://<verified-portal-host>`. For the denied screen, use `frame-ancestors 'none'`. Do not emit `X-Frame-Options: SAMEORIGIN` for the authorized application response.
8. Send `Cache-Control: no-store` for both screens.

## Starter installation

Copy the contents of `assets/starter/bitrix24-browser-gate/` into the same relative paths in a freshly created Laravel application and remove the `.tpl` suffix. Replace the fresh scaffold files only before business development begins.

For Laravel 11-13, use the supplied `bootstrap/app.php.tpl` to add the narrow CSRF exception. If the framework layout differs, apply the equivalent middleware configuration using the installed Laravel version's API.

Merge the selected storage `.env` template with these values:

```dotenv
SESSION_SECURE_COOKIE=true
SESSION_HTTP_ONLY=true
SESSION_SAME_SITE=none
BITRIX24_LAUNCH_SESSION_TTL=900
BITRIX24_LAUNCH_TIMEOUT=5
BITRIX24_ALLOWED_PORTAL_HOSTS=
```

Local plain-HTTP verification may temporarily use `SESSION_SECURE_COOKIE=false`; test and production must use HTTPS and `true`.

## Acceptance checks

- Direct `GET /` returns HTTP 200 and contains the exact denied message.
- Fake iframe or referrer headers do not grant access.
- Missing, invalid, and expired tokens do not create a session and receive HTTP 403 on launch POST.
- Direct requests to installation and settings URLs remain gated; a verified installation POST renders the `installFinish` page without exposing OAuth tokens.
- Run `scripts/verify_bitrix24_installer.sh <project-root>` before deployment. If it fails, replace the unsafe loader with the current starter implementation, rerun feature tests, and rerun the verifier before continuing.
- A mocked successful `app.info` response rotates the session and redirects to `/`.
- The authorized shell contains no credentials and uses the verified portal in `frame-ancestors`.
- A top-level request with an otherwise valid session still receives the denied screen.
- Expired or absent application sessions return to the denied screen.
- The CSRF exception contains only `bitrix24/launch`.
- Feature tests and the full project test suite pass.
