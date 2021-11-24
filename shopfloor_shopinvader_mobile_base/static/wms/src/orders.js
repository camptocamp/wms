import {process_registry} from "/shopfloor_mobile_base/static/wms/src/services/process_registry.js";
import {translation_registry} from "/shopfloor_mobile_base/static/wms/src/services/translation_registry.js";

import store from "./store/index.js";

import OrderModule from "./store/modules/order_store.js";

const orders_module = new OrderModule();
store.registerModule("orders_module", orders_module);

const Orders = {
    template: `
    <Screen :screen_info="screen_info">
        <v-list v-if="_.isEmpty(current_order)">
            <v-list-item
                v-for="order in orders"
                :key="order.id"
                class="order-list"
                @click="view_order(order)"
            >
                <v-list-item-content>
                    <v-list-item-title>Order {{ order.name}} </v-list-item-title>
                    <v-list-item-subtitle>{{ format_date(order.date) }}</v-list-item-subtitle>
                    <v-list-item-subtitle>Products purchased: {{ order.lines.items.length }}</v-list-item-subtitle>
                    <v-list-item-subtitle>Total number of units purchased: {{ calculate_items(order) }}</v-list-item-subtitle>
                </v-list-item-content>
            </v-list-item>
        </v-list>
        <v-card v-if="!_.isEmpty(current_order)">
            <v-toolbar
            color="white"
            v-on:click="to_orders"
            >
                <v-icon>mdi-arrow-left</v-icon>
                <v-toolbar-items class="add-another-product">{{$t("screen.orders.back_to_orders")}}</v-toolbar-items>
            </v-toolbar>
            <v-card class="order-card">
                <div class="order-header">
                    <h1> Order {{ current_order.name }} </h1>
                </div>
                <v-list>
                    <v-list-item-content dense>
                        <div
                            v-for="item in current_order.lines.items"
                            class="order-content"
                        >
                            <h2>{{ item.product.name }}</h2>
                            <p>Price: {{ item.amount.price }}</p>
                            <p> Quantity: {{ item.qty }}</p>
                            <h3> Total: {{ item.amount.total }}</h3>
                        </v-list-item>
                    </v-list-item-content>
                </v-list>
            </v-card>
        </v-card>
    </Screen>
    `,
    data: function () {
        return {
            current_order: {},
        };
    },
    mounted() {
        const odoo_params = {
            base_url: this.$root.app_info.shop_api_route,
            usage: "sales",
        };
        this.odoo = this.$root.getOdoo(odoo_params);
        this._fetch(this.$route.params.identifier);
    },
    beforeRouteUpdate(to, from, next) {
        if (to.params.identifier) {
            this._load_order(to.params.identifier);
        }
        next();
    },
    methods: {
        _fetch: function (identifier) {
            const params = {};
            const self = this;
            this.odoo.get("search", params).then((result) => {
                this.$store.commit("orders_loadOrders", result.data);
                if (identifier) {
                    this._load_order(identifier);
                }
            });
        },
        format_date: function (date) {
            const split_date = date.split("T");
            return split_date[0] + " - " + split_date[1];
        },
        calculate_items: function (order) {
            return order.lines.items.reduce((acc, next) => {
                return acc + next.qty;
            }, 0);
        },
        _load_order: function (identifier) {
            const order = _.find(this.orders, ["name", identifier]);
            this.$set(this, "current_order", order);
        },
        view_order: function (order) {
            this.$router.push({name: "orders", params: {identifier: order.name}});
        },
        to_orders: function (e) {
            this.current_order = {};
            this.$router.push({name: "orders", params: {identifier: undefined}});
        },
    },
    computed: {
        orders: function () {
            return this.$store.state.orders_module.orders;
        },
        screen_info: function () {
            return {
                title: this.screen_title,
                klass: "shop orders",
            };
        },
        screen_title: function () {
            return this.$t("screen.orders.title");
        },
    },
};

translation_registry.add("en-US.screen.orders.title", "Orders");
translation_registry.add("fr-FR.screen.orders.title", "Commandes");
translation_registry.add("de-DE.screen.orders.title", "Bestellungen");

translation_registry.add("en-US.screen.orders.back_to_orders", "Back to orders");
translation_registry.add("fr-FR.screen.orders.back_to_orders", "Vers vos ordres");
translation_registry.add(
    "de-DE.screen.orders.back_to_orders",
    "Zurück zu Bestellungen"
);

process_registry.add(
    "orders",
    Orders,
    {
        path: "/orders/:identifier?",
    },
    {
        menu: {
            _type: "all",
            name: "Orders",
            id: "order",
            to: {
                name: "orders",
            },
        },
    }
);
