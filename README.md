# Minimal Python-based OpenLDAP server for Docker

## Overview

The design goal is to provide an easy-to-use container image that can provide a lightweight LDAP
server for testing purposes. At minimum, this image should provide a nominal number of users and
groups, with the ability to add more as needed.

For those who are more interested in bulking up the number of users in order to test how well their
LDAP client scales, this image will be able to generate a large number of users with minimal
effort.

The container image this repo encompasses will, when ran, do the following:

1. generate a password stub (valid only for the duration of the container)
1. generate a number of test users (default 100, if no count specified)
1. for each username, the password is the username + `_` + the password stub generated earlier
   eg, for the username `user42` and password stub `abc123`, the password would be `user42_abc123`
1. assign each username to one of the curated groups on a round-robin basis
1. start an OpenLDAP server with the generated users, listening on port 389

### Note

Please note the following:

#### Username numeric suffix length varies with user count

Please note the following username generation rules:

- if the count is <= 10, the usernames will range from `user0` to `user9`
- if the count is <= 100, the usernames will range from `user00` to `user09`
- if the count is <= 1000, the usernames will range from `user000` to `user999`

and so on.

#### Group names are fixed

With regards to the groups, there are only 3 at this time:

- `Admin`
- `IT`
- `Finance`

which in general could be used/mapped onto the following RBAC roles:

- full admin (no restrictions)
- limited admin (some restrictions)
- read-only (no write access)

#### Container start time scales with user count

Be advised that as the number of users increases, the time it takes to generate the users will scale
accordingly, at runtime. For example:

- 200 users -> 3s
- 2,000 users -> 14s
- 20,000 users -> 2m 40s

#### Password stub is unique per container

Note that for security reasons, the password stub will be unique with each container invocation.
Once the container is terminated, the password stub will be lost.

You can find the ephemeral password stub in the container logs.

## Usage

To build the image:

```bash
docker build -t <name:tag> .
```

To run the image:

```bash
docker run -d -p 389:389 <name:tag> [options]
```

where `[options]` can be one or more of the following:

- `-c <count>` - number of users to generate (default: 100)
- `-v` - verbose output

Alternatively, try the following image:

```bash
docker pull quaddo/openldapmock:latest
```

and then run it as needed.

When in doubt, run it with `-h`/`--help` to see the available options:

```bash
❯ docker run -it --rm -p 389:389 --name slapd quaddo/openldapmock:latest -h
Usage: docker run <image> [options]

Options:
  -v, --verbose   Enable verbose mode
  -c, --count     Specify a positive integer for the count
  -h, --help      Display this help message
```

### Examples

Run the container with no options:

```bash
docker run -it --rm -p 389:389 --name slapd quaddo/openldapmock:latest
```

Example output from the above command:

```bash
❯ docker run -it --rm -p 389:389 --name slapd quaddo/openldapmock:latest
Unable to find image 'quaddo/openldapmock:latest' locally
latest: Pulling from quaddo/openldapmock
Digest: sha256:5e02de850e7de106e87d69a269e6530fdd2390ccabc383f44c5789a20b5ec433
Status: Downloaded newer image for quaddo/openldapmock:latest
Creating LDIF based on the COUNT environment variable (default: 100)...
The password suffix for all 100 generated users is: _m8R6A0Z8
So for example, user 'user42' would have the password 'user42_m8R6A0Z8'
Initializing LDAP database from /ldap/init.ldif...
Appending TLS config...
Closing DB...

Replaying output of Python LDIF generator...
The password suffix for all 100 generated users is: _m8R6A0Z8
So for example, user 'user42' would have the password 'user42_m8R6A0Z8'

Starting slapd...
67b3d0a8.39822688 0x7f6948789b28 @(#) $OpenLDAP: slapd 2.6.8 (Sep 25 2024 06:46:47) $
        openldap
67b3d0a9.11993878 0x7f6948789b28 slapd starting
```

Run the container with additional verbosity:

```bash
docker run -it --rm -p 389:389 --name slapd quaddo/openldapmock:latest -v
```

Run the container, specifying 200 users:

```bash
docker run -it --rm -p 389:389 --name slapd quaddo/openldapmock:latest -c 200
```

## Client configuration

### MKE4 configuration

Using the MKE4 reference example [listed here](https://docs.mirantis.com/mke-docs/docs/configuration/authentication/ldap/),
the following configuration block has been tested and known to work. Shared here, as reference examples
are always nice to have. Other than the host IP, everything else in this example should be usable
as-is:

```yaml
spec: # line included for context
  authentication:
    ldap:
      enabled: true
      host: <IP of LDAP server>:389 # change me
      insecureNoSSL: true
      bindDN: cn=Manager,dc=my-domain,dc=com
      bindPW: secret
      usernamePrompt: Email Address
      userSearch:
        baseDN: ou=users,dc=my-domain,dc=com
        filter: "(objectClass=person)"
        username: uid
        idAttr: DN
        emailAttr: mail
        nameAttr: cn
```

### MKE3 configuration

TBD

## Supplemental

By default, the slapd configuration is located at: `/etc/openldap/slapd.conf`.

Some notable configuration values are as follows:

```conf
include       /etc/openldap/schema/core.schema
pidfile       /var/run/openldap/slapd.pid
argsfile      /var/run/openldap/slapd.args
database      mdb
maxsize       1073741824
suffix        "dc=my-domain,dc=com"
rootdn        "cn=Manager,dc=my-domain,dc=com"
rootpw        secret
index         objectClass  eq
```

If necessary, you may add new entities using the following:

```bash
ldapadd -x -c -H ldap://localhost -D "cn=Manager,dc=my-domain,dc=com" -w secret -f <new_file.ldif>
```

Note the admin password specified above.

To verify, you can use the following:

```bash
ldapsearch -H ldap://localhost -D "cn=Manager,dc=my-domain,dc=com" -w secret -b dc=my-domain,dc=com
```
