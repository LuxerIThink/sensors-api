from argon2 import PasswordHasher
from fastapi.security import OAuth2PasswordBearer
from password_strength import PasswordPolicy

password_hasher = PasswordHasher()

password_checker = PasswordPolicy.from_names(
    length=8,
    uppercase=1,
    numbers=1,
    special=1,
    nonletters=1,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="actions/token")