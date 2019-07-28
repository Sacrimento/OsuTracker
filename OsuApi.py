import requests

class OsuApi():
    def __init__(self):
        with open('./.secret', 'r') as t:
            osuToken = t.readline().split(' ')[1]
        self.baseUrl = "https://osu.ppy.sh/api/{}?k=" + osuToken

    def getStats(self, player):
        url = self.baseUrl.format("get_user") + "&u=" + player
        ret = requests.get(url).json()
        if ret:
            return ret[0]
        return None

    def getBestScores(self, player):
        url = self.baseUrl.format("get_user_best") + "&u=%s&limit=100" % (player)
        ret = requests.get(url).json()
        if ret:
            return ret
        return None

    def getBmpInfos(self, BmpID):
        url = self.baseUrl.format("get_beatmaps") + "&b=" + BmpID
        ret = requests.get(url).json()
        if ret:
            return ret
        return None