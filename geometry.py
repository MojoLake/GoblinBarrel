import numpy as np
import ifcopenshell
from math import sqrt
import multiprocessing
import numpy
import ifcopenshell
import ifcopenshell.util.placement
import ifcopenshell.util.element
import ifcopenshell.geom
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.api.context
import ifcopenshell.api.project
import ifcopenshell.api.geometry

from handle_file import beam_and_columns
from filter_functions import filter_furnishment, filter_low_volume_elements

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
            
            # print("mn: ", mn)
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
        return sqrt((self.x - another.x)**2 + (self.y - another.y)**2 + (self.z - another.z)**2)

    def greater_x(self, another):
        return self.x >= another.x
    
    def greater_y(self, another):
        return self.y >= another.y

    def greater_z(self, another):
        return self.z >= another.z




def remove_too_close_ones(vertices, distance_too_close):
    okays = []
    for i in range(len(vertices)):
        v = vertices[i]
        fail = False
        for u in okays:
            if u.distance_to(v) <= distance_too_close:
                fail = True
                break

        if not fail:
            okays.append(v)

    return okays


def find_vertices_close_to_others(beams, columns, distance=30, distance_too_close=3):
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

    vertices_to_highlight = []

    for element in elements:
        to_highlight = space.find_vertices_to_highlight(element, distance)
        vertices_to_highlight.extend(to_highlight)

        print("for this element amount of vertices to highlight:", len(to_highlight))

    return remove_too_close_ones(vertices_to_highlight, distance_too_close)

def mark_vertices(model, vertices_to_mark, output_file_name):

    building_storey = model.by_type("IfcBuildingStorey")[0]
    model3d = ifcopenshell.api.context.add_context(model, context_type="Model")
    body = ifcopenshell.api.context.add_context(model, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model3d)

    vertices = [[(0.,0.,2.5), (0.,.6,2.5), (.6,.6,2.5), (.6,0.,2.5), (.3,.3,0.)]]
    faces = [[(0,1,2,3), (0,4,1), (1,4,2), (2,4,3), (3,4,0)]]

    representation = ifcopenshell.api.geometry.add_mesh_representation(model, context=body, vertices=vertices, faces=faces)

    beams = model.by_type("IfcBeam")
    columns = model.by_type("IfcColumn")


    for vertice in vertices_to_mark:
        matrix = numpy.eye(4)
        matrix[:,3][0] = vertice.x
        matrix[:,3][1] = vertice.y
        matrix[:,3][2] = vertice.z


        element = ifcopenshell.api.root.create_entity(model, ifc_class="IfcElementAssembly", name="elias")
        ifcopenshell.api.run(
                "spatial.assign_container",
                model,
                    products=[element], relating_structure=building_storey,
                )
        ifcopenshell.api.geometry.edit_object_placement(model, product=element, matrix=matrix)
        ifcopenshell.api.geometry.assign_representation(model, product=element, representation=representation)

    model.write(output_file_name)


def main():
    print("Program starting...")
    file_path = "./data/WoodenOffice.ifc"

    print("Opening file...")
    model = ifcopenshell.open(file_path)

    print("Filtering furnishment away...")
    filter_furnishment(model)

    print("Filtering according to volume")
    filter_low_volume_elements(model, volume_threshold=0.01)
    
    print("Finding beams and columns")
    beams, columns = beam_and_columns(model)

    print("Detecting vertices to mark...")
    vertices_to_mark = set(find_vertices_close_to_others(beams, columns, 30, 3))

    output_file_name = "output.ifc"

    print("Marking vertices with pyramids...")
    mark_vertices(model, vertices_to_mark, output_file_name)



if __name__ == "__main__":
    main()
