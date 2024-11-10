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


def filter_furnishment(ifc_file):
    remove = []
    furnish = ifc_file.by_type("IfcFurnishingElement")

    for element in furnish:
        ifc_file.remove(element)




def main():
    
    print("Program starting...")
    file_path = "./Ifc2x3_Duplex_Architecture.ifc"
    model = ifcopenshell.open(file_path)
    print("File opened!")
    filter_furnishment(model)
    beams, columns = beam_and_columns(model)
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

    vertices_to_highlight = []

    for element in elements:
        # close = space.find_close_elements(element, 10) 
        # print("Amount close")
        # print(len(close))
        to_highlight = space.find_vertices_to_highlight(element, 30)
        vertices_to_highlight.extend(to_highlight)
        print("for this element amount of vertices to highlight:", len(to_highlight))

    print("Len of vertices_to_highlight before filtering:", len(vertices_to_highlight))
    okays = []
    for i in range(len(vertices_to_highlight)):
        v = vertices_to_highlight[i]
        fail = False
        for u in okays:
            if u.distance_to(v) <= 3:
                fail = True
                break

        if not fail:
            okays.append(v)

    vertices_to_highlight = set(okays)

    # for v in vertices_to_highlight:
    #     print(v.x, v.y, v.z)

    # We want our representation to be the 3D body of the element.
    # This representation context is only created once per project.
    # You must reuse the same body context every time you create a new representation.

    building_storey = model.by_type("IfcBuildingStorey")[0]
    model3d = ifcopenshell.api.context.add_context(model, context_type="Model")
    body = ifcopenshell.api.context.add_context(model,
    context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model3d)

# These vertices and faces represent a .2m square .5m high upside down pyramid in SI units.
# Note how they are nested lists. Each nested list represents a "mesh". There may be multiple meshes.
    vertices = [[(0.,0.,2.5), (0.,.6,2.5), (.6,.6,2.5), (.6,0.,2.5), (.3,.3,0.)]]
    # vertices = [[(0.,0.,1.5), (0.,.6,1.5), (.6,.6,1.5), (.6,0.,1.5), (0., 0., 0.), (0., .6, 0.), (.6, .6, 0.), (.6, 0., 0.)]]
    # faces = [[(0, 1, 2, 3), (4, 5, 6, 7), (0, 4, 7, 3), (1, 5, 4, 0), (2, 6, 5, 1), (3, 7, 6,2)]]
    faces = [[(0,1,2,3), (0,4,1), (1,4,2), (2,4,3), (3,4,0)]]
    representation = ifcopenshell.api.geometry.add_mesh_representation(model, context=body, vertices=vertices, faces=faces)

    beams = model.by_type("IfcBeam")
    columns = model.by_type("IfcColumn")


    print("Length of vertices to hightlight:", len(vertices_to_highlight))

    # Create a new IFC entity for each clash
    # Yoy'll need to have Blender python library (bpy) installed to run this part of the code
    for collision in vertices_to_highlight:
        matrix = numpy.eye(4)
        # matrix[:,3][0:3] = list(collision.p1)
        matrix[:,3][0] = collision.x
        matrix[:,3][1] = collision.y
        matrix[:,3][2] = collision.z


        element = ifcopenshell.api.root.create_entity(model, ifc_class="IfcElementAssembly", name="elias")
        ifcopenshell.api.run(
                "spatial.assign_container",
                model,
                    products=[element], relating_structure=building_storey,
                )
        ifcopenshell.api.geometry.edit_object_placement(model, product=element, matrix=matrix)
        ifcopenshell.api.geometry.assign_representation(model, product=element, representation=representation)

    # Save the new IFC file
    model.write("please_work.ifc")

    





if __name__ == "__main__":
    main()
