from flask_login import UserMixin

class Theater(UserMixin):

    def __init__(self,name,id_location,sections,theater_url)->None:
        self.name = name
        self.id_location = id_location
        self.sections = sections
        self.theater_url = theater_url
        