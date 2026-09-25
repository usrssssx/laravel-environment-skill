<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Установка приложения</title>
    <script src="https://api.bitrix24.tech/api/v1/"></script>
</head>
<body>
    <p>Завершаем установку приложения...</p>
    <script nonce="{{ $nonce }}">
        BX24.init(function () {
            BX24.installFinish();
        });
    </script>
</body>
</html>
