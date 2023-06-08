# Copyright 2023 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__file__)


def post_init_hook(cr, registry):
    _logger.info("Add set packaging dimension option on reception scenario")
    env = api.Environment(cr, SUPERUSER_ID, {})
    scenario = env.ref("shopfloor_reception.scenario_reception")
    options = json.loads(scenario.options_edit)
    options.update({"set_packaging_dimension": True})
    scenario.options_edit = json.dumps(options)


def uninstall_hook(cr, registry):
    _logger.info("Remove set packaging dimension option on reception scenario")
    env = api.Environment(cr, SUPERUSER_ID, {})
    scenario = env.ref("shopfloor_reception.scenario_reception")
    options = json.loads(scenario.options_edit)
    if "set_packaging_dimension" in options.keys():
        options.pop("set_packaging_dimension")
    scenario.options_edit = json.dumps(options)
