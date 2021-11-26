export default class {
    constructor(products = []) {
        this.state = {
            products: products,
        };
        this.mutations = {
            // NOTE: The products mutations start with products_
            // so that the store subscription can identify
            // which key in sessionStorage needs to be updated
            // after each store change.
            products_loadProducts: (state, products) => {
                state.products = products;
            },
        };
    }
}
