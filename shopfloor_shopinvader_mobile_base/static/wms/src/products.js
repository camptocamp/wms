/**
 * Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
 * @author Simone Orsi <simone.orsi@camptocamp.com>
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

import {process_registry} from "/shopfloor_mobile_base/static/wms/src/services/process_registry.js";
import {translation_registry} from "/shopfloor_mobile_base/static/wms/src/services/translation_registry.js";
import ProductModule from "./store/modules/product_store.js";
import store from "/shopfloor_mobile_base/static/wms/src/store/index.js";

const products_module = new ProductModule();
store.registerModule("products_module", products_module);

// TODO: add pagination for products (currently showing only 1 page of 10 items by default)
// TODO: add images to detail and list

const Products = {
    template: `
        <Screen :screen_info="screen_info">
            <searchbar
                v-on:found="on_search"
                :input_placeholder="$t('screen.products.search')"
            />
            <span v-if="filter_text">Searching for "{{filter_text}}"</span>
            <v-btn
                color="secondary"
                class="remove-filter"
                v-if="filter_text"
                v-on:click="remove_filter"
            >
                {{$t('screen.products.remove_filter')}}
            </v-btn>
            <v-container fluid v-if="products && _.isEmpty(current_product)">
                <v-row dense>
                    <v-col
                        v-for="record in show_products()"
                        :key="record.id"
                        :cols="12"
                        :sm="6"
                    >
                        <v-card data-id="{{ record.id }}" >
                            <v-img
                                class="white--text align-end"
                                height="200px"
                                src="https://via.placeholder.com/200"
                                @click="view_product(record)"
                            >
                                <v-card-title>{{ record.name }}</v-card-title>
                            </v-img>
                            <v-card-subtitle class="product-price">Price: <span> {{record.price.default.value.toFixed(2)}}</span> </v-card-subtitle>
                            <v-card-actions>
                                <v-spacer></v-spacer>
                                <v-btn color="primary" v-on:click="add_to_cart(record)">
                                    {{$t("screen.products.add_to_cart")}}
                                </v-btn>
                            </v-card-actions>
                        </v-card>
                    </v-col>
                </v-row>
            </v-container>

            <v-card
            class="mx-auto"
            v-if="!_.isEmpty(current_product)"
            >
                <v-toolbar
                color="white"
                v-on:click="to_catalog"
                class="back-to-catalog"
                >
                    <v-icon>mdi-arrow-left</v-icon>
                    <v-toolbar-items class="add-another-product">
                        {{$t("screen.products.back_to_catalog")}}
                    </v-toolbar-items>
                </v-toolbar>
                <v-img
                    height="400px"
                    class="white--text align-end"
                    src="https://via.placeholder.com/400"
                >
                </v-img>
                <v-card-title>{{current_product.name}}</v-card-title>
                <v-card-text class="text--primary">
                    <div>{{current_product.meta_description || description_lipsum}}</div>
                </v-card-text>
                <v-card-subtitle class="product-price">Price: <span> {{current_product.price.default.value.toFixed(2)}}</span> </v-card-subtitle>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="primary" v-on:click="add_to_cart(current_product)">
                        {{$t("screen.products.add_to_cart")}}
                    </v-btn>
                </v-card-actions>
            </v-card>
        </Screen>
    `,
    data: function () {
        return {
            current_product: {},
            has_filter: false,
            filter_text: "",
            filtered_products: [],
            // TODO: Delete once the backend provides a product description.
            description_lipsum:
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
        };
    },
    mounted() {
        const cart = this.utils.cart.get_cart();
        if (cart) {
            this.$store.commit("cart_loadCart", cart);
        }
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
        to_catalog: function () {
            this.current_product = {};
            this.$router.push({name: "products", params: {identifier: undefined}});
        },
        // TODO: fetch should be done from the sync service.
        // We should pick product from the local storage instead.
        _fetch: function (identifier) {
            const params = {};
            const self = this;
            this.odoo.get("search", params).then((result) => {
                this.$store.commit("products_loadProducts", result.data);
                if (identifier) {
                    this._load_product(identifier);
                }
            });
        },
        _load_product: function (identifier) {
            const product = _.find(this.products, ["sku", identifier]);
            this.$set(this, "current_product", product);
        },
        view_product: function (product) {
            this.$router.push({name: "products", params: {identifier: product.sku}});
        },
        show_products: function () {
            if (this.has_filter) {
                return this.filtered_products;
            } else {
                return this.products;
            }
        },
        on_search: function (input) {
            if (_.isEmpty(input.text)) {
                this.remove_filter();
            } else {
                this.has_filter = true;
                this.filter_text = input.text;
                this.filtered_products = this.products.filter((product) => {
                    return product.name
                        .toLowerCase()
                        .includes(input.text.toLowerCase());
                });
            }
        },
        remove_filter: function () {
            this.has_filter = false;
            this.filter_text = "";
            this.filtered_products = [];
        },
        add_to_cart: function (record) {
            // TODO: Create utils for cart.
            const cart = this.utils.cart.get_cart();
            const has_cart = !_.isEmpty(cart);

            const self = this;
            const odoo_params = {
                base_url: this.$root.app_info.shop_api_route,
                usage: "cart",
                headers: {},
            };

            if (has_cart) {
                odoo_params.headers["SESS-CART-ID"] = cart.id;
            }

            // TODO: update this once the backend accepts
            // retrieving cart data. At the moment
            // it is necessary to initialize a cart.

            const odoo = this.$root.getOdoo(odoo_params);

            odoo.post("add_item", {
                params: {product_id: record.id, item_qty: 1},
            }).then(function (result) {
                if (!has_cart) {
                    result.data.lines.items[0] = {
                        product: result.data.lines.items[0].product,
                        total: result.data.lines.items[0].product.price.default.value,
                        qty: 1,
                    };
                    self.$store.commit("cart_loadCart", result.data);
                } else {
                    self.$store.commit("cart_addItemToCart", record);
                }
            });
        },
    },
    computed: {
        products: function () {
            return this.$store.state.products_module.products;
        },
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

translation_registry.add("en-US.screen.products.title", "Products");
translation_registry.add("fr-FR.screen.products.title", "Produits");
translation_registry.add("de-DE.screen.products.title", "Produkte");

translation_registry.add("en-US.screen.products.add_to_cart", "ADD TO CART");
translation_registry.add("fr-FR.screen.products.add_to_cart", "AJOUTER AU PANIER");
translation_registry.add(
    "de-DE.screen.products.add_to_cart",
    "PRODUKT IN DEN WARENKORB LEGEN"
);

translation_registry.add("en-US.screen.products.back_to_catalog", "Back to catalog");
translation_registry.add("fr-FR.screen.products.back_to_catalog", "Vers le catalogue");
translation_registry.add("de-DE.screen.products.back_to_catalog", "Zurück zum Katalog");

translation_registry.add("en-US.screen.products.search", "Search");
translation_registry.add("fr-FR.screen.products.search", "Rechercher");
translation_registry.add("de-DE.screen.products.search", "Suchen");

translation_registry.add("en-US.screen.products.remove_filter", "Remove filter");
translation_registry.add("fr-FR.screen.products.remove_filter", "Supprimer le filtre");
translation_registry.add("de-DE.screen.products.remove_filter", "Filter entfernen");

export default Products;
