from .const import *
from .models import *
from shapely.geometry import Polygon, Point


# Klasse welche das Klima überprüft.
class climate_observation_unit:
    # Der maximale und minmale Messbereich eines Sensors
    MAX_TEMP = 50;
    MIN_TEMP = -10;
    MAX_HUMIDITY = 100;
    MIN_HUMIDITY = 0;

    # Methode die das Klima eines Messwertepaares bewertet.
    # Parameter: Bekommt ein Messwertepaar und den Sensor übergeben.
    def check_climate(self, data, sensor):
        # Ermittelt den Raumtypen um die Optimalwerte zu erhalten.
        room = self.determine_room_type(sensor.roomType, sensor)

        # Der Punkt aus den beiden Messwerten.
        data_point = Point(data.get('temperature'), data.get('humidity'))

        # Alle Bereiche werden als Polygon erzeugt.
        optimal_area = self.points_polygon([room.p1, room.p2, room.p3, room.p4])

        too_hot_area = self.points_polygon([Point(room.p3.x, room.p4.y), room.p3, Point(self.MAX_TEMP, room.p3.y), Point(self.MAX_TEMP, room.p4.y)])

        too_cold_area = self.points_polygon([room.p1, Point(room.p1.x, room.p2.y), Point(self.MIN_TEMP, room.p2.y), Point(self.MIN_TEMP, room.p1.y)])

        too_humid_area = self.points_polygon([Point(room.p1.x, self.MAX_HUMIDITY), room.p1, room.p4, Point(room.p3.x, room.p4.y), Point(room.p3.x, self.MAX_HUMIDITY)])

        too_dry_area = self.points_polygon([Point(room.p1.x, room.p2.y), Point(room.p1.x, self.MIN_HUMIDITY), Point(room.p3.x, self.MIN_HUMIDITY), room.p3, room.p2])

        too_dry_cold_area = self.points_polygon([Point(room.p1.x, room.p2.y), room.p2, room.p1, Point(room.p1.x, room.p2.y), Point(self.MIN_TEMP, room.p2.y), Point(self.MIN_TEMP, self.MIN_HUMIDITY), Point(room.p1.x, self.MIN_HUMIDITY)])

        too_humid_hot_area = self.points_polygon([Point(room.p3.x, room.p4.y), room.p4, room.p3, Point(room.p3.x, room.p4.y), Point(self.MAX_TEMP, room.p4.y), Point(self.MAX_TEMP, self.MAX_HUMIDITY), Point(room.p3.x, self.MAX_HUMIDITY)])

        too_dry_hot_area = self.points_polygon([room.p3, Point(room.p3.x, self.MIN_HUMIDITY), Point(self.MAX_TEMP, self.MIN_HUMIDITY), Point(self.MAX_TEMP, room.p3.y)])

        too_humid_cold_area = self.points_polygon([room.p1, Point(room.p1.x, self.MAX_HUMIDITY), Point(self.MIN_TEMP, self.MAX_HUMIDITY), Point(self.MIN_TEMP, room.p1.y)])

        # Es wird überprüft in welchem Bereich sich der Punkt befindet.
        if optimal_area.contains(data_point):
            return '2'

        elif too_hot_area.contains(data_point):
            return '4'

        elif too_cold_area.contains(data_point):
            return '3'

        elif too_humid_area.contains(data_point):
            return '5'

        elif too_dry_area.contains(data_point):
            return '6'

        elif too_dry_cold_area.contains(data_point):
            return '8'

        elif too_humid_hot_area.contains(data_point):
            return '9'

        elif too_dry_hot_area.contains(data_point):
            return '7'

        elif too_humid_cold_area.contains(data_point):
            return '10'

        else:
            return '11'

    # Da Mit den Punkten nicht direkt ein Polygon erstellt werden kann müssen sie erst in eine Liste aus Koordinaten umgewadnelt werden
    def points_polygon(self, points_list):
        coords = sum(map(list, (p.coords for p in points_list)), [])
        poly = Polygon(coords)
        return poly

    # Ermittelt den Raumtypen und Returnt diesen als Objekt mit den Eckpunkten
    def determine_room_type(self, room_type, sensor):
        room = ""
        # Ermittelt welcher Raumtyp übergeben wurde
        if sensor.roomType == "Livingroom":
            room = Livingroom()

        elif sensor.roomType == "Bathroom":
            room = Bathroom()

        elif sensor.roomType == "Bedroom":
            room = Bedroom()

        elif sensor.roomType == "Office":
            room = Office()

        elif sensor.roomType == "Kitchen":
            room = Kitchen()

        return room
