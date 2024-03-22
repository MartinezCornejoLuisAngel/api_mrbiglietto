from werkzeug.security import check_password_hash #generate_password_hash
from flask_login import UserMixin

class Location(UserMixin):

    def __init__(self,id,country,state,
        city,colony,postal_code,address)->None:
        self.id = id
        self.country = country
        self.state = state
        self.city = city
        self.colony = colony
        self.postal_code = postal_code
        self.address = address