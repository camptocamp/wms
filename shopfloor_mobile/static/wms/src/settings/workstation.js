/**
 * Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

export var Workstation = Vue.component("workstation", {
    data: function() {
        return {
            usage: "workstation",
            workstation_scanned: false,
            scan_data: {},
            scan_message: {},
            search_input_placeholder: "Scan workstation code",
        };
    },
    template: `
        <Screen :screen_info="{title: $t('screen.settings.workstation.title'), klass: 'settings settings-workstation'}">
            <template v-slot:header>
                <user-information
                    v-if="workstation_scanned"
                    :message="scan_message"
                    />
            </template>
            <searchbar
                v-on:found="on_scan"
                :input_placeholder="search_input_placeholder"
                />

            <div class="button-list button-vertical-list full">
                <v-row align="center">
                    <v-col class="text-center" cols="12">
                        <btn-back/>
                    </v-col>
                </v-row>
            </div>
        </Screen>
    `,
    mounted() {
        const odoo_params = {usage: this.usage};
        this.odoo = this.$root.getOdoo(odoo_params);
        if (this.$route.params.identifier) {
            this.getData(this.$route.params.identifier);
        }
    },
    methods: {
        on_scan: function(scanned) {
            this.odoo.call("setdefault", {barcode: scanned.text}).then(result => {
                this.workstation_scanned = true;
                if (result.error) {
                    console.error(result);
                    this.scan_message = {
                        message_type: "error",
                        body:
                            "Request could not be processed, maybe the module shopfloor_workstation is not installed.",
                    };
                    return;
                }
                this.scan_data = result.data;
                this.scan_message = result.message;
                if (this.scan_message.message_type === "info") {
                    this.$root.trigger(
                        "profile:selected",
                        this.scan_data.records[0].profile,
                        true
                    );
                    // TODO: the success message will not be displayed, as we change screen !
                    this.$root.$router.push({name: "home"});
                }
            });
        },
    },
});
