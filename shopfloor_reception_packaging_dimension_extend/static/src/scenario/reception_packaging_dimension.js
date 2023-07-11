/**
 * Copyright 2023 Camptocamp SA (http://www.camptocamp.com)
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

import {process_registry} from "/shopfloor_mobile_base/static/wms/src/services/process_registry.js";

// Get the template of the reception scenario previously updated
// by the shopfloor_reception_packaging_dimension_mobile module
const reception_scenario = process_registry.get("reception");
const template = reception_scenario.component.template;
// Add the new fields in the form at the predifined location
const pos = template.indexOf("<!-- extend -->");
const new_template =
    template.substring(0, pos) +
    `
            <v-row>
                <v-switch
                    label="Bundeable"
                    v-model="state.data.packaging.is_bundeable"
                ></v-switch>
            </v-row>
            <v-row>
                <v-switch
                    label="Prepackaged"
                    v-model="state.data.packaging.is_prepackaged"
                ></v-switch>
            </v-row>

` +
    template.substring(pos);

// Add the new packaging measurements to return in the payload
const packaging_measurements = reception_scenario.component.methods.get_packaging_measurements();
packaging_measurements.push("is_bundeable", "is_prepackaged");

// Extend the reception scenario with :
//   - the new patched template
//   - the new list of packaging measurements
//
const ReceptionPackageDimension = process_registry.extend("reception", {
    template: new_template,
    "methods.get_packaging_measurements": function () {
        return packaging_measurements;
    },
});

process_registry.replace("reception", ReceptionPackageDimension);
