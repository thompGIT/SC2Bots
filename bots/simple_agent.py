from pysc2.agents import base_agent
from pysc2.lib import actions
from pysc2.lib import features
import time

# Functions
_BUILD_SUPPLYDEPOT = actions.FUNCTIONS.Build_SupplyDepot_screen.id
_NOOP = actions.FUNCTIONS.no_op.id
_SELECT_POINT = actions.FUNCTIONS.select_point.id

# Features
_PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_UNIT_TYPE = features.SCREEN_FEATURES.unit_type.index

# Unit IDs
_TERRAN_COMMANDCENTER = 18
_TERRAN_SCV = 45

# Parameters
_PLAYER_SELF = 1
_NOT_QUEUED = [0]
_QUEUED = [1]

class SimpleAgent(base_agent.BaseAgent):

    # Spawn Location - Simple64 map only has 2
    base_top_left = None

    # Some helper variables
    supply_depot_built = False
    scv_selected = False

    def step(self, obs):
        super(SimpleAgent, self).step(obs)

        # Slow things down
        time.sleep(0.5)

        # Determine our spawn location
        if self.base_top_left is None:
            player_y, player_x = (obs.observation["minimap"][_PLAYER_RELATIVE] == _PLAYER_SELF).nonzero()
            self.base_top_left = player_y.mean() <= 31
            if self.base_top_left:
                print("Spawned in Top Left")
            else:
                print("Spawned in Lower Right")

        # Build a Supply Depot
        if not self.supply_depot_built:

            # Select an SCV...
            if not self.scv_selected:

                # Target the first SCV on the screen
                unit_type = obs.observation["screen"][_UNIT_TYPE]
                unit_y, unit_x = (unit_type == _TERRAN_SCV).nonzero()
                target = [unit_x[0], unit_y[0]]

                self.scv_selected = True
                print("SCV Selected")

                # Select / Click the SCV
                return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])

            # ...Build the Supply Depot
            elif _BUILD_SUPPLYDEPOT in obs.observation["available_actions"]:

                # Locate a position to drop the Supply Depot
                unit_type = obs.observation["screen"][_UNIT_TYPE]
                unit_y, unit_x = (unit_type == _TERRAN_COMMANDCENTER).nonzero()
                target = self.transformLocation(int(unit_x.mean()), 0, int(unit_y.mean()), 20)

                self.supply_depot_built = True
                print("Building a Supply Depot")

                # Issue the command to build a Supply Depot
                return actions.FunctionCall(_BUILD_SUPPLYDEPOT, [_NOT_QUEUED, target])

        # Default to doing nothing this turn
        return actions.FunctionCall(actions.FUNCTIONS.no_op.id, [])

    # Transform relative location depending on spawn point
    def transformLocation(self, x, x_distance, y, y_distance):
        if not self.base_top_left:
            return [x - x_distance, y - y_distance]
        return [x + x_distance, y + y_distance]