export default class {
    constructor(cart = {}) {
        this.state = {
            cart: cart,
        };
        this.getters = {
            _get_cart_state_key: () => {
                return Object.keys(this.state)[0];
            },
        };
        this.mutations = {
            // NOTE: The cart mutations start with cart_
            // so that the store subscription can identify
            // which key in sessionStorage needs to be updated
            // after each store change.
            cart_loadCart: (state, cart) => {
                state.cart = cart;
            },
            cart_addItemToCart: (state, newItem) => {
                const item_in_cart = this.findItemInCart(state, newItem);
                if (!item_in_cart) {
                    state.cart.lines.items.push({
                        product: newItem,
                        total: newItem.price.default.value,
                        qty: 1,
                    });
                    state.cart.amount.total += newItem.price.default.value;
                } else {
                    // TODO: recalculations for tax, discount, total_without_discount, untaxed
                    this.addOne(state, item_in_cart);
                }
            },
            cart_addOneUnit: (state, item) => {
                const item_in_cart = this.findItemInCart(state, item.product);
                this.addOne(state, item_in_cart);
            },
            cart_removeOneUnit: (state, item) => {
                item.qty -= 1;
                item.total -= item.product.price.default.value;
                state.cart.amount.total -= item.product.price.default.value;
                if (item.qty < 1) {
                    const cart_items = state.cart.lines.items;
                    const index = cart_items.indexOf(item);
                    cart_items.splice(index, 1);
                }
            },
        };
    }
    findItemInCart(state, newItem) {
        const cart_items = state.cart.lines.items;
        const same_item_in_cart = cart_items.find(
            (item) => item.product.id === newItem.id
        );
        return same_item_in_cart;
    }
    addOne(state, item) {
        item.qty += 1;
        item.total += item.product.price.default.value;
        state.cart.amount.total += item.product.price.default.value;
    }
}
