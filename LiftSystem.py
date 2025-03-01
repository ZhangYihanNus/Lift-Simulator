class LiftSystem:
    def __init__(self, name):
        self.name = name

    lifts = []
    targets = []

    def initialize(self, liftInitials):
        global lifts
        global targets
        
        for lift in liftInitials:
            self.lifts.append(lift)
            self.targets.append([])
        self.targets.append([])
        
        print("Initializing lifts:")
        print(self.lifts)
        #TODO: initialize into dicts


    def update(self, source, targetLevel):
        global lifts
        global targets
        
        #TODO: check target level is not the same as current level
        targets[source].append(targetLevel)

        





if __name__ == "__main__":

    mySystem = LiftSystem("lift simulator")
    liftsInit = [2,5,10]
    mySystem.initialize(liftsInit)


