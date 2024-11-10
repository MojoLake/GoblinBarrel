import ifcopenshell



def material_identifier(id1,id2, ifcFile):
    
    mat1 = "none"
    mat2 = "none"

    element1 = ifcFile.by_id(id1)
    element2 = ifcFile.by_id(id2)


    material_relation1 = next((rel for rel in element1.HasAssociations if rel.is_a("IfcRelAssociatesMaterial")), None)
    material_relation2 = next((rel for rel in element2.HasAssociations if rel.is_a("IfcRelAssociatesMaterial")), None)

    if material_relation1:
        material = material_relation1.RelatingMaterial
        if material.is_a("IfcMaterial"):
            material_name = material.Name.lower()
            if "concrete" in material_name:
                mat1 =  "concrete"
            elif "steel" in material_name:
                mat1 = "steel"
            else:
                print(f"Material 1 is {material.Name} and not of our interest")
        else:
            print("Material information not available.")

    
    if material_relation2:
        material = material_relation2.RelatingMaterial
        if material.is_a("IfcMaterial"):
            material_name = material.Name.lower()
            if "concrete" in material_name:
                mat2 = "concrete"
            elif "steel" in material_name:
                mat2 = "steel"
            else:
                print(f"Material 2 is {material.Name} and not of our interest")
        else:
            print("Material information not available.")

    return (mat1, mat2)
    





def main():
    file_path = "./data/test.ifc"
    ifc_file = ifcopenshell.open(file_path)
    beams = list(map(lambda x: x.id() ,ifc_file.by_type("IfcBeam")))

    print(material_identifier(beams[0], beams[1], ifc_file))


if __name__ == "__main__":
    main()
