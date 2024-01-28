zero = time.time()
def now(self):
    return time.time() - zero
    
class Logging(enum):
    Debug = 5
    Zero = 4
    Main = 3
    Minor = 2
    Pedantic = 1
    Get = 0
    
log_level = Logging.Main
log_list = {
    "move" : Debug.Pedantic,
    "turn" : Debug.Pedantic,
    "goto" : Debug.Pedantic,
    "snap" : Debug.Pedantic,
    "peek" : Debug.Pedantic,
    "triangulate" : Debug.Pedantic,
    "getPower" : Debug.Log,
}