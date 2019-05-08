from enum import Enum

# Enums für Choice-Felder
GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
)

ROOM_CHOICES = (
    ('Bathroom', 'Bathroom'),
    ('Livingroom', 'Livingroom'),
    ('Bedroom', 'Bedroom'),
    ('Kitchen', 'Kitchen'),
    ('Office', 'Office'),
)

SENSOR_STATES = (
    ('0', 'Not Connected'),
    ('1', 'No Data'),
    ('2', 'Climate is good!'),
    ('3', 'Too cold!'),
    ('4', 'Too hot!'),
    ('5', 'Too humid!'),
    ('6', 'Too dry!'),
    ('7', 'Too dry and too hot!'),
    ('8', 'Too dry and too cold!'),
    ('9', 'Too humid and too hot!'),
    ('10', 'Too humid and too cold!'),
    ('11', 'Error'),
)
