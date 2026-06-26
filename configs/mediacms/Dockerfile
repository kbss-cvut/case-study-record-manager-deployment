FROM mediacms/mediacms:7.2

ARG MEDIACMS_HOME=/home/mediacms.io/mediacms
ARG MEDIACMS_DOCKER_DIR=${MEDIACMS_HOME}/deploy/docker

COPY ./images/userlogos/ ${MEDIACMS_HOME}/media_files/userlogos/

COPY ./local_settings.py ${MEDIACMS_DOCKER_DIR}/
COPY ./media_access/ ${MEDIACMS_DOCKER_DIR}/
COPY ./auth/ ${MEDIACMS_DOCKER_DIR}/
COPY ./nginx.conf ${MEDIACMS_DOCKER_DIR}/nginx_http_only.conf