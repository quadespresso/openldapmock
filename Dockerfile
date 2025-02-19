FROM python:3.12-alpine3.21

LABEL org.opencontainers.image.authors="Jim Carroll <pcarroll@mirantis.com>"

RUN apk add --no-cache busybox musl libldap libltdl libsasl \
  libuuid openldap openldap-clients openldap-back-mdb openssl \
  && pip3 install --no-cache-dir faker

COPY files /ldap
RUN mv /ldap/entrypoint.sh / && chmod +x /entrypoint.sh

EXPOSE 389 636

ENTRYPOINT ["/entrypoint.sh"]
