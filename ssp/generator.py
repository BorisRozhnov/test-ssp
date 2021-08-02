import random
import string


class Generator():
    lowcase = 'abcdefghikmnprstuvwxyz'
    upcase = 'ABCDEFGHKLMNPRSTUVWXYZ'
    digits = '23456789'
    special = '!%$#'
    def get_random_alphanumeric_string(self, length):
        letters_and_digits = string.ascii_letters + string.digits
        result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
        return result_str

    @staticmethod
    def get_random_characters(length, characters):
        result_str = ''.join((random.choice(characters) for i in range(length)))
        return result_str

    def get_password(self, length=8):
        # list of characters and number of char in password
        char_low_number = length - 4 if length >= 8 else 4
        password = self.get_random_characters(char_low_number, self.lowcase)
        password += self.get_random_characters(1, self.upcase)
        password += self.get_random_characters(2, self.digits)
        password += self.get_random_characters(1, self.special)
        password_list = list(password)
        random.SystemRandom().shuffle(password_list)
        password = ''.join(password_list)
        return password