import os
import random
import string
from faker import Faker

# Constants
NUM_USERS = int(os.getenv("COUNT", 100))
LDIF_FILE = "/ldap/init.ldif"

# Initialize Faker
fake = Faker()


def generate_usernames(num_users):
    """Generate a list of usernames based on the number of users."""
    width = len(str(num_users - 1))
    return [f"user{str(i).zfill(width)}" for i in range(num_users)]


# Generate a random alphanumeric string of length 8
random_string = "".join(random.choices(string.ascii_letters + string.digits, k=8))


def generate_ldif(num_users):
    """Generate dummy LDIF data."""

    usernames = generate_usernames(num_users)
    ldif_data = [
        """
dn: dc=my-domain,dc=com
objectClass: top
objectClass: dcObject
objectClass: organization
o: Example Organization
dc: my-domain

dn: ou=users,dc=my-domain,dc=com
objectClass: organizationalUnit
ou: users

dn: ou=groups,dc=my-domain,dc=com
objectClass: organizationalUnit
ou: groups
""".strip(),
    ]

    groups = ["Admin", "Finance", "IT"]
    group_count = len(groups)

    group_members = {group: [] for group in groups}

    for index, username in enumerate(usernames):
        group = groups[index % group_count]
        group_members[group].append(username)
        first_name = fake.first_name()
        last_name = fake.last_name()

        ldif_entry = f"""
# Unhashed password: {username}_{random_string}
dn: uid={username},ou=users,dc=my-domain,dc=com
objectClass: inetOrgPerson
uid: {username}
sn: {last_name}
givenName: {first_name}
cn: {first_name} {last_name}
mail: {username}@my-domain.com
telephoneNumber: {fake.phone_number()}
userPassword: {username}_{random_string}
"""
        ldif_data.append(ldif_entry.strip())

    for group, members in group_members.items():
        group_dn = f"cn={group},ou=groups,dc=my-domain,dc=com"
        unique_members = "\n".join(
            [f"member: uid={member},ou=users,dc=my-domain,dc=com" for member in members]
        )
        group_entry = f"""
dn: cn={group},ou=groups,dc=my-domain,dc=com
objectClass: top
objectClass: groupOfNames
cn: {group}
{unique_members}
""".strip()
        ldif_data.append(group_entry)

    return "\n\n".join(ldif_data)


if __name__ == "__main__":
    print(f"The password suffix for all users is: _{random_string}")
    ldif_content = generate_ldif(NUM_USERS)
    with open(LDIF_FILE, "w") as file:
        file.write(ldif_content)
