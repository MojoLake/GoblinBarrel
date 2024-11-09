import ifcopenshell
import ifcopenshell.geom
import numpy as np

file_path = "./data/test.ifc"
output_path = "./data/output.ifc"

def get_bounding_box(element, settings):
    shape = ifcopenshell.geom.create_shape(settings, element)
    vertices = np.array(shape.geometry.verts).reshape(-1, 3)

    min_coords = vertices.min(axis=0)
    max_coords = vertices.max(axis=0)

    length, width, height = max_coords - min_coords
    return length, width, height

def get_dimensions(elements):
    element_ids = []
    dimensions = []

    for element in elements:
        try:
            # length, width, height = get_bounding_box(element, settings)
            element_ids.append(element)
            dimensions.append([get_bounding_box(element, settings)])

        except Exception as e:
            print(f"Skipping element {element.GlobalId} due to error:", e)
            
    dimensions = np.array(dimensions)
    print(f"Number of element id's: {len(element_ids)}")
    print(f"Number of dimensions", {len(dimensions)})
    assert(len(element_ids) == len(dimensions))
    return zip(element_ids, dimensions)


def filter_based_on_size(ifc_file, dimension_bounds=(1, 1, 1)):
    elements = ifc_file.by_type("IfcElement")
    print("Total elements found:", len(elements))

    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)

    res = get_dimensions(elements)

    for element_id, dimension in res:
        print(element_id, dimension)


    



def main():

    print("Program starting...")
    demo_file = ifcopenshell.open(file_path)
    filter_based_on_size(demo_file)

    return
    # Find all columns in the IFC file
    columns = demo_file.by_type("IfcColumn")
    print("Number of columns found:", len(columns))

    # Create a red color (RGB values range from 0.0 to 1.0)
    red_color = demo_file.createIfcColourRgb(None, 1.0, 0.0, 0.0)

    # Create a surface style rendering with the red color
    red_rendering = demo_file.createIfcSurfaceStyleRendering(
        SurfaceColour=red_color,
        Transparency=None,
        DiffuseColour=None,
        TransmissionColour=None,
        DiffuseTransmissionColour=None,
        ReflectionColour=None,
        SpecularColour=None,
        ReflectanceMethod='FLAT'  # You can use 'FLAT' or 'SURFACE_COLOUR'
    )

    # Create a surface style that uses the rendering
    red_surface_style = demo_file.createIfcSurfaceStyle(
        Name=None,
        Side='BOTH',
        Styles=[red_rendering]
    )

    # Create a presentation style assignment
    style_assignment = demo_file.createIfcPresentationStyleAssignment([red_surface_style])

    # Apply the red style to each column
    for column in columns:
        if column.Representation:
            for representation in column.Representation.Representations:
                for item in representation.Items:
                    # Check if the item already has a styled item
                    existing_styled_items = [
                        si for si in demo_file.by_type('IfcStyledItem') if si.Item == item
                    ]
                    if existing_styled_items:
                        # Update existing styled item with the new style
                        existing_styled_items[0].Styles = [style_assignment]
                    else:
                        # Create a new styled item
                        demo_file.createIfcStyledItem(
                            Item=item,
                            Styles=[style_assignment],
                            Name=None
                        )

    # Save the modified IFC file
    demo_file.write(output_path)
    print(f"Modified IFC file saved to {output_path}")

if __name__ == "__main__":
    main()

