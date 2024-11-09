import ifcopenshell

file_path = "./data/test.ifc"
output_path = "./data/output.ifc"

def main():
    # Open the IFC file
    demo_file = ifcopenshell.open(file_path)

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

