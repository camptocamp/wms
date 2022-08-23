/**
 * Copyright 2022 Camptocamp SA (http://www.camptocamp.com)
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
 */

import {ScenarioBaseMixin} from "/shopfloor_mobile_base/static/wms/src/scenario/mixins.js";
import {process_registry} from "/shopfloor_mobile_base/static/wms/src/services/process_registry.js";

const Reception = {
    mixins: [ScenarioBaseMixin],
    template: `
        <Screen :screen_info="screen_info">
            <template v-slot:header>
                <state-display-info :info="state.display_info" v-if="state.display_info"/>
            </template>
            <template v-if="state_is('select_document') && visible_pickings">
                <searchbar
                    v-on:found="on_scan"
                    :input_placeholder="search_input_placeholder"
                />
                <searchbar
                    v-on:found="on_search"
                    :input_placeholder="filter_input_placeholder"
                />
                <manual-select
                    class="with-progress-bar"
                    :records="visible_pickings"
                    :options="manual_select_options()"
                    :key="make_state_component_key(['reception', 'manual-select'])"
                />
            </template>
            <template v-if="state_in[('select_line', 'set_lot')]">
                <item-detail-card
                    :key="make_state_component_key(['reception-picking-item-detail', state.data.picking.id])"
                    :record="state.data.picking"
                    :options="opts_for_operation()"
                    :card_color="utils.colors.color_for(state_in(['scan_destination', 'scan_destination_all']) ? 'screen_step_done': 'screen_step_todo')"
                />
            </template>
        </Screen>
    `,
    computed: {
        visible_pickings: function () {
            return !_.isEmpty(this.filtered_pickings)
                ? this.filtered_pickings
                : this.state.data.pickings;
        },
    },
    methods: {
        manual_select_options: function () {
            return {
                show_title: false,
                showActions: false,
                group_title_default: "Pickings to process",
                group_color: this.utils.colors.color_for("screen_step_todo"),
                list_item_component: "detail-picking-select",
                // list_item_extra_component: "picking-list-item-progress-bar",
                list_item_options: {
                    fields: [
                        {path: "carrier"},
                        {path: "origin"},
                        {
                            path: "scheduled_date",
                            renderer: (rec, field) => {
                                return this.utils.display.render_field_date(rec, field);
                            },
                        },
                    ],
                },
            };
        },
        opts_for_operation: function () {
            return {
                fields: [
                    {path: "name"},
                    {
                        path: "origin",
                        renderer: (rec, field) => {
                            return rec.origin + " - " + rec.partner.name;
                        },
                    },
                    {path: "carrier"},
                ],
            };
        },
        on_search: function (input) {
            this.filtered_pickings = this.state.data.pickings.filter((picking) =>
                this._apply_search_filter(picking, input.text)
            );
        },
        on_scan: function (scanned) {
            this.$root.trigger("scan", scanned.text);
        },
        select_document: function (selected) {
            this.$root.trigger("scan", selected.name);
        },
        display_product_info: function (selected) {
            debugger;
        },
        _apply_search_filter: function (picking, input) {
            const values = [picking.origin];
            return !_.isEmpty(values.find((v) => v.includes(input)));
        },
    },
    data: function () {
        return {
            usage: "reception",
            initial_state_key: "select_document",
            states: {
                init: {
                    enter: () => {
                        this.wait_call(this.odoo.call("start"));
                    },
                },
                select_document: {
                    display_info: {
                        title: "Choose an operation",
                        scan_placeholder: "Scan document / product / package",
                    },
                    events: {
                        scan: "on_scan",
                    },
                    on_scan: (barcode) => {
                        this.wait_call(
                            this.odoo.call("scan_document", {
                                barcode,
                            })
                        );
                    },
                },
                select_line: {
                    display_info: {
                        title: "Choose an operation",
                        scan_placeholder: "Scan document / product / package",
                    },
                },
                set_lot: {},
                set_quantity: {},
                set_destination: {},
                select_dest_package: {},
            },
            filter_input_placeholder: "Filter operations",
            filtered_pickings: [],
        };
    },
};

process_registry.add("reception", Reception);

export default Reception;
