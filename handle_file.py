import ifcopenshell
import ifcopenshell.geom


def do_geometry(ifc_file):
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)


    walls = ifc_file.by_type("IfcWallStandardCase")

    wall = walls[0]

    wall_shape = ifcopenshell.geom.create_shape(settings, wall)

    vertices = wall_shape.geometry.verts
    edges = wall_shape.geometry.edges

    print("Vertices", vertices)
    print("Edges", edges)


def main():

    print("Program starting...")
    file_path = "./data/Ifc2x3_Duplex_Architecture.ifc"
    demo_file = ifcopenshell.open(file_path)
    walls = demo_file.by_type("IfcWallStandardCase")
    print("number of walls found:", len(walls))
    do_geometry(demo_file)



if __name__ == "__main__":
    main()
