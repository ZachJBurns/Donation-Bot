from steam.steamid import SteamID
def tryURL(arg: str):
    steam = SteamID(SteamID.from_url(arg))
    if steam.is_valid():
        return steam.as_steam2;
    else:
        return False

def tryID(arg: str):
    steam = SteamID(arg)
    if steam.is_valid():
        return steam.as_steam2
    else:
        return False

def checkMessageForID(args: tuple):
    args = list(args)
    steamString = None
    for arg in args:
        if 'steam' in arg.lower():
            steamString = arg
            break
    if steamString is None:
        raise Exception("Could not find any Steam ID or Steam Profile URL in your message")

    steamID = None
    if steamString != None:
        steamID = tryURL(steamString)
        if steamID is False:
            steamID = tryID(steamString)

    if steamID != False:
        return steamID
    else:
        raise Exception("Please make sure you send a valid Steam ID or Steam Profile URL")
