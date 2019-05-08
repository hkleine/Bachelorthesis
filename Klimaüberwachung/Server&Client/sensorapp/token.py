import secrets
# Klasse welche einen zufälligen Token erzeugt.
class Token():
    def createToken():
        return secrets.token_urlsafe(15)
