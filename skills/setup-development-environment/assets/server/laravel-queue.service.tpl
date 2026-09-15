[Unit]
Description=Laravel queue worker for __APP_NAME__
After=network.target redis-server.service

[Service]
Type=simple
User=__DEPLOY_USER__
Group=www-data
WorkingDirectory=__DEPLOY_PATH__/current
ExecStart=/usr/bin/php artisan queue:work --sleep=3 --tries=3 --timeout=90
Restart=always
RestartSec=5
KillSignal=SIGTERM
TimeoutStopSec=3600

[Install]
WantedBy=multi-user.target
