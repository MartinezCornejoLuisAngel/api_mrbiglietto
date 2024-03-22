from werkzeug.security import check_password_hash #generate_password_hash
from flask_login import UserMixin

class Artist(UserMixin):

    def __init__(self,artistName,artistDescription,
        artistGenre,artistUrl,artistTourName)->None:
        self.artistName  = artistName
        self.artistDescription = artistDescription
        self.artistGenre = artistGenre
        self. artistUrl = artistUrl
        self.artistTourName = artistTourName
