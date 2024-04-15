from flask_login import UserMixin

class Section(UserMixin):

    def __init__(self,name="Empty",columns_number="Empty",rows_number="Empty",
                 general="Empty",available_seats="Empty")->None:
        self.name = name
        self.columns_number = columns_number
        self.rows_number = rows_number
        self.general = general
        self.available_seats = available_seats
    
    def contructor(self, id_section,available_seats,price)->None:
        self.id_section = id_section
        self.available_seats = available_seats
        self.price = price 