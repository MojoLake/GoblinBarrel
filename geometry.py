import numpy as np
import ifcopenshell
from math import sqrt
from handle_file import beam_and_columns

class GeometricSpace:
    def __init__(self, elements):
        self.elements = elements

    def find_close_elements(self, element, min_dist=1):
        ret = []

        for another in self.elements:
            if another.id == element.id:
                continue # don't compare to itself
            if element.find_min_vertice_dis(another) <= min_dist:
                ret.append(another)
        
        return ret

    def find_vertices_to_highlight(self, element, min_dist=10):
        ret = [] 

        for vertice in element.vertices:
            mn = 1e9 # big
            for another in self.elements:
                if another.id == element.id:
                    continue
                mn = min(mn, another.find_specific_min_vertice_dis(vertice))
            
            print("mn: ", mn)
            if mn <= min_dist:
                ret.append(vertice)

        return ret



class Element:
    def __init__(self, id, vertices):
        self.id = id
        self.vertices = vertices
        assert(len(self.vertices) > 1) # should be more than 3 tbh

    def find_specific_min_vertice_dis(self, vertice):
        mn = 1e9 # big
        for v in self.vertices:
            mn = min(mn, v.distance_to(vertice))
        return mn

    def find_min_vertice_dis(self, another):
        mn = 1e9 # big
        for v in self.vertices:
            mn = min(mn, another.find_specific_min_vertice_dis(v))
        return mn


class Vertice:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def distance_to(self, another):
        return sqrt((self.x + another.x)**2 + (self.y + another.y)**2 + (self.z + another.z)**2)

    def greater_x(self, another):
        return self.x >= another.x
    
    def greater_y(self, another):
        return self.y >= another.y

    def greater_z(self, another):
        return self.z >= another.z




def main():
    
    print("Program starting...")
    file_path = "./data/test.ifc"
    ifc_file = ifcopenshell.open(file_path)
    print("File opened!")
    beams, columns = beam_and_columns(ifc_file)
    print("found beams and columns")
    print("Length of beams:", len(beams))
    print("Length of columns:", len(columns))

    elements = []


    for id, vertices in beams.items():
        vers = []
        for x, y, z in vertices:
            vers.append(Vertice(x, y, z))
        elements.append(Element(id, vers))

    for id, vertices in columns.items():
        vers = []
        for x, y, z in vertices:
            vers.append(Vertice(x, y, z))
        elements.append(Element(id, vers))

    space = GeometricSpace(elements)


    close_ones = set()
    for element in elements:
        # close = space.find_close_elements(element, 10) 
        # print("Amount close")
        # print(len(close))
        to_highlight = space.find_vertices_to_highlight(element, 30)
        print("for this element amount of vertices to highlight:", len(to_highlight))

         

    





if __name__ == "__main__":
    main()
