import {Storage} from './storage.js'


export class OdooMixin {

    constructor(params) {
        this.params = params;
        this.usage = params.usage
        this.process_id = this.params.process_id
        this.process_menu_id = this.params.process_menu_id
        this.debug = this.params.debug
    }
    call(path, data, method='POST', fullpath=false) {
        let endpoint = fullpath ? path : this.usage + '/' + path
        return this._call(endpoint, method, data)
    }
    _call(endpoint, method, data) {
        if (this.debug) console.log('CALL', endpoint)
        let self = this;
        let params = {
            method: method,
            headers: this._get_headers()
        }
        data = _.isUndefined(data) ? {} : data
        if (method == 'GET' && data.length) {
            endpoint += '?' + new URLSearchParams(data).toString();
        } else if (method == 'POST') {
            params['body'] = JSON.stringify(data);
        }
        return fetch(
            this._get_url(endpoint), params
        )
        .then((response) => {
            if (response.ok) {
                return response.json()
            }
            else {
                let handler = self['_handle_' + response.status.toString()]
                if (_.isUndefined(handler))
                    handler = this._handle_error
                return handler.call(this, response);
            }
        });
    }
    _error_info (response) {
        return {
            'error': response.statusText,
            'status': response.status,
            'response': response,
        }
    }
    _handle_403(response) {
        Storage.apikey = "";
        return this._error_info(response)
    }
    _handle_404(response) {
        console.log('Endpoint not found, please check your odoo configuration. URL: ', response.url)
        return this._error_info(response)
    }
    _handle_500(response) {
        return this._error_info(response)
    }
    _handle_error(response) {
        console.log(response.status, response.statusText, response.url)
        return this._error_info(response)
    }
    _get_headers() {
        return {
            'Content-Type': 'application/json',
            'SERVICE_CTX_MENU_ID': this.process_menu_id,
            'SERVICE_CTX_PROFILE_ID': 1, // FIXME
            'API_KEY': Storage.apikey,
        }
    }
    _get_url (endpoint) {
        return '/shopfloor/' + endpoint
    }
}


export class OdooMocked extends OdooMixin{

    _set_demo_data() {
        this.demo_data = window.DEMO_CASES[this.usage]
    }
    call(path, data, method='POST', fullpath=false) {
        this._set_demo_data()
        console.log('CALL:', path, this.usage);
        console.dir('CALL data:', data);
        if (!_.isUndefined(this[path])) {
            // provide your own mock by enpoint
            return this[path].call(this, data)
        }
        if (!_.isUndefined(this[this.usage + '_' + path])) {
            // provide your own mock by enpoint and specific process
            return this[this.usage + '_' + path].call(this, data)
        }
        let result
        let barcode = data ? data.barcode || data.location_barcode : null
        if (_.has(this.demo_data, barcode)) {
            // pick a specific case for this barcode
            result = this.demo_data[barcode]
        }
        if (_.has(this.demo_data, path)) {
            // pick general case for this path
            result = this.demo_data[path]
        }
        if (_.has(result, barcode)) {
            // pick specific barcode case inside path case
            result = result[barcode]
        }
        if (_.has(result, path)) {
            // pick the case were the 1st step is decide by the barcode
            result = result[path]
        }
        if (_.has(result, 'ok')) {
            // pick the case were you have good or bad result
            result = result['ok']
        }
        if (!result) {
            throw 'NOT IMPLEMENTED: ' + path
        }
        console.dir('CALL RETURN data:', result);
        return Promise.resolve(result)
    }
    scan_anything (barcode) {
        console.log('Scan anything', barcode, this.usage);
        this._set_demo_data()
        var demo_case = this.demo_data[barcode]
        if (!demo_case) {
            return Promise.resolve({
                "message": {"message_type": "error", "message": "Unknown barcode"}
            })
        }
        console.dir(demo_case);
        return Promise.resolve(demo_case)
    }
    cluster_picking_set_destination_all (data) {
        let result = this.demo_data['set_destination_all']
        if (data.confirmation) {
            result = result['OK']
        } else {
            result = result['KO']
        }
        return Promise.resolve(result)
    }
}


export class Odoo extends OdooMixin{

    // TODO: review and drop very specific methods, move calls to specific components
    start (barcode) {
        return this.call('start', 'POST', {'barcode': barcode})
    }
    scan_anything (barcode) {
        console.log('Scan anything', barcode, this.usage);
        throw 'NOT IMPLEMENTED!'
    }

}
