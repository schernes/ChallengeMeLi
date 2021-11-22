from pydrive2.auth import GoogleAuth

gauth = GoogleAuth()

# Creates local webserver and auto handles authentication.
gauth.LocalWebserverAuth()
