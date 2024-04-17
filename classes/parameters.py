class ModelParameters:
    def __init__(self, operRooms = list(), blockIds = list(), 
                 specialties = list(), demand = dict(), revenue = dict(), 
                 cost = dict(), infra = dict(), pastDeficit = dict(), 
                 anestAvailab = dict(), teamsAvailab = dict(), 
                 priorities = dict(), needAnest = dict()):
        self.operRooms = operRooms
        self.blockIds = blockIds
        self.specialties = specialties
        self.demand = demand
        self.revenue = revenue
        self.cost = cost
        self.infra = infra
        self.pastDeficit = pastDeficit
        self.anestAvailab = anestAvailab
        self.teamsAvailab = teamsAvailab
        self.priority = priorities
        self.needAnest = needAnest

    def getOperRooms(self):
        return self.operRooms

    def getBlockIds(self):
        return self.blockIds

    def getSpecialties(self):
        return self.specialties

    def getDemand(self):
        return self.demand

    def getRevenue(self):
        return self.revenue

    def getCost(self):
        return self.cost

    def getInfra(self):
        return self.infra

    def getPastDeficit(self):
        return self.pastDeficit

    def getAnestAvailab(self):
        return self.anestAvailab

    def getTeamsAvailab(self):
        return self.teamsAvailab

    def getPriority(self):
        return self.priority

    def getNeedAnest(self):
        return self.needAnest
    
    def __str__(self):
        classStr = "ModelParameters:\n"
        classStr += "operRooms: " + str(self.operRooms) + "\n"
        classStr += "blockIds: " + str(self.blockIds) + "\n"
        classStr += "specialties: " + str(self.specialties) + "\n"
        classStr += "demand: " + str(self.demand) + "\n"
        classStr += "revenue: " + str(self.revenue) + "\n"
        classStr += "cost: " + str(self.cost) + "\n"
        classStr += "infra: " + str(self.infra) + "\n"
        classStr += "pastDeficit: " + str(self.pastDeficit) + "\n"
        classStr += "anestAvailab: " + str(self.anestAvailab) + "\n"
        classStr += "teamsAvailab: " + str(self.teamsAvailab) + "\n"
        classStr += "priority: " + str(self.priority) + "\n"
        classStr += "needAnest: " + str(self.needAnest) + "\n"
        return classStr