<?php

return [
    'launch_timeout' => (int) env('BITRIX24_LAUNCH_TIMEOUT', 5),
    'launch_session_ttl' => (int) env('BITRIX24_LAUNCH_SESSION_TTL', 900),
    'allowed_portal_hosts' => array_values(array_filter(array_map(
        static fn (string $host): string => strtolower(trim($host)),
        explode(',', (string) env('BITRIX24_ALLOWED_PORTAL_HOSTS', '')),
    ))),
];
