class TBL_sched_init:
    def __init__(self,SBmatch=None,GBmatch=None):
        self.TeamNames = ['Heros','Jabronies','Truth','Chimps','Beatdoazers','Eighth','Roughnecks','Computerblue']
        self.numweeks = 15
        self.rivalweeks = [4,10]
        self.RivalMatchups = [
        [['Heros','Jabronies'],['Truth','Eighth'],['Chimps','Roughnecks'],['Beatdoazers','Computerblue']],
        [['Heros','Computerblue'],['Jabronies','Truth'],['Chimps','Beatdoazers'],['Eighth','Roughnecks']]
        ]
        self.SBrematchWeek = 1
        self.GBrematchWeek = 1
        self.init_sched = []
        for week_index in range(len(self.numweeks)):
            if week_index == self.SBrematchWeek:
                
