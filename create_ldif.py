import random
from faker import Faker

# Constants
NUM_USERS = 50

# Initialize Faker
fake = Faker()

def generate_usernames(num_users):
    """Generate a list of usernames based on the number of users."""
    width = len(str(num_users))
    return [f"user{str(i).zfill(width)}" for i in range(1, num_users + 1)]

def generate_ldif(num_users):
    """Generate dummy LDIF data."""
    usernames = generate_usernames(num_users)
    ldif_data = [
        """
dn: dc=example,dc=com
objectClass: top
objectClass: dcObject
objectClass: organization
o: Example Organization
dc: example
""".strip()
    ]

    group_entries = [
        """
dn: cn=Admin,ou=groups,dc=example,dc=com
objectClass: top
objectClass: posixGroup
cn: Admin
gidNumber: 1001
""",
        """
dn: cn=Finance,ou=groups,dc=example,dc=com
objectClass: top
objectClass: posixGroup
cn: Finance
gidNumber: 1002
""",
        """
dn: cn=IT,ou=groups,dc=example,dc=com
objectClass: top
objectClass: posixGroup
cn: IT
gidNumber: 1003
"""
    ]

    ldif_data.extend(group_entries)
        first_name = fake.first_name()
        last_name = fake.last_name()
        ldif_entry = f"""
dn: uid={username},ou=users,dc=example,dc=com
objectClass: inetOrgPerson
uid: {username}
sn: {last_name}
givenName: {first_name}
cn: {first_name} {last_name}
mail: {username}@example.com
"""
        ldif_data.append(ldif_entry.strip())

    return "\n\n".join(ldif_data)

if __name__ == "__main__":
    ldif_content = generate_ldif(NUM_USERS)
    with open("bootstrap.ldif", "w") as file:
        file.write(ldif_content)
