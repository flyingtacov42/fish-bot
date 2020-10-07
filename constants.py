# Hyperparameters for training
GAMMA = 0.999
MAX_HISTORY_LENGTH = 10000
TRAINING_GAMES = 1

# Rewards for training
REWARD_SUCCESSFUL_ASK = 1
REWARD_UNSUCCESSFUL_ASK = -1
REWARD_SUCCESSFUL_CALL = 10
REWARD_UNSUCCESSFUL_CALL = -10
REWARD_WIN = 100
REWARD_LOSE = -100

# Constants for state and action tables
SIZE_STATES = 763
SIZE_ACTIONS = 162

# Constants for information in info dict
YES = 1
NO = -1
UNSURE = 0

# Constants for Fish Game
DECK_SIZE = 54
RANK_SIZE = 13
SUIT_SIZE = 4
JOKERS = 2
HS_SIZE = 6 # Half suit size

NUM_PLAYERS = 6
NUM_TEAMS = 2 # This is not used anywhere in my code yet, but may implement in the future