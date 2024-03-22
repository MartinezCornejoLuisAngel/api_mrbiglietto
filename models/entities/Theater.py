from flask_login import UserMixin

class Theater(UserMixin):

    def __init__(self,name,id_location,sections)->None:
        self.name = name
        self.id_location = id_location
        self.sections = sections
        