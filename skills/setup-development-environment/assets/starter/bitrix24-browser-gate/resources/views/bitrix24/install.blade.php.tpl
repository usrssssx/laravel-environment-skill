<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Установка приложения</title>
</head>
<body>
    <p id="installation-status">Завершаем установку приложения...</p>
    <script nonce="{{ $nonce }}">
        (function () {
            const status = document.getElementById('installation-status');
            const sdkUrls = [
                'https://api.bitrix24.com/api/v1/',
                'https://api.bitrix24.tech/api/v1/',
            ];

            function fail() {
                status.textContent = 'Не удалось загрузить SDK Битрикс24. Обновите страницу установки.';
            }

            function finish() {
                if (!window.BX24 || typeof window.BX24.init !== 'function') {
                    fail();
                    return;
                }

                window.BX24.init(function () {
                    window.BX24.installFinish();
                });
            }

            function loadSdk(index) {
                if (index >= sdkUrls.length) {
                    fail();
                    return;
                }

                const script = document.createElement('script');
                script.src = sdkUrls[index];
                script.onload = finish;
                script.onerror = function () {
                    loadSdk(index + 1);
                };
                document.head.appendChild(script);
            }

            loadSdk(0);
        })();
    </script>
</body>
</html>
