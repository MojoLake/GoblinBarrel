class spatialSurface:
    #Make list of vertices actually contain faces (vectors of n elements scraped from polyloop)
    def __init__(self, listOfFaces):
        self.faces = listOfFaces
    
    #Try to reconstruct cross-sectional-area, based on vertices? Polyloop could tell us how to group them


