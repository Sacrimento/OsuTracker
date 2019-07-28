import discord
import asyncio
import datetime as dt, time

from OsuApi import OsuApi

class OsuTracker():
    def __init__(self):
        self.funcs = {"stats": self.__stats, "help": self.__help, "track": self.__addTrack, "untrack": self.__untrack}
        self.tracked = []
        self.osuApi = OsuApi()

    def __getArgs(self, msg): ## Splitting the request to a list: args[0] here is the function to call, args[1+] are the actual arguments.
        args = msg.split(' ')[1:] ## Spliting
        args = list(filter(None, args)) ## Removing white spaces

        l = len(args) - 1 ## Those ugly lines to merge the quoted args
        i = 1
        while i < l:
            if (args[i][0] == '\'' or args[i][0] == '"') and (args[i + 1][-1] == '\'' or args[i + 1][-1] == '"'):
                args[i] = args[i] + ' ' + args[i + 1]
                args[i] = args[i][1:len(args[i]) - 1]
                args.pop(i + 1)
                l -= 1
            else:
                i += 1
        
        return args

    def __addTrack(self, args): ## Adds args[0] (aka PLAYER) to the tracked list
        ret = self.osuApi.getStats(args[0])
        if ret: ## If player exists
            if args[0] not in self.tracked:
                self.tracked.append(ret)
                return "Successfully added %s to the tracked list! Big brother is watching..." % (args[0])
            else:
                return "Player %s already tracked!" % (args[0])
        else:
            return "Unknown user \"" + args[0] + "\"..."
    
    def __untrack(self, args): ## Removes args[0] (aka PLAYER) from the tracked list
        if args[0] in self.tracked:
            self.tracked.remove(args[0])
            return "Successfully untracked %s!" % (args[0])
        else:
            return "%s was not tracked..." % (args[0])

    def __stats(self, args): ## Displays general stats about args[0] (aka PLAYER)
        ret = self.osuApi.getStats(args[0])
        if not ret:
            return "Unknown user \"" + args[0] + "\"..."
        return "Player %s is ranked #%s (%s PPs!!), and has %.2f%s accuracy!" % (args[0], ret['pp_rank'], ret['pp_raw'], float(ret['accuracy']), '%') 

    def __help(self, args):
        return """- Osu Tracker -
!osu stats PLAYER -- Displays general stats about PLAYER
!osu track PLAYER -- Adds PLAYER to tracked list. Whenever a tracked player will earn PPs, Osu Tracker will send a notification about the performance

For any suggestions, send me a PM (:"""

    ##TODO: CHANNEL ID IS HARDCODED NEED TO CHANGE THAT ASAP
    async def checkTracked(self, client): ## For every tracked player, every minute, check if a player won some PPs, in which case the bot will display the performance
        while not client.is_closed:
            for i, player in enumerate(self.tracked):
                newStats = self.osuApi.getStats(player["username"])
                if player["pp_raw"] <= newStats["pp_raw"]: ## If the player has won any PPs since the last check
                    self.tracked[i] = newStats
                    bmpInfo = self.__getNewScoreInfo(player["username"])
                    if bmpInfo:
                        await client.send_message(client.get_channel('456421575428800522'), "%s just won %d PPs, by achieving a %s rank on %s (%d*). This performance worths %s PPs!" % (player["username"], float(newStats["pp_raw"]) - float(player["pp_raw"]), bmpInfo["rank"], bmpInfo["title"], bmpInfo["stars"], bmpInfo["pp"]))
                        # print("%s just won %d PPs, by achieving a %s rank on %s (%d*). This performance worths %s PPs!" % (player["username"], float(newStats["pp_raw"]) - float(player["pp_raw"]), bmpInfo["rank"], bmpInfo["title"], bmpInfo["stars"], bmpInfo["pp"]))
                # else:
                #     print(player["username"] + " did not win any PPs :(")
            await asyncio.sleep(5)

    def __getNewScoreInfo(self, player): ## Return a string containing infos about the new score performed. New score is found by checking the time if each top plays of the user
        bestScores = self.osuApi.getBestScores(player)
        for score in bestScores:
            performanceDate = dt.datetime.strptime(score["date"], "%Y-%m-%d %H:%M:%S")
            lastCheck = dt.datetime.now() - dt.datetime.strptime("06", "%S")
            if time.mktime((performanceDate - lastCheck).timetuple()) > 0: ## The score was performed between this and last check
                ret = score
                bmp = self.osuApi.getBmpInfo(score["beatmap_id"])
                if bmp:
                    ret["stars"] = bmp["difficultyrating"]
                    ret["title"] = bmp["title"]
                    return ret

    def exec(self, message): ## Calling the appropriate function, defined in self.funcs
        args = self.__getArgs(message.content)
        
        if args[0] in list(self.funcs.keys()):
            return self.funcs[args[0]](args[1:])
        else:
            return "Sorry, I don't understand your ugly 6 digits language... Type \"!osu help\""
