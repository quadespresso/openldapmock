#!/bin/sh

VERBOSE=""
COUNT=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    -v|--verbose)
      VERBOSE="-v"
      shift
      ;;
    -c|--count)
      if [ -n "$2" ] && [ "$2" -eq "$2" ] 2>/dev/null; then
        COUNT="$2"
        shift 2
      else
        echo "Error: Argument for $1 must be an integer." >&2
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

echo "Creating LDIF based on environment variables..."
GEN_OUT=$(python /ldap/ldifgen.py)
echo "${GEN_OUT}"

echo "Initializing LDAP database from /ldap/init.ldif..."
rm -rf /var/lib/openldap/data/*
slapadd $VERBOSE -l /ldap/init.ldif

echo
echo "Replaying output of Python LDIF generator..."
echo "${GEN_OUT}"
echo

echo "Starting slapd..."
exec slapd -d 256
