# -*- coding: utf-8 -*-
"""
Created on Sun May 21 10:05:03 2017
Edited 11/30/2018 - DGF
Edited 12/01/2018 - DGF

@author: David George Ferguson. All rights Reserved.
"""
import random
import warnings
import numpy as np

class league_settings:
    """
    Class that defines the settings for a league that are relevent for building a schedule

    Arguments
    ---------
    gen_type : str
        Type of method used to generate schedule.
            'random' : randomly generated weeks consistent with constraints
            'yahoo' : Yahoo default method. Uses the input ordering of team names

    Attributes
    ----------
    team_names : list
        list of strings that specify the teams names in the league
    sched : list
        list of length the number of weeks in the regular season. The elements
        of the list are `weeks`. Weeks are lists of all the games that have
        been assigned to that week. Games are sets that list the two
        teams that are playing in the game.
    min_game_spacing : int
        The minimum allowable weeks between teams playing twice.
        The higher min_game_spacing the more likely schedule generation fails
            0 : matchups between same teams allowed in consecutive weeks
            1 : at least one week spacing between matchups between same teams
            n : at least n weeks spacing between matchups between same teams
    """
    def __init__(self, gen_type='random'):
        # Define team names here
        self.team_names = [
            'Heros',
            'Jabronies',
            'Truth',
            'Chimps',
            'Beatdoazers',
            'Hateful8',
            'Roughnecks',
            'Computerblue'
            ]
        # Set the number of weeks for the fantasy league's regular season
        numweeks = 15
        self.sched = numweeks*[[]]
        # Set initial scheudle information here
        SB_rematch_week = 1
        rival_week1 = 5
        rival_week2 = 11
        SB_rematch_game = {'Truth', 'Jabronies'}
        GB_rematch_game = {'Roughnecks', 'Hateful8'}
        self.sched[SB_rematch_week-1] = [
            SB_rematch_game,
            GB_rematch_game
            ]

        self.sched[rival_week1-1] = [
            {'Heros', 'Jabronies'},
            {'Truth', 'Hateful8'},
            {'Chimps', 'Roughnecks'},
            {'Beatdoazers', 'Computerblue'}
            ]

        self.sched[rival_week2-1] = [
            {'Heros', 'Computerblue'},
            {'Jabronies', 'Truth'},
            {'Chimps', 'Beatdoazers'},
            {'Hateful8', 'Roughnecks'}
            ]
        # Set schedule requierments here
        self.min_game_spacing = 1
        self.gen_type = gen_type


