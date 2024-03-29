from flask_login import UserMixin

class Event(UserMixin):

    def __init__(self,id_artist,id_theater,datetime,
        pricepersection)->None:
        self.id_artist = id_artist
        self.id_theater = id_theater
        self.datetime = datetime
        self.pricepersection = pricepersection