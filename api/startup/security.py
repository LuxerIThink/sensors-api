from argon2 import PasswordHasher
from password_strength import PasswordPolicy

password_hasher = PasswordHasher()

password_checker = PasswordPolicy.from_names(
        length=8,
        uppercase=1,
        numbers=1,
        special=1,
        nonletters=1,
)
