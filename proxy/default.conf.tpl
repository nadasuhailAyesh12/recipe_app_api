server{
    listen $(LISTEN_PORT);

    location /static {
        alias /vol/static;
    }

    location / {
    uwsgi_pass $(App_Host):$(APP_PORT);
    include /etc/nginx/wsgi_params;
    client_max_body_size 10M;
    }
}
