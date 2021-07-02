/**
 * Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

import {ScenarioBaseMixin} from "/shopfloor_mobile_base/static/wms/src/scenario/mixins.js";
import {process_registry} from "/shopfloor_mobile_base/static/wms/src/services/process_registry.js";

const DeliveryShipment = {
    mixins: [ScenarioBaseMixin],
    template: `
        <Screen :screen_info="screen_info">
            <template v-slot:header>
                <state-display-info :info="state.display_info" v-if="state.display_info"/>
            </template>
            <searchbar
                v-if="state.on_scan"
                v-on:found="on_scan"
                :input_placeholder="search_input_placeholder"
                />

              <v-row align="center" justify="center" v-if="state_is('loading_list')">
                <v-col class="text-center" cols="12">
                <v-btn-toggle mandatory v-model="filter_state">
                  <v-btn color="success" value="lading">
                    Lading
                  </v-btn>
                  <v-btn color="warning" value="dock">
                    On Dock
                  </v-btn>
                </v-btn-toggle>
                </v-col>
              </v-row>

            <detail-picking
                v-if="state_is('loading_list')"
                v-for="picking in filter_pickings(pickings())"
                :record="picking"
                :options="{main: true, key_title: 'name', title_action_icon: 'mdi-help-circle', on_title_action: state.onBack2Picking, fields:[{path:'carrier.name', label: 'Carrier'}, {path:'move_line_count', label:'Lines'}]}"
                :key="make_component_key(['shipment-picking', picking.id])"
                :card_color="getOperationColor(picking)"
                />

            <item-detail-card
                v-if="!_.isEmpty(picking())"
                :key="make_state_component_key(['delivery-shipment-pick', picking().id])"
                :record="picking()"
                :options="{main: true, key_title: 'name', title_action_field: {path: 'name', action_val_path: 'name'}}"
                :card_color="utils.colors.color_for('screen_step_done')"
                />

            <item-detail-card
                v-if="state_is('scan_document')"
                :key="make_state_component_key(['delivery-shipment-shipment', shipment().id])"
                :record="shipment()"
                :options="{main: true, key_title: 'name', fields: [{path: 'dock.name', label: 'Dock'}]}"
                :card_color="utils.colors.color_for('screen_step_done')"
                />


            <div v-if="state_is('scan_document')" v-for="(value, name, index) in this.state.data.content">
                <v-card color="blue lighten-1" class="detail v-card mt-5 main">
                    <v-card-title>{{ name }}</v-card-title>
                </v-card>
                <item-detail-card
                    v-for="packlevel in value.package_levels"
                    :key="make_state_component_key(['shipment-pack', packlevel.id])"
                    :record="packlevel.package_src"
                    :options="getPackOptions(packlevel)"
                    :card_color="getPackColor(packlevel)"
                    />
                <item-detail-card
                    v-for="line in value.move_lines"
                    :key="make_state_component_key(['shipment-product', line.product.id])"
                    :record="line"
                    :options="getLineOptions(line)"
                    :card_color="getLineColor(line)"
                    />
            </div>

            <v-card color="warning" class="detail v-card main mb-2" v-if="state_is('validate')">
                <v-card-title>Are you sure you want to close the shipment ?</v-card-title>
            </v-card>
            <item-detail-card v-if="state_is('validate')"
                :key="make_state_component_key(['lading-detail', 123])"
                :record="state.data.lading"
                :card_color="getShipmentSummaryColor(state.data.lading)"
                :options="getShipmentSummary(state.data.lading)"
                >
                <template v-slot:title>
                        <span>Lading</span>
                </template>
            </item-detail-card>
            <item-detail-card v-if="state_is('validate')"
                :key="make_state_component_key(['dock-detail', 123])"
                :record="state.data.on_dock"
                :card_color="getShipmentSummaryColor(state.data.on_dock)"
                :options="getShipmentSummary(state.data.on_dock)"
                >
                <template v-slot:title>
                        <span>On Dock</span>
                </template>
            </item-detail-card>


            <div class="button-list button-vertical-list full" v-if="!state_is('scan_dock')">
                <v-row align="center" v-if="state_is('scan_document')">
                    <v-col class="text-center" cols="12">
                        <btn-action color="default" @click="state.on_go2loading_list">Shipment Advice</btn-action>
                    </v-col>
                </v-row>
                <v-row align="center" v-if="state_is('loading_list')">
                    <v-col class="text-center" cols="12">
                        <btn-action color="default" @click="state.on_close_shipment">Close Shipment</btn-action>
                    </v-col>
                </v-row>
                <v-row align="center" v-if="state_is('validate')">
                    <v-col class="text-center" cols="12">
                        <btn-action color="default" @click="state.on_confirm">Confirm</btn-action>
                    </v-col>
                </v-row>
                <v-row align="center">
                    <v-col class="text-center" cols="12">
                        <btn-action color="default" @click="state.on_back">{{ btnBackLabel() }}</btn-action>
                    </v-col>
                </v-row>
            </div>

        </Screen>
        `,
    methods: {
        screen_title: function() {
            if (_.isEmpty(this.state.data.shipment_advice)) {
                return this.menu_item().name;
            }
            return this.state.data.shipment_advice.name;
        },
        btnBackLabel: function() {
            return this.state.buttonBackLabel || "Back";
        },
        // The current picking
        picking: function() {
            if (_.isEmpty(this.state.data.picking)) {
                return {};
            }
            return this.state.data.picking;
        },
        pickings: function() {
            if (this.filter_state === "dock" && !_.isEmpty(this.state.data.on_dock)) {
                return this.state.data.on_dock;
            } else if (
                this.filter_state === "lading" &&
                !_.isEmpty(this.state.data.lading)
            ) {
                return this.state.data.lading;
            }
            return {};
        },
        filter_pickings: function(pickings) {
            let res = pickings;
            const nameFilter = this.state.data.filter_name;
            if (nameFilter) {
                res = _.filter(pickings, pick => {
                    return pick.name.indexOf(nameFilter) >= 0;
                });
            }
            return res;
        },
        shipment: function() {
            if (_.isEmpty(this.state.data.shipment_advice)) {
                return {};
            }
            return this.state.data.shipment_advice;
        },
        getPackOptions: function(pack) {
            const action = pack.is_done
                ? () => {
                      this.unloadPack(pack);
                  }
                : null;
            return {
                key_title: "name",
                on_title_action: action,
                title_action_icon: "mdi-upload",
            };
        },
        getPackColor: function(pack) {
            const color = pack.is_done ? "screen_step_done" : "screen_step_todo";
            return this.utils.colors.color_for(color);
        },
        getLineOptions: function(line) {
            const action =
                line.qty_done == line.quantity
                    ? () => {
                          this.unloadLine(line);
                      }
                    : null;
            return {
                // main: true,
                key_title: "product.display_name",
                on_title_action: action,
                title_action_icon: "mdi-upload",
                fields: [
                    {path: "lot.name", label: "Lot"},
                    {path: "quantity", label: "Qty"},
                ],
            };
        },
        getLineColor: function(line) {
            const color =
                line.qty_done >= line.quantity
                    ? "screen_step_done"
                    : "screen_step_todo";
            return this.utils.colors.color_for(color);
        },
        unloadLine: function(line) {
            this.wait_call(
                this.odoo.call("unload_move_line", {
                    shipment_advice_id: this.shipment().id,
                    move_line_id: line.id,
                })
            );
        },
        unloadPack: function(pack) {
            this.wait_call(
                this.odoo.call("unload_package_level", {
                    shipment_advice_id: this.shipment().id,
                    package_level_id: pack.id,
                })
            );
        },
        getOperationColor: function(pick) {
            var color = "";
            if (pick.is_fully_loaded) {
                color = "success";
            } else if (pick.is_partially_loaded) {
                color = "warning";
            } else {
                color = "error";
            }
            return this.utils.colors.color_for(color);
        },
        getShipmentSummary: function(data) {
            var fields = [
                {path: "pickings_count", label: "Deliveries", display_no_value: true},
                {path: "packages_count", label: "Package", display_no_value: true},
                {path: "bulk_lines_count", label: "Bulk moves", display_no_value: true},
            ];
            if ("total_load" in data) {
                fields.unshift({
                    path: "total_load",
                    renderer: () => {
                        return this.state.data.shipment_advice.dock.name;
                    },
                    label: "Loading dock",
                });
                fields.push({
                    path: "total_load",
                    label: "Total load (Kg)",
                    display_no_value: true,
                });
            }
            return {fields: fields};
        },
        getShipmentSummaryColor: function(data) {
            const isLading = "total_load" in data;
            var color = "";
            if (isLading) {
                //TODO need to know if planned or not
                color = "screen_step_done";
            } else {
                if (data.pickings_count > 0) {
                    color = "error";
                } else {
                    color = "success";
                }
            }
            return this.utils.colors.color_for(color);
        },
    },
    data: function() {
        const self = this;
        return {
            usage: "delivery_shipment",
            initial_state_key: "scan_dock",
            filter_state: "dock",
            states: {
                scan_dock: {
                    display_info: {
                        title: "Start by scanning a dock",
                        scan_placeholder: "Scan dock",
                    },
                    on_scan: scanned => {
                        this.wait_call(
                            this.odoo.call("scan_dock", {
                                barcode: scanned.text,
                            })
                        );
                    },
                },
                scan_document: {
                    display_info: {
                        title: "Scan some shipment's content",
                        scan_placeholder: () => {
                            if (_.isEmpty(this.picking())) {
                                return "Scan a lot, a pack or an operation";
                            } else {
                                return "Scan a lot, a product, a pack or an operation";
                            }
                        },
                    },
                    on_scan: scanned => {
                        this.wait_call(
                            this.odoo.call("scan_document", {
                                barcode: scanned.text,
                                shipment_advice_id: this.shipment().id,
                                picking_id: this.picking().id,
                            })
                        );
                    },
                    on_back: () => {
                        this.state_to("scan_dock");
                    },
                    on_go2loading_list: () => {
                        this.wait_call(
                            this.odoo.call("loading_list", {
                                shipment_advice_id: this.shipment().id,
                            })
                        );
                    },
                },
                loading_list: {
                    display_info: {
                        title: "Filter documents",
                        scan_placeholder: "Scan a document number",
                    },
                    on_scan: scanned => {
                        this.state_set_data({filter_name: scanned.text});
                    },
                    on_back: () => {
                        this.state_to("scan_document");
                    },
                    onBack2Picking: picking => {
                        this.wait_call(
                            this.odoo.call("scan_document", {
                                barcode: picking.name,
                                shipment_advice_id: this.shipment().id,
                            })
                        );
                    },
                    on_close_shipment: () => {
                        this.wait_call(
                            this.odoo.call("validate", {
                                shipment_advice_id: this.shipment().id,
                            })
                        );
                    },
                },
                validate: {
                    display_info: {
                        title: "Shipment closure confirmation",
                    },
                    buttonBackLabel: "Cancel",
                    on_back: () => {
                        this.wait_call(
                            this.odoo.call("loading_list", {
                                shipment_advice_id: this.shipment().id,
                            })
                        );
                    },
                    on_confirm: () => {
                        this.wait_call(
                            this.odoo.call("validate", {
                                shipment_advice_id: this.shipment().id,
                                confirm: true,
                            })
                        );
                    },
                },
            },
        };
    },
};

process_registry.add("delivery_shipment", DeliveryShipment);

export default DeliveryShipment;
