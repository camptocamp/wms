/**
 * Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
 * @author Simone Orsi <simone.orsi@camptocamp.com>
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

import store from "/shopfloor_mobile_base/static/wms/src/store/index.js";

import CartModule from "./store/modules/cart_store.js";
import {translation_registry} from "/shopfloor_mobile_base/static/wms/src/services/translation_registry.js";

const cart_module = new CartModule();
store.registerModule("cart_module", cart_module);

import {process_registry} from "/shopfloor_mobile_base/static/wms/src/services/process_registry.js";

const Cart = {
    template: `
        <Screen :screen_info="screen_info">
            <v-card v-if="has_cart" class="mx-auto" max-width="85%">
                <cart-list
                    :records="cart.lines.items"
                    :toProducts="to_products"
                    :key="make_component_key(['cart-list'])"
                />
                <v-card color="secondary">
                    <v-card-title class="total-cart">{{$t("screen.cart.total_in_cart")}}: {{ cart.amount.total.toFixed(2) }}</v-card-title>
                </v-card>
                <v-card color="primary">
                    <v-card-title class="to-checkout" v-on:click="checkout">{{$t("screen.cart.checkout")}}</v-card-title>
                </v-card>
            </v-card>
            <div class="on-checkout" v-if="!has_cart && !checkout_success && !checkout_failure">
                <h3>The cart is empty</h3>
                <div>
                    <btn-action color="primary" v-on:click="to_products">NEW PURCHASE</btn-action>
                </div>
            </div>
            <div class="on-checkout" v-if="checkout_success">
                <h3>Checkout successful!</h3>
                <div>
                    <btn-action color="primary" v-on:click="to_products">NEW PURCHASE</btn-action>
                    <btn-action color="primary" v-on:click="to_orders">ORDERS</btn-action>
                </div>
            </div>
            <h3 v-if="checkout_failure">Something went wrong with checkout...</h3>
        </Screen>
    `,
    data: function () {
        return {
            has_cart: false,
            checkout_success: false,
            checkout_failure: false,
        };
    },
    mounted() {
        this.initialize_cart();
    },
    updated() {
        const cart_lines = this.$store.state.cart_module.cart.lines;
        if (_.isEmpty(cart_lines.items)) {
            this.has_cart = false;
        }
    },
    methods: {
        initialize_cart: function () {
            // TODO: if we want the cart to persist between sessions, should it go to localStorage?
            const cart = this.utils.cart.get_cart();

            if (cart) {
                this.$store.commit("cart_loadCart", cart);
                this.has_cart = true;
            }
        },
        get_odoo: function () {
            const odoo_params = {
                base_url: this.$root.app_info.shop_api_route,
                usage: "cart",
                headers: {},
            };

            if (!_.isEmpty(this.cart)) {
                odoo_params.headers["SESS-CART-ID"] = this.cart.id;
            }

            return this.$root.getOdoo(odoo_params);
        },
        to_products: function () {
            this.$router.push({name: "products"});
        },
        to_orders: function () {
            this.$router.push({name: "orders"});
        },
        checkout: function () {
            // TODO: Update this once the backend is updated
            // and doesn't require adding one line at a time.
            // At the moment the checkout button only updates
            // the UI, and it's for the rest of the app to send calls
            // to the backend.
            this.has_cart = false;
            this.checkout_success = true;
            this.utils.cart.remove_cart();
        },
    },
    computed: {
        cart: function () {
            return this.$store.state.cart_module.cart;
        },
        screen_info: function () {
            return {
                title: this.screen_title,
                klass: "shop cart",
            };
        },
        screen_title: function () {
            return this.$t("screen.cart.title");
        },
    },
};

process_registry.add(
    "cart",
    Cart,
    {
        path: "/cart",
    },
    {
        menu: {
            _type: "all",
            name: "Cart",
            id: "cart",
            to: {
                name: "cart",
            },
        },
    }
);

translation_registry.add("en-US.screen.cart.title", "Cart");
translation_registry.add("fr-FR.screen.cart.title", "Panier");
translation_registry.add("de-DE.screen.cart.title", "Warenkorb");

translation_registry.add("en-US.screen.cart.total_in_cart", "Total in cart");
translation_registry.add("fr-FR.screen.cart.total_in_cart", "Total dans le panier");
translation_registry.add("de-DE.screen.cart.total_in_cart", "Gesamt im Warenkorb");

translation_registry.add("en-US.screen.cart.checkout", "CHECKOUT");
translation_registry.add("fr-FR.screen.cart.checkout", "COMMANDER");
translation_registry.add("de-DE.screen.cart.checkout", "BESTELLEN");

export default Cart;
