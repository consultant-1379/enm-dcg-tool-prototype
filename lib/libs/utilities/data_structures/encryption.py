import base64


class Encryption():
    ascii = 'ascii'

    @staticmethod
    def encrypt(plain_text):
        binary_str = plain_text.encode(Encryption.ascii)

        b64_encoded = base64.urlsafe_b64encode(binary_str)
        encrypted = str(b64_encoded.decode(Encryption.ascii))
        return encrypted

    @staticmethod
    def decrypt(encrypted):
        b64_encoded = encrypted.encode(Encryption.ascii)
        b64_decoded = base64.urlsafe_b64decode(b64_encoded)
        decrypted = str(b64_decoded.decode(Encryption.ascii))
        return decrypted
