#!/bin/sh

echo "Creating LDIF based on environment variables..."
GEN_OUT=$(python /ldap/ldifgen.py)
echo "${GEN_OUT}"

echo "Initializing LDAP database from /ldap/init.ldif..."
rm -rf /var/lib/openldap/data/*
slapadd -l /ldap/init.ldif

echo
echo "Replaying output of Python LDIF generator..."
echo "${GEN_OUT}"
echo

echo "Starting slapd..."
exec slapd -d 256
