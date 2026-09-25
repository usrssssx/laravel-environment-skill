#!/usr/bin/env bash
set -euo pipefail

project_root="${1:-.}"
view="$project_root/resources/views/bitrix24/install.blade.php"
controller="$project_root/app/Http/Controllers/Bitrix24AppController.php"

fail() {
  echo "ERROR: $1" >&2
  exit 1
}

[[ -f "$view" ]] || fail "Bitrix24 installation view is missing: $view"
[[ -f "$controller" ]] || fail "Bitrix24 controller is missing: $controller"

grep -Fq "script.onload" "$view" \
  || fail "installer does not wait for the Bitrix24 SDK load event"
grep -Fq "window.BX24" "$view" \
  || fail "installer does not guard access to window.BX24"
grep -Fq "typeof window.BX24.init" "$view" \
  || fail "installer does not verify that BX24.init is available"
grep -Fq "https://api.bitrix24.com/api/v1/" "$view" \
  || fail "primary Bitrix24 SDK URL is missing"
grep -Fq "https://api.bitrix24.tech/api/v1/" "$view" \
  || fail "fallback Bitrix24 SDK URL is missing"

if grep -Eq '(^|[[:space:](;])BX24\.(init|installFinish)[[:space:]]*\(' "$view"; then
  fail "installer calls BX24 directly before proving that the SDK loaded"
fi

grep -Fq "https://api.bitrix24.com" "$controller" \
  || fail "Content-Security-Policy does not allow the primary Bitrix24 SDK host"
grep -Fq "https://api.bitrix24.tech" "$controller" \
  || fail "Content-Security-Policy does not allow the fallback Bitrix24 SDK host"

command -v curl >/dev/null 2>&1 || fail "curl is required to verify the Bitrix24 SDK"

sdk_ok=false
temporary_file="$(mktemp)"
trap 'rm -f "$temporary_file"' EXIT

for sdk_url in \
  "https://api.bitrix24.com/api/v1/" \
  "https://api.bitrix24.tech/api/v1/"; do
  if curl --fail --silent --show-error --location --max-time 15 "$sdk_url" -o "$temporary_file" \
    && grep -Fq "window.BX24" "$temporary_file"; then
    sdk_ok=true
    break
  fi
done

[[ "$sdk_ok" == true ]] || fail "official Bitrix24 SDK endpoints did not provide window.BX24"

echo "Bitrix24 installer SDK check passed."
