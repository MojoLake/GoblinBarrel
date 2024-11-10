import ifcopenshell

def get_low_volume_elements(ifc_file, volume_threshold):
    """
    Returns a list of columns and beams that have a Volume property less than the specified threshold.
    
    Args:
        ifc_file_path (str): Path to the IFC file.
        volume_threshold (float): The volume threshold in cubic meters.
        
    Returns:
        List[Tuple[str, float]]: A list of tuples containing the GlobalId and volume of each element 
                                 with a volume below the threshold.
    """
    # Open the IFC file
    
    # List to store elements with volume less than the threshold
    low_volume_elements = []
    
    # Function to get the Volume property if it exists
    def get_volume_property(element):
        for definition in element.IsDefinedBy:
            if hasattr(definition, "RelatingPropertyDefinition"):
                property_set = definition.RelatingPropertyDefinition
                if property_set.is_a("IfcPropertySet"):
                    for prop in property_set.HasProperties:
                        if prop.Name == "Volume" and prop.NominalValue:
                            return float(prop.NominalValue.wrappedValue)
        return None
    
    # Loop through all columns and beams
    for element_type in ["IfcColumn", "IfcBeam"]:
        elements = ifc_file.by_type(element_type)
        
        for element in elements:
            # Get the Volume property
            volume = get_volume_property(element)
            
            # Check if the volume is below the threshold
            if volume is not None and volume < volume_threshold:
                low_volume_elements.append((element.GlobalId, volume))
    
    return low_volume_elements
