from tortoise.validators import Validator
from tortoise.exceptions import ValidationError
from password_strength import PasswordPolicy
from email_validator import validate_email, EmailNotValidError


class PasswordValidator(Validator):
    def __init__(self):
        self.password_policy = PasswordPolicy.from_names(
            length=8,
            uppercase=1,
            numbers=1,
            special=1,
            nonletters=1,
        )

    def __call__(self, value: str):
        failed_tests = self.password_policy.test(value)

        if failed_tests:
            failure_types = {
                "Length": "8 characters",
                "Special": "special character",
                "Uppercase": "uppercase letter",
                "Numbers": "digit",
                "NonLetters": "non-letter character",
            }

            failure_message_parts = ["doesn't have"]

            for test in failed_tests:
                failure_type = str(test).split("(")[0]
                failure_message_parts.append(failure_types[failure_type])

            failure_message = ", ".join(failure_message_parts)

            raise ValidationError(failure_message)


class EmailValidator(Validator):
    def __call__(self, value: str):
        try:
            validate_email(value, check_deliverability=True)
        except EmailNotValidError as exc:
            raise ValidationError(f"email: {str(exc)}")
