FROM mediacms/mediacms:7.2

COPY ./images/userlogos /home/mediacms.io/mediacms/media_files/userlogos
COPY ./local_settings.py /home/mediacms.io/mediacms/deploy/docker/local_settings.py
COPY ./protected_media.py /home/mediacms.io/mediacms/deploy/docker/protected_media.py
COPY ./by_md5.py /home/mediacms.io/mediacms/deploy/docker/by_md5.py
COPY ./by_id.py /home/mediacms.io/mediacms/deploy/docker/by_id.py
COPY ./nginx.conf /home/mediacms.io/mediacms/deploy/docker/nginx_http_only.conf
COPY ./oidc_adapter.py /home/mediacms.io/mediacms/deploy/docker/oidc_adapter.py
COPY ./dev_auth.py /home/mediacms.io/mediacms/deploy/docker/dev_auth.py