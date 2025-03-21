class plane():
    __name = ""
    __person = 0
    
    def __init__(self,name,person):
        self.__name = "A380"
        self.__person = 800
        
    def set_name(self,name):
        self.__name = name
        
    def set_person(self,person):
        self.__person = person

    def get_name(self):
        return self.__name
        
    def get_person(self):
        return self.__person
     
     
class PlaneTest():
   plane1 = plane("A320",200)
   plane2 = plane("A330",300)
   plane3 = plane("A340",400)
   plane1.set_name("A350")
   plane1.set_person(500)
   print(plane1.get_name())
   print(plane1.get_person())
   print(plane2.get_name())
   print(plane2.get_person())
   print(plane3.get_name())
   print(plane3.get_person())   