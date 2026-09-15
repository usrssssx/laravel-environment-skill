server {
    listen 80;
    server_name __SERVER_NAME__;
    root __DEPLOY_PATH__/current/public;
    index index.php;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location = /health {
        access_log off;
        try_files $uri /index.php?$query_string;
    }

    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php__PHP_FPM_VERSION__-fpm.sock;
        fastcgi_read_timeout 60s;
    }

    location ~ /\. {
        deny all;
    }
}
