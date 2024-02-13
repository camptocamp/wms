This module overrides the put_in_pack method from stock.picking
so that it marks lines as shopfloor_checkout_done
when putting them in a pack in the backend.

This is done to make sure that these lines are displayed
in the shopfloor frontend even if they're handled in the backend.