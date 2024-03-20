/**
 * Copyright 2024 Camptocamp SA (http://www.camptocamp.com)
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

import {process_registry} from "/shopfloor_mobile_base/static/wms/src/services/process_registry.js";

// stock_picking_partner_note makes the 'note' field in pickings an HTML field,
// which means that we need to display the note as HTML in the shopfloor frontend as well.
const checkout_scenario = process_registry.get("checkout");
const template = checkout_scenario.component.template;
const new_template = template.replace(
    'v-text="state.data.picking.note"',
    'v-html="state.data.picking.note"'
);

const CheckoutStockPickingPartnerNote = process_registry.extend("checkout", {
    template: new_template,
});

process_registry.replace("checkout", CheckoutStockPickingPartnerNote);
