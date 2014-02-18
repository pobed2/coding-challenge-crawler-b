# -*- coding: UTF-8 -*-


class Stop:
    def __init__(self, name, location, latitude, longitude):
        self.name = unicode(name)
        self.location = unicode(location)
        self.lat = unicode(latitude)
        self.long = unicode(longitude)

    def __str__(self):
        return u"{} {} {} {}".format(self.name, self.location, self.lat, self.long).encode('utf-8', 'ignore')

    def to_dict(self):
        return dict(stop_name=self.name,
                    stop_location=self.location, lat=self.lat, long=self.long)


class Route:
    def __init__(self, origin, destination):
        self.origin = unicode(origin)
        self.destination = unicode(destination)

    def __str__(self):
        return u"{} {}".format(self.origin, self.destination).encode('utf-8', 'ignore')

    def to_dict(self):
        return dict(origin=self.origin, destination=self.destination)


class Departure:
    def __init__(self, origin, destination, departure_time, arrival_time, duration, price):
        self.origin = origin
        self.destination = destination
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.duration = duration
        self.price = price

    def __str__(self):
        return u"{} {} {} {} {} {}".format(self.origin, self.destination, self.departure_time, self.arrival_time,
                                           self.duration, self.price).encode('utf-8', 'ignore')

    def to_dict(self):
        return dict(origin=self.origin, destination=self.destination, departure_time=str(self.departure_time),
                    arrival_time=str(self.arrival_time), duration=self.duration, price=self.price)
