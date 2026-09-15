[Unit]
Description=Run Laravel scheduler every minute for __APP_NAME__

[Timer]
OnCalendar=*-*-* *:*:00
Persistent=true
Unit=__APP_SLUG__-scheduler.service

[Install]
WantedBy=timers.target
