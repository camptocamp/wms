export default class {
    constructor(orders = {}) {
        this.state = {
            orders: orders,
        };
        this.mutations = {
            // NOTE: The orders mutations start with orders_
            // so that the store subscription can identify
            // which key in sessionStorage needs to be updated
            // after each store change.
            orders_loadOrders: (state, orders) => {
                state.orders = orders;
            },
        };
    }
}
