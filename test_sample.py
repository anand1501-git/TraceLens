import math

def calculate_area(radius):
    return math.pi * radius * radius

class Circle:
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return calculate_area(self.radius)