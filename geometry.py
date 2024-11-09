import numpy as np

class GeometricSpace(elements: List[Element]):
    self.elements = elements


class Element(id, vertices: List[Vertice]):
    self.id = id
    self.vertices = vertices
    assert(len(self.vertices) > 1) # should be more than 3 tbh

class Vertice(x: float, y: float, z: float):
    self.x, self.y, self.z = x, y, z

    def distance_to(another: Vertice):
        return sqrt((self.x + another.x)**2 + (self.y + another.y)**2 + (self.z + another.z)**2)

    def greater_x(another: Vertice):
        return self.x >= another.x
    
    def greater_y(another: Vertice):
        return self.y >= another.y

    def greater_z(another: Vertice):
        return self.z >= another.z




def main():
    
    beams, columns = find_beams_and_columns


    for id, vertices in beams:
        print(id, vertices)
        print(vertices)

    





if __name__ == "__main__":
    main()
