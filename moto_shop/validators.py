from django.core.exceptions import ValidationError

def validate_only_letters(value):
    if not value.isalpha():
        raise ValidationError("Acest câmp trebuie să conțină doar litere.")
