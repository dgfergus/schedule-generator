# -*- coding: utf-8 -*-
"""
Created on Sun May 21 10:05:03 2017

@author: david
"""
import numpy as np
import random

class league_settings:
    def __init__(self):
        self.team_names = ['Heros','Jabronies','Truth','Chimps','Beatdoazers','Staffords','Roughnecks','Computerblue']
        self.numweeks = 15
        self.rivalweeks = [4,10]
        self.RivalMatchups = [['Heros','Jabronies','Truth','Staffords','Chimps','Roughnecks','Beatdoazers','Computerblue'],
                           ['Heros','Computerblue','Jabronies','Truth','Chimps','Beatdoazers','Staffords','Roughnecks']]
        self.SBrematchWeek = 1 

class fantasyschedule:
    """
    Class to generate a fantasy football league schedule
    
    Attributes
    ----------
    team_names : list
        List of strings for the team names
    season_length : int
        Length of regular season
    sched : list
        List of length `season_length`. Each element of the list is a list of the 
        matchups that week. Matchups are represented by a set of team names.
        
    Methods
    -------
    weeks_have_duplicate_game(week1,week2):
        Returns True if the two weeks have a duplicate game, else False.
        
    
    
    
    
    """
    def __init__(self,basicsettings = basicsettings(), SBrematch = ['Truth','Jabronies'], GenFullSched = False):
        if basicsettings is None:
            raise('Must Set Basic Settings')
        else:
            self.team_names = basicsettings.team_names
            self.numweeks = basicsettings.numweeks
            self.rivalweeks = basicsettings.rivalweeks
            self.RivalMatchups = basicsettings.RivalMatchups
            self.SBrematchWeek = basicsettings.SBrematchWeek
            self.SBrematch = SBrematch
            if GenFullSched == True:
                self.genfullsched()
                self.printsched()
            
    def buildmatchuplist(self):
        matchuplist = []
        for team1Index,team1 in enumerate(self.team_names):
            for team2Index,team2 in enumerate(self.team_names):
                if team2Index > team1Index:
                    matchuplist.append(list(np.sort([team1,team2])))
        self.matchups = matchuplist
        return self.matchups
    
    def buildfullmatchuplist(self,numduplicates=3):
        fullmatchuplist = []
        for n in range(numduplicates):
            for matchupVal in self.matchups:
                matchupVal = np.sort(list(matchupVal))
                strtoadd = ''
                for stringval in matchupVal:
                    strtoadd += stringval
                strtoadd += str(n+1)
                fullmatchuplist.append(strtoadd)
        self.fullmatchuplist = fullmatchuplist
        self.remainingmatchuplist = fullmatchuplist.copy()

        return self.fullmatchuplist
            
    def genweek(self,weekstart = None):
        if weekstart is None:
            remainingTeams = self.team_names.copy()
            week = []
        else:
            week = weekstart.copy()
            remainingTeams = list(set(self.team_names)-set(week))
        while len(remainingTeams) >0:
            team = random.choice(remainingTeams)
            week.append(team)
            remainingTeams = list(set(remainingTeams)-set([team]))
        return week
    
    def matchupsfromweek(self,week):
        matchups = []
        for index,team in enumerate(week):
            if index%2 ==0:
                match = [team]
            else:
                match.append(team)
                matchups.append(set(match))
        return matchups
    
    def matchupstringtoteams(self,fullmatchuplist = 'HerosTruth1'):
        team1 = fullmatchuplist[0]
        team2 = ''
        isfirstteam = True
        for charIndex,char in enumerate(fullmatchuplist):
            if not(charIndex in [0,len(fullmatchuplist)-1]):
                if str.istitle(char):
                    isfirstteam = False
                if isfirstteam:
                    team1 += char
                else:
                    team2 += char
            
        return team1,team2    

    def genweekfrommatchuplist(self,weekstart = None, printstatus = False):
        if weekstart is None:
            remainingTeams = self.team_names.copy()
            week = []
        else:
            week = weekstart
            remainingTeams = list(set(self.team_names)-set(week))
        # sometimes you get stuck choosing the wrong matchups and need to try again
        remainingTeamsIni = remainingTeams.copy()
        weekini = week.copy()
        count = 0
        foundweek = False
        while not(foundweek):
            count += 1
            if printstatus:
                print('Trying to find week from matchuplist. Try '+str(count))
            if count == 100:
                raise Exception('probably cannot generate week from existing matchups')
            # restart with new list of matchups to choose from
            # and new remaining team list
            remainingmatchupstochoosefrom = self.remainingmatchuplist.copy()
            remainingTeams = remainingTeamsIni.copy()
            week = weekini.copy()
            while len(remainingTeams) >0 and len(remainingmatchupstochoosefrom) > 0:
                randommatchup = random.choice(remainingmatchupstochoosefrom)
                remainingmatchupstochoosefrom = list(set(remainingmatchupstochoosefrom)-set([randommatchup]))
                team1,team2 = self.matchupstringtoteams(randommatchup)
                if (team1 in remainingTeams) and (team2 in remainingTeams):
                    remainingTeams = list(set(remainingTeams)-set([team1,team2]))
                    week.append(team1)
                    week.append(team2)
                if len(week) == len(self.team_names):
                    foundweek = True
            
        return week
    
    def removeweek(self,week):
        numberofremainingteams = len(self.remainingmatchuplist)
        for weekIndex,team in enumerate(week):
            if weekIndex%2 == 1:
                matchup = list(np.sort([team,week[weekIndex-1]]))
                matchupstring = ''
                for team in matchup:
                    matchupstring += team
                for fullmatchupstring in self.remainingmatchuplist:
                    reducedmatchupstring = fullmatchupstring[0:(len(fullmatchupstring)-1)]
                    if matchupstring == reducedmatchupstring:
                        self.remainingmatchuplist = list(set(self.remainingmatchuplist) - set([fullmatchupstring]))
                        break
        if not(numberofremainingteams-int(round(len(week)/2)) == len(self.remainingmatchuplist)):
            raise Exception('week was not in the remaining matchup list')
            
        # cycle through the remaining matchups
        # check to see if either team has one opponents with three scheduled matchups against that opponent
        # if so then count the total number of secheduled and remaining matchups for each other opponent
        # (the scheduled matchups don't change and can be precalculated)
        # if the total is three and remaining matchups is more than zero remove the matchup
        schedmatchuparray = self.countmatchupsinschedule()
        numtripmatch = self.countnumberoftriplematchups()

        for matchup in self.remainingmatchuplist:
            team1,team2 = self.matchupstringtoteams(matchup)
            team1Index = self.team_names.index(team1)
            team2Index = self.team_names.index(team2)
            matchupavailarray = self.countremainingavailablematchups()
            totalpotentialmatchups = schedmatchuparray[team1Index,team2Index] + matchupavailarray[team1Index,team2Index]
            if (numtripmatch[team1Index] == 1) or (numtripmatch[team2Index] == 1):
                if totalpotentialmatchups >= 3:
                    self.remainingmatchuplist = list(set(self.remainingmatchuplist) - set([matchup]))
            
        return self.remainingmatchuplist
                
        
    def initsched(self):
        self.sched = []
        for weekindex in range(self.numweeks):
            self.sched.append([])
        
        # TBL Superbowl Rematch
        for team in self.SBrematch:
            self.sched[self.SBrematchWeek-1].append(team)
        
        # Extend to full week of matchups
        self.sched[self.SBrematchWeek-1] = self.genweek(self.sched[self.SBrematchWeek-1])
    
        # rival weeks
        for Rivalindex,weekIndex in enumerate(self.rivalweeks):
            self.sched[weekIndex-1] = self.RivalMatchups[Rivalindex]
            
        return self.sched
    
    def printsched(self):
        for index,week in enumerate(self.sched):
            print('Week'+str(index+1))
            weekout = []
            for teamIndex,team in enumerate(week):
                if teamIndex%2 ==1:
                    weekout.append(team+' vs. '+week[teamIndex-1])
            print(weekout)
            
    def weeks_have_duplicate_game(self,weekList1,weekList2):
        DuplicateGame = False
        for MatchUp1 in self.matchupsfromweek(weekList1):
            for MatchUp2 in self.matchupsfromweek(weekList2):
                if MatchUp1 == MatchUp2:
                    DuplicateGame = True
        return DuplicateGame
    
    def initialremovematchups(self):
        for weekIndex,week in enumerate(self.sched):
            if len(week) == len(self.team_names):
                # remove games from matchuplist
                self.removeweek(week) 
        return self.remainingmatchuplist
        
    def countcompletedweeks(self):
        count = 0
        for week in self.sched:
            if len(week) == len(self.team_names):
                count += 1
        return count
    
    
    def add_week_to_sched(self,printstatus = False):
        # Find first non-finished week
        firstemptyweek = -1
        for weekIndex,week in enumerate(self.sched):
            if len(week) < len(self.team_names): # If the week is not full
                if firstemptyweek == -1:
                    firstemptyweek = int(weekIndex)

        else:
            if firstemptyweek == 0:
                previousweek = []
            else:
                previousweek = self.sched[firstemptyweek-1].copy()
            if weekIndex == (len(self.sched)-1):
                nextweek = []
            else:
                nextweek = self.sched[firstemptyweek+1].copy()
        gennewweek = True
        count = 0
        while (gennewweek) and (count < 100):
            count += 1
            randweek = self.genweekfrommatchuplist(printstatus=printstatus)
            if printstatus:
                print('try '+str(count)+' at generating a random week that works with the schedule:')
                print(randweek)
            previoussame = self.weeks_have_duplicate_game(randweek,previousweek)
            nextsame = self.weeks_have_duplicate_game(randweek,nextweek)
            
            allhavelessthanthreetriplematchups = self.allnumtriplematchupslessthanthree(testweek = randweek)
            
            if not(previoussame) and not(nextsame) and allhavelessthanthreetriplematchups:
                self.sched[firstemptyweek] = randweek
                self.removeweek(randweek)
                gennewweek = False
                    
        completeweeks = self.countcompletedweeks()
        if completeweeks == len(self.sched):
            if printstatus:
                self.printsched()
        else:
            if printstatus:
                print('The number of complete weeks is '+str(completeweeks))
                print('The number left to fill is '+str(len(self.sched)-completeweeks))
                print('The number of remaining matchups to choose from is '+str(len(self.remainingmatchuplist)))
                print('Completed Matchup array then available matchup array.')
                print(self.countmatchupsinschedule())
                print(self.countremainingavailablematchups())
                self.printsched()
        
        return completeweeks
        
    def genfullsched(self,printstatus = False):
        retrycount = 0
        iscomplete = False
        while (retrycount < 100) and not(iscomplete):
            print('Try number '+str(retrycount)+' at generating full schedule.')
            retrycount += 1
            self.buildmatchuplist()
            self.buildfullmatchuplist()
            self.initsched()
            self.initialremovematchups()
            completeweeks = self.countcompletedweeks()
            count = 0
            while (completeweeks < len(self.sched)) and count < 20:
                count += 1
                self.add_week_to_sched(printstatus = printstatus)
                completeweeks = self.countcompletedweeks()
            if completeweeks == len(self.sched):
                  iscomplete = True
        if printstatus:
            self.printsched()
        return
        
        
    def countmatchupsinschedule(self,testweek = None):
        
        matchupcountarray = np.zeros([len(self.team_names),len(self.team_names)],dtype = 'int')
        
        for teamIndex1, teamname1 in enumerate(self.team_names):
            for teamIndex2, teamname2 in enumerate(self.team_names):
                for week in self.sched:
                    for mu in self.matchupsfromweek(week):
                        if set([teamname1,teamname2]) == mu:
                                matchupcountarray[teamIndex1,teamIndex2] += 1
                                
        if not(testweek is None):
            mups = self.matchupsfromweek(testweek)
            for mu in mups:
                for teamIndex1, team1name in enumerate(self.team_names):
                    for teamIndex2, team2name in enumerate(self.team_names):
                        if set([teamname1,teamname2]) == mu:
                            matchupcountarray[teamIndex1,teamIndex2] += 1
                        
        return matchupcountarray
    
    def countremainingavailablematchups(self,testweek = None):
        
        matchupcountarray = np.zeros([len(self.team_names),len(self.team_names)],dtype = 'int')
        
        for teamIndex, teamname in enumerate(self.team_names):
            for remainmatch in self.remainingmatchuplist:
                team1,team2 = self.matchupstringtoteams(remainmatch)
                if teamname in set([team1,team2]):
                    for otherteamIndex,otherteam in enumerate(self.team_names):
                        if otherteam in set(set([team1,team2])-set([teamname])):
                            matchupcountarray[teamIndex,otherteamIndex] += 1
                            
        if not(testweek is None):
            mups = self.matchupsfromweek(testweek)
            for mu in mups:
                for teamIndex1, team1name in enumerate(self.team_names):
                    for teamIndex2, team2name in enumerate(self.team_names):
                        if team1name in mu:
                            if (team2name in mu) and not(team1name == team2name):
                                matchupcountarray[teamIndex1,teamIndex2] += -1
                        
        return matchupcountarray
    
    def countnumberoftriplematchups(self,testweek = None):
        mupcountarray = self.countmatchupsinschedule(testweek=testweek)
        numtriplematchups = []
        for matchupsarray in mupcountarray:
            numtriple = 0
            for mupcount in matchupsarray:
                if mupcount == 3:
                    numtriple += 1
            numtriplematchups.append(numtriple)
            
        return numtriplematchups

    def allnumtriplematchupslessthanthree(self,testweek = None):
        triplematchupsarelessthanthree = True
        for numtripmatch in self.countnumberoftriplematchups(testweek=testweek):
            if numtripmatch>3:
                triplematchupsarelessthanthree = False
        return triplematchupsarelessthanthree
        
            
          
        
        