from tortoise.validators import Validator
from tortoise.exceptions import ValidationError
from api.startup.security import password_checker


class PasswordValidator(Validator):

    def __call__(self, value: str):
        failed_tests = password_checker.test(value)

        if failed_tests:

            failed_tests_string = str(failed_tests)

            failure_message_parts = ["doesn't have"]

            if "Length" in failed_tests_string:
                failure_message_parts.append("8 characters")

            if "Special" in failed_tests_string:
                failure_message_parts.append("special character")

            if "Uppercase" in failed_tests_string:
                failure_message_parts.append("uppercase letter")

            if "Numbers" in failed_tests_string:
                failure_message_parts.append("digit")

            if "NonLetters" in failed_tests_string:
                failure_message_parts.append("non-letter character")

            failure_message = ", ".join(failure_message_parts)

            raise ValidationError(failure_message)
