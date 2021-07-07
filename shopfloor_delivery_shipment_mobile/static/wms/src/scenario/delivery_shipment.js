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

            <v-card-text class="full" v-if="state_is('loading_list')">
              <v-row align="center" justify="center" >
                <v-col class="text-center" cols="12">
                <v-btn-toggle v-model="filter_state">
                  <v-btn color="default" value="lading">
                    Lading
                  </v-btn>
                  <v-btn color="warning" value="dock">
                    On Dock
                  </v-btn>
                </v-btn-toggle>
                </v-col>
              </v-row>
            </v-card-text>
            <div v-if="state_is('loading_list')">
            filtering on {{ filter_state }} and {{ this.state.data.filter_name}}
            </div>

            <detail-picking
                v-if="state_is('loading_list')"
                v-for="picking in filter_pickings(pickings())"
                :record="picking"
                :key="make_component_key(['picking', picking.id])"
                />


            <item-detail-card
                v-if="!_.isEmpty(picking())"
                :key="make_state_component_key(['delivery-shipment-pick', picking().id])"
                :record="picking()"
                :options="{main: true, key_title: 'name', title_action_field: {action_val_path: 'barcode'}}"
                :card_color="utils.colors.color_for('screen_step_done')"
                />
            <item-detail-card
                v-if="state_in(['scan_document'])"
                :key="make_state_component_key(['delivery-shipment-shipment', shipment().id])"
                :record="shipment()"
                :options="{main: true, key_title: 'name', title_action_field: {action_val_path: 'barcode'}, fields: [{path: 'dock.name', label: 'Dock'}]}"
                :card_color="utils.colors.color_for('screen_step_done')"
                />

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
                <v-row align="center" v-if="state_is('validate_shipment')">
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
            if (_.isEmpty(this.state.data.picking)) {
                return this.menu_item().name;
            }
            return this.state.data.picking.name;
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
        // All pickings in the shipment advice
        pickings: function() {
            if (_.isEmpty(this.state.data.shipment_advice)){
                return {};
            }
            if (_.isEmpty(this.state.data.shipment_advice.pickings)){
                return {};
            }
            return this.state.data.shipment_advice.pickings;
        },
        filter_pickings: function(pickings) {
            let res = pickings;
            const nameFilter =  this.state.data.filter_name;
            let stateFilter = [];
            if (this.filter_state === "dock"){
                stateFilter = ["all", "partial"]
            } else if (this.filter_state === "lading") {
                stateFilter = ["none"]
            }
            if (nameFilter) {
                res = _.filter(pickings, (pick) => {return pick.name.indexOf(nameFilter) >= 0;});
            }
            if (stateFilter.length){
                res = _.filter(res, (pick) => {return stateFilter.includes(pick.load_state);})
            }
            return res;

        },
        shipment: function() {
            if (_.isEmpty(this.state.data.shipment_advice)) {
                return {};
            }
            return this.state.data.shipment_advice;
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
                        scan_placeholder:
                            "Scan a lot, a product, a pack or an operation",
                    },
                    on_scan: scanned => {
                        this.wait_call(
                            this.odoo.call("scan_document", {
                                barcode: scanned.text,
                                shipment_advice_id: this.shipment().id,
                                // picking_id
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
                        // this.state_to("loading_list");
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
                    on_close_shipment: () => {
                        this.state_to("validate_shipment");
                    },
                    on_filter_lading:() => {
                        // this.state_set_data({filter_state: "lading"});
                    },
                    on_filter_dock:() => {
                        // this.state_set_data({filter_state: "dock"});
                    },
                },
                validate_shipment: {
                    display_info: {
                        title: "Shipment closure confirmation",
                    },
                    buttonBackLabel: "Cancel",
                    on_back: () => {
                        this.state_to("loading_list");
                    },
                    on_confirm: () => {
                        this.wait_call(
                            this.odoo.call("validate_shipment", {
                                shipment_advice_id: this.shipment().id,
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
