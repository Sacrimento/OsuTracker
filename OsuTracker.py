import discord
import requests

class OsuTracker():
    def __init__(self):
        self.funcs = {"stats": self.__osuStats, "help": self.__help, "track": self.__track, "untrack": self.__untrack}
        
        with open('./.secret', 'r') as t:
            osuToken = t.readline().split(' ')[1]
        self.osuBaseUrl = "https://osu.ppy.sh/api/{}?k=" + osuToken

        self.tracked = []

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

    def __track(self, args): ## Adds args[0] (aka PLAYER) to the tracked list
        url = self.osuBaseUrl.format("get_user") 
        url += "&u=" + args[0]
        if requests.get(url).json(): ## If player exists
            if args[0] not in self.tracked:
                self.tracked.append(args[0])
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

    def __osuStats(self, args): ## Displays general stats about args[0] (aka PLAYER)
        url = self.osuBaseUrl.format("get_user")
        url += "&u=" + args[0]
        ret = requests.get(url).json()
        if not ret:
            return "Unknown user \"" + args[0] + "\"..."
        return "Player %s is ranked #%s (%s pps!!), and has %.2f%s accuracy!" % (args[0], ret[0]['pp_rank'], ret[0]['pp_raw'], float(ret[0]['accuracy']), '%') 

    def __help(self, args):
        return """- Osu Tracker -
!osu stats PLAYER -- Displays general stats about PLAYER
!osu track PLAYER -- Adds PLAYER to tracked list. Whenever a tracked player will earn PPs, Osu Tracker will send a notification about the performance

For any suggestions, send me a PM (:"""

    def exec(self, message):
        args = self.__getArgs(message.content)
        
        if args[0] in list(self.funcs.keys()):
            return self.funcs[args[0]](args[1:])
        else:
            return "Sorry, I don't understand your ugly 6 digits language... Type \"!osu help\""
