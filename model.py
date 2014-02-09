# -*- coding: UTF-8 -*-

class Station:
    def __init__(self, name, location, latitude, longitutde):
        self.name = unicode(name)
        self.location = unicode(location)
        self.lat = unicode(latitude)
        self.long = unicode(longitutde)

    def __str__(self):
        return "{} {} {} {}".format(self.name , self.location , self.lat , self.long)

class Route:
    def __init__(self, origin, destination):
        self.origin = unicode(origin)
        self.destination = unicode(destination)

    def __str__(self):
        return "{} {}".format(self.origin, self.destination)

class Departure:
    def __init__(self, origin, destination, departure_time, arrival_time, duration, price):
        self.origin = origin
        self.destination = destination
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.duration = duration
        self.price = price

    def __str__(self):
        return "{} {} {} {} {} {}".format(self.origin ,self.destination,self.departure_time , self.arrival_time,self.duration, self.price)
