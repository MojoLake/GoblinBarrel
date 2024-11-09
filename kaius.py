import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.element
import ifcopenshell.api

file_path = "./data/test.ifc"
output_path = "./data/output.ifc"


def get_relevant_types(ifc_file, element_types=[]):
    elements = []
    if not element_types:
        return ifc_file
    for elem_type in element_types:
        elements.extend(ifc_file.by_type(elem_type))
    return elements


def profile_area(item):
    if item.is_a("IfcExtrudedAreaSolid"):
        profile = item.SweptArea
        return compute_profile_area(profile)
    elif item.is_a("IfcSweptAreaSolid"):
        profile = item.SweptArea
        return compute_profile_area(profile)
    elif item.is_a("IfcMappedItem"):
        return handle_mapped_item(item)
    return 0 # default to area 0


def is_big_enough(element, min_area_m2):
    if not element.Representation:
        return False

    print("Element:", element)

    body_rep = list(filter(lambda x: x.RepresentationIdentifier == 'Body', element.Representation.Representations))

    assert(len(body_rep) <= 1)
    if len(body_rep) == 0:
        return False

    body_rep = body_rep[0]

    return any(abs(profile_area(item)) >= min_area_m2 for item in body_rep.Items)



def filter_elements_by_cross_section_area(ifc_file, _min_area_m2=0.09):
    print("filter elements by cross secion area:")
    elements = get_relevant_types(ifc_file, ["IfcBeam", "IfcColumn"])
    print("elements")
    for element in elements:
        print(element)
    filtered_elements = filter(is_big_enough, elements)



def compute_profile_area(profile):
    if profile.is_a("IfcRectangleProfileDef"):
        return profile.XDim * profile.YDim
    elif profile.is_a("IfcCircleProfileDef"):
        return 3.141592653589793 * (profile.Radius ** 2)
    elif profile.is_a("IfcIShapeProfileDef"):
        return compute_i_shape_area(profile)
    elif profile.is_a("IfcLShapeProfileDef"):
        return compute_l_shape_area(profile)
    elif profile.is_a("IfcCompositeProfileDef"):
        return compute_composite_profile_area(profile)
    else: 
        # Unsupported profile type
        return None

def compute_i_shape_area(profile):
    if profile.is_a('IfcIShapeProfileDef'):
        # Check for standard attribute names
        if hasattr(profile, 'OverallDepth') and hasattr(profile, 'OverallWidth'):
            h = profile.OverallDepth
            b = profile.OverallWidth
        else:
            # Unsupported or unexpected profile format
            return None
        tw = profile.WebThickness
        tf = profile.FlangeThickness
        # Calculate area of the I-shape
        area = (b * tf * 2) + ((h - (2 * tf)) * tw)
        return area
    else:
        # Not an IfcIShapeProfileDef
        return None

def compute_l_shape_area(profile):
    if profile.is_a('IfcLShapeProfileDef'):
        if hasattr(profile, 'Leg1Length') and hasattr(profile, 'Leg2Length'):
            # IFC4 schema
            b = profile.Leg1Length
            h = profile.Leg2Length
        elif hasattr(profile, 'Width') and hasattr(profile, 'Depth'):
            # IFC2X3 schema
            b = profile.Width
            h = profile.Depth
        else:
            # Unsupported or unexpected profile format
            return None
        t = profile.Thickness
        # Calculate area of the L-shape
        area = (b * t) + ((h - t) * t)
        return area
    else:
        # Not an IfcLShapeProfileDef
        return None

def compute_composite_profile_area(profile):
    area = 0
    for sub_profile in profile.Profiles:
        sub_area = compute_profile_area(sub_profile)
        if sub_area is None:
            return None  # Unsupported sub-profile
        area += sub_area
    return area


def handle_mapped_item(mapped_item):
    # Access the mapping source
    mapping_source = mapped_item.MappingSource
    if mapping_source and mapping_source.MappedRepresentation:
        for item in mapping_source.MappedRepresentation.Items:
            if item.is_a("IfcExtrudedAreaSolid"):
                profile = item.SweptArea
                return compute_profile_area(profile)
    return None






def main():

    print("Program starting...")
    demo_file = ifcopenshell.open(file_path)

    # Get the filtered elements
    filtered_elements = filter_elements_by_cross_section_area(demo_file)

    return

    allowed_types = {"IfcSlab", "IfcWall", "IfcPlate", "IfcBuilding", "IfcBuildingStorey", "IfcSite"}

    # Create a set of element IDs to retain
    elements_to_keep = {element.id() for element in filtered_elements}
    for elem_type in allowed_types:
        elements_to_keep.update({element.id() for element in demo_file.by_type(elem_type)})

    # Collect elements to delete
    elements_to_delete = [element for element in demo_file.by_type("IfcProduct") if element.id() not in elements_to_keep]

    # Print elements to be retained and removed for debugging
    print("Elements to keep (IDs):", elements_to_keep)
    print("Elements to delete (IDs):", [element.id() for element in elements_to_delete])

    # Directly delete elements
    for element in elements_to_delete:
        demo_file.remove(element)

    # Write the modified IFC file to output path
    demo_file.write(output_path)
 

if __name__ == "__main__":
    main()

