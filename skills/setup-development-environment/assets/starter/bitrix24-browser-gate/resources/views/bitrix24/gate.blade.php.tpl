<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>База Бизнеса — приложение Битрикс24</title>
    <style>
        :root { color-scheme: light; font-family: Inter, Arial, system-ui, sans-serif; }
        * { box-sizing: border-box; }
        body { min-height: 100vh; margin: 0; color: #18222b; background: #ffffff; }
        body::before { content: ''; position: fixed; inset: 0 0 auto; height: 6px; background: #681b12; }
        main { width: min(100% - 40px, 680px); min-height: 100vh; margin: 0 auto; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 64px 0 48px; text-align: center; }
        .logo { width: 116px; height: 116px; display: block; margin-bottom: 32px; object-fit: cover; }
        .eyebrow { margin: 0 0 12px; color: #7d2a20; font-size: 13px; line-height: 1.4; font-weight: 700; text-transform: uppercase; }
        h1 { max-width: 620px; margin: 0; font-size: 48px; line-height: 1.12; font-weight: 720; letter-spacing: 0; }
        .instruction { max-width: 520px; margin: 20px 0 0; color: #596772; font-size: 18px; line-height: 1.6; }
        .signature { width: min(100%, 420px); margin-top: 44px; padding-top: 24px; border-top: 1px solid #dce5df; color: #596772; font-size: 14px; line-height: 1.5; }
        .signature strong { display: block; margin-top: 3px; color: #18222b; font-size: 18px; font-weight: 700; }
        @media (max-width: 480px) {
            main { width: min(100% - 32px, 680px); padding-top: 48px; }
            .logo { width: 96px; height: 96px; margin-bottom: 26px; }
            h1 { font-size: 34px; }
            .instruction { font-size: 16px; }
        }
    </style>
</head>
<body>
    <main>
        <img class="logo" src="/brand/business-base-logo.png" alt="Логотип База Бизнеса" width="116" height="116">
        <p class="eyebrow">Приложение для Битрикс24</p>
        <h1>Приложение доступно только внутри Битрикс24</h1>
        <p class="instruction">Откройте приложение из меню вашего портала Битрикс24.</p>
        <p class="signature">Вас приветствует команда<strong>База Бизнеса</strong></p>
    </main>
</body>
</html>