class fantasyschedule:
    """
    Class to generate a fantasy football league schedule

    Arguments
    ---------
    settings : league_settings class
        Input class that allows a user to specifiy the details of their league

    Attributes
    ----------
    team_names : list
        List of strings that specify the team names
    sched : list
        list of length the number of weeks in the regular season. The elements
        of the list are `weeks`. Weeks are sets of all the games that have
        been assigned to that week. Games are frozen sets that list the two
        teams that are playing in the game.
    min_game_spacing : int
        Minimum spacing between games
    max_num_matchups : int
        Maximum number of times a matchup is allowed in the schedule.
        Example:
            Team 'A' can play any other team at most 3 times
    max_num_matchups_that_have_max_num_games : int
        Maximum times that a team can have a matchup that has the
        maximum allowable number of matchups.
        Example:
            Team 'A' can play only 1 team 3 times. This will make sure that
            team 'A' will play all other teams 2 times. If team 'A' played 2
            teams three times then if would play one team only one time.

    Methods
    -------
    rand_genfullsched()
        Method to generate a random scheudle
    add_week_to_sched()
        Method to add a week to the schedule
    printsched()
        Method to print the schedule
    check_close_games(test_sched, week_index)
        Method to check if the test schedule has games that are too close
    check_num_matchups(test_sched)
        Method to check that no matchup occurs too many times
    """
    def __init__(self, settings=None):
        if settings is None:
            raise Exception('Must set league settings')
        else:
            self.gen_type = settings.gen_type
            self.team_names = settings.team_names
            self.sched = settings.sched
            try:
                self.min_game_spacing = settings.min_game_spacing
            except:
                self.min_game_spacing = 0
            self.sched = [[frozenset(game) for game in week] for week in self.sched]
            self.matchup_list = []
            for team_index, team1 in enumerate(self.team_names):
                for team2 in self.team_names[0:team_index]:
                    self.matchup_list += [frozenset({team1, team2})]

            num_games = len(self.sched)*len(self.team_names)//2
            self.max_num_matchups = int(np.ceil(num_games/len(self.matchup_list)))
            self.max_num_matchups_that_have_max_num_games = (
                (len(self.sched)-1)%(len(self.team_names)-1) + 1
                )
            if self.gen_type is 'yahoo':
                self.genfullsched_yahoo_default()
            elif self.gen_type is 'random':
                self.rand_genfullsched()
            else:
                raise Exception("Schedule generation type not recognized")
            self.printsched()

    def genfullsched_yahoo_default(self):
        """
        Yahoo default method to generate league schedule
        """
        # TODO check if Yahoo default is consistent with input schedule
        warnings.warn("Input schedule not used")
        num_weeks = len(self.sched)
        self.sched = num_weeks*[[]]

        for week_index in range(len(self.sched)):
            temp_week = []
            for team1_index, team1 in enumerate(self.team_names[0:-1]):
                team2_index = (-team1_index + week_index + 1) % (len(self.team_names)-1)
                if team2_index == team1_index:
                    team2 = self.team_names[-1]
                else:
                    team2 = self.team_names[team2_index]
                game = frozenset({team1, team2})
                if game not in temp_week:
                    temp_week.append(game)

            self.sched[week_index] = temp_week

    def rand_genfullsched(self):
        """
        Randomly generates the full schedule using the input schedule as a starting point.

        Notes
        -----
        If the schedule is not complete but the method add_week_to_schedule fails
        then the whole process starts over with in input shedule.
        This is tried up to 100 times at which point an excpetion is passed.
        """
        retrycount = 0
        complete_weeks = [len(week) for week in self.sched].count(len(self.team_names)//2)
        initial_sched = self.sched.copy()
        while retrycount < 100:
            # Schedule is re-initialized to the input schedule
            self.sched = initial_sched.copy()

            # start with the assumption that it is possible to find new weeks
            cant_find_new_week = False
            while complete_weeks < len(self.sched):
                week_pass = self.add_week_to_sched()
                complete_weeks = [len(week) for week in self.sched].count(len(self.team_names)//2)
                if not week_pass:
                    break
            if complete_weeks == len(self.sched):
                break
            if not week_pass:
                retrycount += 1
                continue
        if retrycount == 100:
            self.printsched()
            raise Exception("Could not generate schedule given constratins and input schedule")
        return

    def add_week_to_sched(self):
        """
        Adds a week of games to the sechdule that satisfies all scheudle constraints.

        Returns
        -------
        week_pass : bool
            True : If a random week was found that satisfies all constraints.
            False : If after 100 tries no week was found.

        Notes
        -----
        Finds the first non-complete week in the schedule and completes it with
        random a randomely generated list of games creating a test schedule.
        Then checks that the test schedule passes all the schedule constraints.
        If all constraints pass then the schedule is updated with the test_schedule
        If a constrain is not satisfied a new random week is generated.
        This is attempted 100 times after which an excpetion is passed.
        """
        week_index = [(len(week) < (len(self.team_names)//2)) for week in self.sched].index(True)
        week_as_list = [team for game in self.sched[week_index] for team in list(game)]
        count = 0
        week_pass = False
        while (not week_pass) and (count < 100):
            count += 1
            # Find first non-finished week

            # generate randum week
            remaining_teams = list(set(self.team_names) -set(week_as_list))
            test_week_list = (
                week_as_list
                +random.sample(remaining_teams, len(remaining_teams))
                )
            test_week = [
                frozenset({test_week_list[2*index], test_week_list[2*index+1]})
                for index in range(len(self.team_names)//2)
                ]
            test_sched = self.sched.copy()
            test_sched[week_index] = test_week
            # test if new schedule meets constraints
            pass_tests = []
            pass_tests.append(self.check_close_games(test_sched, week_index))
            pass_tests.append(self.check_num_matchups(test_sched))
            if False not in pass_tests:
                week_pass = True
        if week_pass:
            self.sched[week_index] = test_week
        return week_pass

    def printsched(self):
        """
        Prints the schedule to screen.
        """
        for index, week in enumerate(self.sched):
            print('Week'+str(index+1))
            weekout = ''
            for game in week:
                game = list(game)
                weekout += game[0]+' vs. '+game[1]+' | '
            print(weekout)

    def check_close_games(self, test_sched=None, week_index=None):
        """
        Check to make sure that week has no close games in neigboring weeks

        Arguments
        ---------
        test_sched : list
            list representing test schedule
        week_index : int
            Index of week to check that there are no other games in neighborning weeks
            If None then check all weeks

        Returns
        -------
        pass_check : bool
            Boolen condition of whether the close game check was passed.

        Notes
        -----
        self.min_game_spacing sets the minimum allowable space between games.
        self.min_game_spacing = 0 allows games in consecutive weeks
        """
        #Set initial pass_check to True

        pass_check = True
        if week_index is None:
            weeks_to_check = test_sched.copy()
        else:
            weeks_to_check = [test_sched[week_index]]

        # loop over all weeks to check if there are close games
        for week in weeks_to_check:
            # Build list of week indexes that are close but not before the
            # start or after the end of the season
            neighbor_week_index_list = [
                index
                for index in range(
                    week_index-self.min_game_spacing,
                    week_index+self.min_game_spacing+1
                    )
                if ((index > -1) and (index < len(test_sched)) and (index is not week_index))
                ]
            for neighbor_week_index in neighbor_week_index_list:
                check_week = test_sched[neighbor_week_index]
                # Build set intersection of games in weeks.
                # If intersection is non-empty then there is a common game
                if len(set(check_week) & set(week)) > 0:
                    pass_check = False
        return pass_check

    def check_num_matchups(self, test_sched=None):
        """
        Check that the number of matchups between teams is below appropriate amount

        Arguments
        ---------
        test_sched : list
            list representing test schedule

        Returns
        -------
        pass_check : bool
            Boolen condition of whether the num matchups check was passed.

        Notes
        -----
        If the number of weeks in the schedule is not evenly devisable by the
        number of opponents then teams will play some opponents one game more.
        The maximum times that a team plays an opponent is `self.max_num_matchups`.
        The number of opponents that a team plays the maximum number of times is
        `self.max_num_matchups_that_have_max_num_games`. This method checks that
        both max_num_matchups and max_num_matchups_that_have_max_num_games
        are not violated.
        """
        ###############
        # check the max_num_matchups condition
        ###############
        num_games_for_each_matchup = []
        for mu in self.matchup_list:
            #calculate number of games for each matchup
            num_games_for_each_matchup.append(
                [game for week in test_sched for game in week].count(mu)
                )
        # save the max_num_matchups condition
        pass_check_max_num_matchups = (max(num_games_for_each_matchup) <= self.max_num_matchups)

        ################
        # check the max_num_matchups_that_have_max_num_games condition for each team
        ################
        # list for each team wheter they have too many matchups with the maximum
        # number of games
        bool_team_max_num_matchup_okay = []
        for team in self.team_names:
            boolen_list_of_matchup_at_max = []
            for matchup_index, matchup in enumerate(self.matchup_list):
                # matchup at maximum
                condition1 = (
                    num_games_for_each_matchup[matchup_index]
                    == self.max_num_matchups
                    )
                # team in matchup
                condition2 = (team in matchup)
                # team in matchup and matchup at maximum
                boolen_list_of_matchup_at_max.append(
                    condition1 and condition2
                    )
            # count number of matchups at maximum for a given team
            num_max_matchups_for_team = (
                np.sum([int(b) for b in boolen_list_of_matchup_at_max])
                )
            # add to list checking that matchups at max okay for each team
            bool_team_max_num_matchup_okay.append(
                num_max_matchups_for_team
                <= self.max_num_matchups_that_have_max_num_games
                )

# More compact but less readable code that does the above calculation
#        for team in self.team_names:
#            num_max_matchups_for_team.append(
#                    np.sum([
#                            int(
#                                    (num_games_for_each_matchup[matchup_index]
#                                    == self.max_num_matchups)
#                                    and
#                                    (team in matchup)
#                                    )
#                            for matchup_index,matchup in enumerate(self.matchup_list)
#                            ]) <= self.max_num_matchups_that_have_max_num_games
#                            )

        pass_num_max_matchups = (False not in bool_team_max_num_matchup_okay)
        pass_check = pass_check_max_num_matchups and pass_num_max_matchups

        return pass_check

    def print_num_matchups(self):
        num_games_for_each_matchup = [
            [game for week in self.sched for game in week].count(mu)
            for mu in self.matchup_list
            ]
        
        column_width = (max([len(name) for name in self.team_names])+1)
        table_width = column_width*(len(self.team_names) + 1)

        table_title_string = ''.join(
            ['opponent'+(column_width-len('opponent')-1)*' '+'|']
            +[
                team.center(column_width-1)+'|'
                for index, team in enumerate(self.team_names)
                ]
           )

        print(table_title_string)
        print(table_width*'-')
        num_matchups = np.zeros([len(self.team_names),len(self.team_names)],
                                 dtype='int')
        for index1, team1 in enumerate(self.team_names):
            for index2, team2 in enumerate(self.team_names):
                if not team1 == team2:
                    num_matchups[index1, index2] = (
                        [game for week in self.sched for game in week].count(
                            frozenset({team1,team2}))
                        )

        for index1, team1 in enumerate(self.team_names):
            string_to_print = team1 + (column_width - len(team1) - 1)*' '+'|'
            for index2, team2 in enumerate(self.team_names):
                string_to_print += str(num_matchups[index1,index2]).center(
                        column_width-1)
                string_to_print += '|'
            print(string_to_print)
