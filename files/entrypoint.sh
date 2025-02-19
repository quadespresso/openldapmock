#!/bin/sh

VERBOSE=""
COUNT=""

while [ "$#" -gt 0 ]; do
  case "$1" in
  -h | --help)
    echo "Usage: docker run <image> [options]"
    echo
    echo "Options:"
    echo "  -v, --verbose   Enable verbose mode"
    echo "  -c, --count     Specify a positive integer for the count"
    echo "  -h, --help      Display this help message"
    exit 0
    ;;
  -v | --verbose)
    VERBOSE="-v"
    shift
    ;;
  -c | --count)
    if [ -n "$2" ] && [ "$2" -eq "$2" ] 2>/dev/null && [ "$2" -gt 0 ]; then
      COUNT="$2"
      shift 2
    else
      echo "Error: Argument for $1 must be a positive integer." >&2
      exit 1
    fi
    ;;
  *)
    echo "Unknown option: $1" >&2
    exit 1
    ;;
  esac
done

if [ -n "$COUNT" ]; then
  export COUNT
fi

echo "Creating LDIF based on the COUNT environment variable (default: 100)..."
GEN_OUT=$(python /ldap/ldifgen.py)
echo "${GEN_OUT}"

echo "Adding TLS to the config..."
cat /ldap/tls.conf >>/etc/openldap/slapd.conf

echo "Generating self-signed certificate (valid for 365 days)..."
openssl ecparam -name secp384r1 -out /ldap/ecparam.pem
openssl req -x509 -nodes -days 365 -newkey ec:/ldap/ecparam.pem \
  -keyout /ldap/ldaps.key -out /ldap/ldaps.crt -subj "/CN=localhost"

echo "Initializing LDAP database from /ldap/init.ldif..."
rm -rf /var/lib/openldap/data/*
slapadd $VERBOSE -l /ldap/init.ldif

# Repeat the output, in the event that the user specified -v as this makes for a chatty slapadd run.
# Saves the user from having to scroll up to see the output.
echo
echo "Replaying output of Python LDIF generator..."
echo "${GEN_OUT}"
echo

echo "Starting slapd..."
exec slapd -d 256 -h "ldap:/// ldaps:///"
