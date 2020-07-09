# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models


class StockLocationStorageBuffer(models.Model):
    _name = "stock.location.storage.buffer"
    _description = "Location Storage Buffer"

    MAX_LOCATIONS_IN_NAME_GET = 3
    MAX_LOCATIONS_IN_HELP = 10

    buffer_location_ids = fields.Many2many(
        comodel_name="stock.location",
        relation="stock_location_storage_buffer_stock_location_buffer_rel",
        required=True,
        help="Buffers where goods are temporarily stored. When all these "
        "locations contain goods or will receive goods,"
        " the destination locations are not available for putaway.",
    )
    location_ids = fields.Many2many(
        comodel_name="stock.location",
        relation="stock_location_storage_buffer_stock_location_rel",
        required=True,
        help="Destination locations (including sublocations) that will be"
        " unreachable for putaway if the buffers are full.",
    )
    help_message = fields.Html(compute="_compute_help_message")
    active = fields.Boolean(default=True)

    @api.depends("buffer_location_ids", "location_ids")
    def _compute_help_message(self):
        """Generate a description of the storage buffer for humans"""
        for record in self:
            if not (record.buffer_location_ids and record.location_ids):
                record.help_message = _(
                    "<p>Select buffer locations and locations "
                    "blocked for putaways when the buffer locations "
                    "already contain goods or have move lines "
                    "reaching them.</p>"
                )
                continue

            record.help_message = record._help_message()

    def buffers_have_capacity(self):
        self.ensure_one()
        buffer_locations = self.buffer_location_ids.leaf_location_ids
        return any(location.location_is_empty for location in buffer_locations)

    def _help_message(self):
        buffer_locations = self.buffer_location_ids.leaf_location_ids
        buffer_location_count = len(buffer_locations)
        leaf_locations = self.location_ids.leaf_location_ids
        leaf_location_count = len(leaf_locations)

        message = "<p>The buffer locations:<ul><br/>"

        other_locs_template = _("<li>... and {} other locations.</li>")

        for idx, location in enumerate(buffer_locations):
            if idx == self.MAX_LOCATIONS_IN_HELP:
                message += other_locs_template.format(
                    buffer_location_count - self.MAX_LOCATIONS_IN_HELP
                )
                break
            message += "<li>{}</li>".format(location.display_name)

        buffers_have_capacity = self.buffers_have_capacity()

        if buffers_have_capacity:
            message += _(
                "</ul>currently <strong>have capacity</strong>,"
                " so the following locations "
                "<strong>can receive putaways</strong>:<ul><br/>"
            )
        else:
            message += _(
                "</ul>currently <strong>have no capacity</strong>,"
                " so the following locations  "
                "<strong>cannot receive putaways</strong>:<ul><br/>"
            )

        for idx, location in enumerate(leaf_locations):
            if idx == self.MAX_LOCATIONS_IN_HELP:
                message += other_locs_template.format(
                    leaf_location_count - self.MAX_LOCATIONS_IN_HELP
                )
                break
            message += "<li>{}</li>".format(location.display_name)

        message += "</ul></p>"

        if not buffers_have_capacity:
            message += _(
                "<p>The buffers have no capacity because they all contain"
                " goods or will contain goods due to move lines reaching them.</p>"
            )
        return message

    def name_get(self):
        result = []
        for record in self:
            name = ", ".join(
                self.buffer_location_ids[: self.MAX_LOCATIONS_IN_NAME_GET].mapped(
                    "name"
                )
            )
            if len(self.buffer_location_ids) > self.MAX_LOCATIONS_IN_NAME_GET:
                name += ", ..."
            result.append((record.id, name))
        return result
