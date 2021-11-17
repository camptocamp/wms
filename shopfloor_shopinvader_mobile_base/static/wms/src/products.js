/**
 * Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
 * @author Simone Orsi <simone.orsi@camptocamp.com>
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

import {process_registry} from "/shopfloor_mobile_base/static/wms/src/services/process_registry.js";

const Products = {
    template: `
        <Screen :screen_info="screen_info">
            <searchbar
                v-on:found="on_scan"
                :input_placeholder="search_input_placeholder"
                />
            <manual-select
                v-if="_.isEmpty(current_product)"
                :records="products"
                :key="make_component_key(['manual-select'])"
                :options="{showActions: false}"
                v-on:select="view_product"
                />

            <item-detail-card
                v-if="!_.isEmpty(current_product)"
                :card_color="utils.colors.color_for('screen_step_todo')"
                :record="current_product"
                :options="{main: true, loud: true, fields: product_detail_fields()}"
                />
        </Screen>
    `,
    data: function () {
        return {
            products: [],
            current_product: {},
            user_message: {},
            search_input_placeholder: this.$t("screen.scan_anything.scan_placeholder"),
        };
    },
    mounted() {
        const odoo_params = {
            base_url: this.$root.app_info.shop_api_route,
            usage: "products",
        };
        this.odoo = this.$root.getOdoo(odoo_params);
        this._fetch(this.$route.params.identifier);
    },
    beforeRouteUpdate(to, from, next) {
        if (to.params.identifier) {
            this._load_product(to.params.identifier);
        }
        next();
    },
    methods: {
        on_reset: function (e) {
            this.$router.push({name: "products", params: {identifier: undefined}});
        },
        // TODO: fetch should be done from the sync service.
        // We should pick product from the local storage instead.
        _fetch: function (identifier) {
            const params = {};
            const self = this;
            this.odoo.get("search", params).then((result) => {
                this.$set(this, "products", result.data || {});
                if (identifier) {
                    this._load_product(identifier);
                }
                this.user_message = result.message || null;
            });
        },
        _load_product: function (identifier) {
            const product = _.find(this.products, ["sku", identifier]);
            this.$set(this, "current_product", product);
        },
        view_product: function (product) {
            this.$router.push({name: "products", params: {identifier: product.sku}});
        },
        product_detail_fields: function () {
            return [
                {path: "name", klass: "loud"},
                {path: "description", label: "Description"},
            ];
        },

        on_scan: function (scanned) {
            this.$router.push({
                name: "products",
                params: {identifier: scanned.text},
            });
        },
    },
    computed: {
        screen_info: function () {
            return {
                title: this.screen_title,
                klass: "shop products",
                user_message: this.user_message,
            };
        },
        screen_title: function () {
            return this.$t("screen.products.title", {
                what: this.$route.params.identifier,
            });
        },
    },
};

process_registry.add(
    "products",
    Products,
    {
        path: "/products/:identifier?",
    },
    {
        menu: {
            _type: "all",
            name: "Catalog",
            id: "catalog",
            to: {
                name: "products",
                params: {},
            },
        },
    }
);

export default Products;
