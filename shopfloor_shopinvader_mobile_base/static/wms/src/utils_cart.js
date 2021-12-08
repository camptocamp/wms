import {utils_registry} from "/shopfloor_mobile_base/static/wms/src/services/utils_registry.js";
import store from "/shopfloor_mobile_base/static/wms/src/store/index.js";

export class CartUtils {
    get_cart() {
        const sessionStorage_key = this._get_storage_key();
        return JSON.parse(window.sessionStorage.getItem(sessionStorage_key))
            ? JSON.parse(window.sessionStorage.getItem(sessionStorage_key)).value
            : undefined;
    }
    set_cart(payload) {
        const sessionStorage_key = this._get_storage_key();
        window.sessionStorage.setItem(sessionStorage_key, payload);
    }
    remove_cart() {
        const sessionStorage_key = this._get_storage_key();
        window.sessionStorage.removeItem(sessionStorage_key);
    }
    _get_storage_key() {
        const cart_state_key = store.getters._get_cart_state_key;
        return "shopfloor_" + cart_state_key;
    }
}

utils_registry.add("cart", new CartUtils());
