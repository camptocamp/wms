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
            <searchbar
                v-if="state_in(['select_document', 'select_line', 'set_quantity', 'set_destination'])"
                v-on:found="on_scan"
                :input_placeholder="search_input_placeholder"
            />
            <template v-if="state_is('set_lot')">
                <searchbar
                    v-on:found="on_scan_lot"
                    :input_placeholder="search_input_placeholder_lot"
                />
                <searchbar
                    v-on:found="on_scan_expiry"
                    :input_placeholder="search_input_placeholder_expiry"
                />
            </template>
            <template v-if="state_in(['select_line', 'set_lot', 'set_quantity', 'set_destination'])">
                <item-detail-card
                    :record="state.data.picking"
                    :options="operation_options()"
                    :card_color="utils.colors.color_for('screen_step_todo')"
                    :key="make_state_component_key(['reception-picking-item-detail', state.data.picking.id])"
                />
            </template>
            <template v-if="state_is('select_document') && visible_pickings">
                <searchbar
                    v-on:found="on_search"
                    :input_placeholder="filter_input_placeholder"
                    :autofocus="false"
                    clearable_input_type
                />
                <manual-select
                    class="with-progress-bar"
                    :records="visible_pickings"
                    :options="manual_select_options()"
                    v-on:select="on_select_document"
                    :key="make_state_component_key(['reception', 'manual-select'])"
                />
            </template>
            <template v-if="state_is('select_line')">
                <picking-summary
                    :record="state.data.picking"
                    :records_grouped="picking_summary_records_grouped(state.data.picking)"
                    :action_cancel_package_key="'package_dest'"
                    :list_options="picking_summary_options()"
                    :key="make_state_component_key(['picking-summary', 'detail-picking', state.data.picking.id])"
                />
                <div class="button-list button-vertical-list full">
                    <v-row align="center">
                        <v-col class="text-center" cols="12">
                            <btn-action @click="on_mark_done">Mark as Done</btn-action>
                        </v-col>
                    </v-row>
                    <v-row align="center">
                        <v-col class="text-center" cols="12">
                            <cancel-button v-on:cancel="on_cancel"/>
                        </v-col>
                    </v-row>
                </div>
            </template>
            <template v-if="state_is('set_lot')">
                <item-detail-card
                    :record="state.data.selected_move_lines[0].product"
                    :options="picking_detail_options()"
                    :card_color="utils.colors.color_for('screen_step_todo')"
                    :key="make_state_component_key(['reception-product-item-detail-set-lot', state.data.picking.id])"
                />
                <div class="button-list button-vertical-list full">
                    <v-row align="center">
                        <v-col class="text-center" cols="12">
                            <btn-action @click="on_confirm_action">Continue</btn-action>
                        </v-col>
                    </v-row>
                    <v-row align="center">
                        <v-col class="text-center" cols="12">
                            <btn-back/>
                        </v-col>
                    </v-row>
                </div>
            </template>
            <template v-if="state_is('set_quantity')">
                <item-detail-card
                    :record="state.data.selected_move_lines[0].product"
                    :options="picking_detail_extended_options()"
                    :card_color="utils.colors.color_for('screen_step_todo')"
                    :key="make_state_component_key(['reception-product-item-detail-set-quantity', state.data.picking.id])"
                />
                <div class="button-list button-vertical-list full">
                    <v-row align="center">
                        <v-col class="text-center" cols="12">
                            <btn-action @click="on_add_to_existing_pack">Existing pack</btn-action>
                        </v-col>
                    </v-row>
                    <v-row align="center">
                        <v-col class="text-center" cols="12">
                            <btn-action @click="on_create_new_pack">New pack</btn-action>
                        </v-col>
                    </v-row>
                    <v-row align="center">
                        <v-col class="text-center" cols="12">
                            <btn-action @click="on_process_without_pack">Process without pack</btn-action>
                        </v-col>
                    </v-row>
                    <v-row align="center">
                        <v-col class="text-center" cols="12">
                            <cancel-button v-on:cancel="on_cancel"/>
                        </v-col>
                    </v-row>
                </div>
            </template>
            <template v-if="state_is('set_destination')">

            </template>
        </Screen>
    `,
    computed: {
        visible_pickings: function () {
            return !_.isEmpty(this.filtered_pickings)
                ? this.filtered_pickings
                : this.state.data.pickings;
        },
        search_input_placeholder_lot: function () {
            return this.state.display_info.scan_input_placeholder_lot;
        },
        search_input_placeholder_expiry: function () {
            return this.state.display_info.scan_input_placeholder_expiry;
        },
    },
    methods: {
        manual_select_options: function () {
            return {
                show_title: false,
                showActions: false,
                group_title_default: "Pickings to process",
                group_color: this.utils.colors.color_for("screen_step_todo"),
                list_item_component: "list-item",
                list_item_extra_component: "picking-list-item-progress-bar",
                list_item_options: {
                    fields: [
                        {path: "carrier"},
                        {path: "origin", action_val_path: "name"},
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
        operation_options: function () {
            return {
                fields: [
                    {
                        path: "origin",
                        renderer: (rec, field) => {
                            return rec.origin + " - " + rec.partner.name;
                        },
                        action_val_path: "name",
                    },
                    {path: "carrier"},
                ],
            };
        },
        picking_detail_options: function () {
            return {
                fields: [
                    {path: "supplier_code", label: "Vendor code"},
                    {
                        path: "barcode",
                        label: "Product code",
                        action_val_path: "barcode",
                    },
                    {path: "lot", label: "Lot"},
                    // TODO: add scheduled date (not coming from backend)
                ],
            };
        },
        picking_detail_extended_options: function () {
            return {
                fields: [
                    {path: "supplier_code", label: "Vendor code"},
                    {
                        path: "barcode",
                        label: "Product code",
                        action_val_path: "barcode",
                    },
                    {path: "lot", label: "Lot"},
                    // TODO: we need only one line from the backend, instead of multiple lines?
                    // We need data on lot and shceduled date
                ],
            };
        },
        selected_lines_options: function () {
            return {
                card_klass: "loud-labels",
                key_title: "product.display_name",
                show_title: true,
                list_item_options: {
                    fields: [
                        {path: "product.barcode", label: "Product code"},
                        {path: "product.supplier_code", label: "Vendor code"},
                    ],
                },
            };
        },
        picking_summary_options: function () {
            return {
                list_item_options: {
                    actions: ["action_cancel_line"],
                    fields: [
                        {path: "product.name", label: "Product"},
                        {path: "product.barcode", label: "Product code"},
                        {path: "product.supplier_code", label: "Vendor code"},
                        {
                            path: "qty_done",
                            label: "Received qty",
                            display_no_value: true,
                            renderer: (rec, field) => {
                                return rec.qty_done ? rec.qty_done : "None";
                            },
                        },
                    ],
                    list_item_klass_maker: this.utils.wms.move_line_color_klass,
                },
            };
        },
        picking_summary_records_grouped: function (picking) {
            const self = this;
            return this.utils.wms.group_lines_by_product(picking.move_lines, {
                prepare_records: _.partialRight(
                    this.utils.wms.group_by_pack,
                    "product"
                ),
                group_color_maker: function (lines) {
                    return self.utils.wms.move_lines_completeness(lines) == 100
                        ? "screen_step_done"
                        : "screen_step_todo";
                },
            });
        },
        on_search: function (input) {
            this.filtered_pickings = this.state.data.pickings.filter((picking) =>
                this._apply_search_filter(picking, input.text)
            );
        },
        on_scan: function (scanned) {
            this.$root.trigger("scan", scanned.text);
        },
        on_scan_lot: function (scanned) {
            this.$root.trigger("scan_lot", scanned.text);
        },
        on_scan_expiry: function (scanned) {
            this.$root.trigger("scan_expiry", scanned.text);
        },
        on_select_document: function (selected) {
            this.$root.trigger("scan", selected.name);
        },
        on_mark_done: function () {
            this.$root.trigger("mark_as_done");
        },
        on_confirm_action: function () {
            this.$root.trigger("confirm_action");
        },
        on_add_to_existing_pack: function () {
            this.$root.trigger("add_to_existing_pack");
        },
        on_create_new_pack: function () {
            this.$root.trigger("create_new_pack");
        },
        on_process_without_pack: function () {
            this.$root.trigger("process_without_pack");
        },
        _apply_search_filter: function (picking, input) {
            const values = [picking.origin];
            return !_.isEmpty(values.find((v) => v.includes(input)));
        },
        _get_selected_line_ids: function (lines) {
            return lines.map(_.property("id"));
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
                        title: "Select a line",
                        scan_placeholder: "Scan product / package",
                    },
                    events: {
                        scan: "on_scan",
                        mark_as_done: "on_mark_as_done",
                        cancel_picking_line: "on_cancel",
                    },
                    on_scan: (barcode) => {
                        this.wait_call(
                            this.odoo.call("scan_line", {
                                picking_id: this.state.data.picking.id,
                                barcode,
                            })
                        );
                    },
                    on_mark_as_done: () => {
                        this.wait_call(
                            this.odoo.call("done_action", {
                                picking_id: this.state.data.picking.id,
                                confirmation: true,
                            })
                        );
                    },
                    on_cancel: () => {
                        // TODO: endpoint missing in backend
                        // this.wait_call(
                        //     this.odoo.call("cancel", {
                        //         package_level_id: this.state.data.id,
                        //     })
                        // );
                    },
                },
                set_lot: {
                    display_info: {
                        title: "Set lot",
                        scan_input_placeholder_lot: "Scan lot",
                        scan_input_placeholder_expiry: "Scan expiration date",
                    },
                    events: {
                        scan_lot: "on_scan_lot",
                        scan_expiry: "on_scan_expiry",
                        confirm_action: "on_confirm_action",
                    },
                    on_scan_lot: (barcode) => {
                        this.wait_call(
                            this.odoo.call("set_lot", {
                                picking_id: this.state.data.picking.id,
                                selected_line_ids: this._get_selected_line_ids(
                                    this.state.data.selected_move_lines
                                ),
                                lot_name: barcode,
                            })
                        );
                    },
                    on_scan_expiry: (expiration_date) => {
                        this.wait_call(
                            this.odoo.call("set_lot", {
                                picking_id: this.state.data.picking.id,
                                selected_line_ids: this._get_selected_line_ids(
                                    this.state.data.selected_move_lines
                                ),
                                expiration_date: expiration_date,
                            })
                        );
                    },
                    on_confirm_action: () => {
                        this.wait_call(
                            this.odoo.call("set_lot_confirm_action", {
                                picking_id: this.state.data.picking.id,
                                selected_line_ids: this._get_selected_line_ids(
                                    this.state.data.selected_move_lines
                                ),
                            })
                        );
                    },
                },
                set_quantity: {
                    display_info: {
                        title: "Set lot",
                        scan_placeholder:
                            "Scan document / product / package / location",
                    },
                    events: {
                        scan: "on_scan",
                        add_to_existing_pack: "on_add_to_existing_pack",
                        create_new_pack: "on_create_new_pack",
                        process_without_pack: "on_process_without_pack",
                    },
                    on_scan: (barcode) => {
                        this.wait_call(
                            this.odoo.call("set_quantity", {
                                // TODO: add quantity from qty-picker
                                picking_id: this.state.data.picking.id,
                                selected_line_ids: this._get_selected_line_ids(
                                    this.state.data.selected_move_lines
                                ),
                                barcode,
                                confirmation: true,
                            })
                        );
                    },
                    on_cancel: () => {
                        // TODO: endpoint missing in backend
                        // this.wait_call(
                        //     this.odoo.call("cancel", {
                        //         package_level_id: this.state.data.id,
                        //     })
                        // );
                    },
                    on_add_to_existing_pack: () => {
                        this.wait_call(
                            this.odoo.call("process_with_existing_pack", {
                                picking_id: this.state.data.picking.id,
                                selected_line_ids: this._get_selected_line_ids(
                                    this.state.data.selected_move_lines
                                ),
                            })
                        );
                    },
                    on_create_new_pack: () => {
                        this.wait_call(
                            this.odoo.call("process_with_new_pack", {
                                picking_id: this.state.data.picking.id,
                                selected_line_ids: this._get_selected_line_ids(
                                    this.state.data.selected_move_lines
                                ),
                            })
                        );
                    },
                    on_process_without_pack: () => {
                        this.wait_call(
                            this.odoo.call("process_without_pack", {
                                picking_id: this.state.data.picking.id,
                                selected_line_ids: this._get_selected_line_ids(
                                    this.state.data.selected_move_lines
                                ),
                            })
                        );
                    },
                },
                set_destination: {
                    display_info: {
                        title: "Set destination",
                        scan_placeholder: "Scan destination location",
                    },
                    events: {
                        scan: "on_scan",
                    },
                    on_scan: (location_id) => {
                        this.wait_call(
                            this.odoo.call("set_destination", {
                                // TODO: finish adding the expected arguments
                                picking_id: this.state.data.picking.id,
                                selected_line_ids: this._get_selected_line_ids(
                                    this.state.data.selected_move_lines
                                ),
                                location_id,
                                confirmation: true,
                            })
                        );
                    },
                },
                select_dest_package: {},
            },
            filter_input_placeholder: "Filter operations",
            filtered_pickings: [],
        };
    },
};

process_registry.add("reception", Reception);

export default Reception;

// TODO: handle all confirmations in the scenario
