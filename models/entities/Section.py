from flask_login import UserMixin

class Section(UserMixin):

    def __init__(self,name,columns_number,rows_number,
                 general,available_seats)->None:
        self.name = name
        self.columns_number = columns_number
        self.rows_number = rows_number
        self.general = general
        self.available_seats = available_seats
    
    def __init__(self, id_section,available_seats,price)->None:
        self.id_section = id_section
        self.available_seats = available_seats
        self.price = price 