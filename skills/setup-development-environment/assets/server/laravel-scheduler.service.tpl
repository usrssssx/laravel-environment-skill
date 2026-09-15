[Unit]
Description=Run Laravel scheduler for __APP_NAME__

[Service]
Type=oneshot
User=__DEPLOY_USER__
Group=www-data
WorkingDirectory=__DEPLOY_PATH__/current
ExecStart=/usr/bin/php artisan schedule:run
