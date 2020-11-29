#!/venv/bin/python

# internal dependencies
from data_types.ProgramMode import PROGRAM_MODE 


class TwoWayMap(dict):

    def __init__(self, initDict):
        for key, val in initDict.items():
            self.__setitem__(key, val)


    def __setitem__(self, key, value):
        # Remove any previous connections with these values
        if key in self:
            del self[key]
        if value in self:
            del self[value]
        dict.__setitem__(self, key, value)
        dict.__setitem__(self, value, key)


    def __delitem__(self, key):
        dict.__delitem__(self, self[key])
        dict.__delitem__(self, key)


    def __len__(self):
        # Returns the number of connections
        return dict.__len__(self) // 2


PROGRAM_MODE_MAP = TwoWayMap({
	"tv-episodes": PROGRAM_MODE.TV_EPISODES,
	"tv-seasons":  PROGRAM_MODE.TV_SEASONS
})


PROGRAM_MODE_DIRECTORY_KEY_MAP = TwoWayMap({
	PROGRAM_MODE.TV_EPISODES: "TV_TARGET_DIR",
	PROGRAM_MODE.TV_SEASONS:  "TV_TARGET_DIR"
})
