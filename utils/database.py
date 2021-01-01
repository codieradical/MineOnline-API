from datetime import datetime, timezone
import time

def getservers(mongo):
    def removeExpired(server):
        if not "expiresAt" in server:
            return False

        if (server["expiresAt"].replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc)):
            mongo.db.servers.delete_many({"_id": server["_id"]})
            # Hang on to the salt
            if (server["salt"] != None):
                mongo.db.servers.insert_one({"ip": server["ip"], "port": server["port"], "salt": server["salt"]})
            return False

        # Banned Servers
        if (server["ip"] == "51.222.28.199" and server["port"] == "12413"):
            mongo.db.servers.delete_many({"_id": server["_id"]})
            return False
            
        return True
    servers = list(mongo.db.servers.find())
    servers = list(filter(removeExpired, servers))
    servers.sort(key=lambda x: len(x["players"]) if "players" in x else 0, reverse=True)
    return servers