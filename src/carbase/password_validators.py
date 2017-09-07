from django.core.exceptions import ValidationError


class SpecCharValidator():
    def __init__(self):
        self.spec = '''[]~!@#$%^"'&*()_\/+{}":;'''

    def validate(self, password, user=None):
        if not any(char.isdigit() for char in password):
            raise ValidationError('''Пароль должен содержать буквы цифры и спец символы []~!@#$%^"'&*()_\/+{}":;''')
        if not any(char.isalpha() for char in password):
            raise ValidationError('''Пароль должен содержать буквы цифры и спец символы []~!@#$%^"'&*()_\/+{}":;''')
        if not any(char in self.spec for char in password):
            raise ValidationError('''Пароль должен содержать буквы цифры и спец символы []~!@#$%^"'&*()_\/+{}":;''')

    def get_help_text(self):
        return '''Пароль должен содержать буквы цифры и спец символы []~!@#$%^"'&*()_\/+{}":;'''
