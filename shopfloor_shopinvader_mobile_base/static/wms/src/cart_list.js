/**
 * Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
 * @author Simone Orsi <simahawk@gmail.com>
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

import {translation_registry} from "/shopfloor_mobile_base/static/wms/src/services/translation_registry.js";

Vue.component("cart-list", {
    props: ["records", "toProducts"],
    template: `
        <v-card
            class="mx-auto"
        >
        <v-toolbar
        color="white"
        v-on:click="toProducts"
        >
            <v-icon>mdi-arrow-left</v-icon>
            <v-toolbar-items class="add-another-product">{{$t("screen.cart.add_another_product")}}</v-toolbar-items>
        </v-toolbar>

        <v-list>
            <div v-for="(record, index) in records" class="cart-list">
                <v-list-item-content>
                    <v-list-item-title class="cart-list-title">{{record.product.name}}</v-list-item-title>
                    <v-list-item-content>Unit Price: {{record.product.price.default.value.toFixed(2)}}</v-list-item-content>
                    <v-list-item class="cart-quantity">Quantity:
                        {{record.qty}}
                        <div class="cart-quantity-button">
                            <v-btn
                            v-on:click="removeOne(record)"
                            >
                                <v-icon color="primary">
                                    mdi-minus
                                </v-icon>
                            </v-btn>
                            <v-btn
                            v-on:click="addOne(record)"
                            >
                            <v-icon color="primary">
                                mdi-plus
                            </v-icon>
                        </v-btn>
                        </div>
                    </v-list-item>
                    <v-list-item-content style="font-weight: bold;">Total: {{record.total.toFixed(2)}}</v-list-item-content>
                </v-list-item-content>
            </div>
        </v-list>
    </v-card>
    `,
    mounted() {
        const cart = this.utils.cart.get_cart();

        const odoo_params = {
            base_url: this.$root.app_info.shop_api_route,
            usage: "cart",
            headers: {"SESS-CART-ID": cart.id},
        };

        this.odoo = this.$root.getOdoo(odoo_params);
    },
    methods: {
        addOne: function (record) {
            const self = this;
            this.odoo
                .call("add_item", {
                    params: {product_id: record.product.id, item_qty: 1},
                })
                .then(function (result) {
                    self.$store.commit("cart_addOneUnit", record);
                })
                .catch(function (error) {
                    // TODO: add error handling
                });
        },
        removeOne: function (record) {
            const self = this;
            const params = {item_id: record.product.id};
            let endpoint_to_call = "delete_item";

            const new_qty = record.qty - 1;

            if (new_qty > 0) {
                endpoint_to_call = "update_item";
                params["item_qty"] = new_qty;
            }

            this.odoo
                .call(endpoint_to_call, {params: params})
                .then(function (result) {
                    self.$store.commit("cart_removeOneUnit", record);
                })
                .catch(function (error) {
                    // TODO: add error handling
                });
        },
    },
});

translation_registry.add(
    "en-US.screen.cart.add_another_product",
    "Add another product"
);
translation_registry.add(
    "fr-FR.screen.cart.add_another_product",
    "Ajouter un nouveau produit"
);
translation_registry.add(
    "de-DE.screen.cart.add_another_product",
    "Neues Produkt hinzufügen"
);
