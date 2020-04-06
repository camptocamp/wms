import {GenericStatesMixin, ScenarioBaseMixin} from "./mixins.js";

export var SinglePackTransfer = Vue.component("single-pack-transfer", {
    mixins: [ScenarioBaseMixin, GenericStatesMixin],
    template: `
        <Screen :title="menuItem.name" :klass="usage">
            <template v-slot:header>
                <user-information
                    v-if="!need_confirmation && user_notification.message"
                    v-bind:info="user_notification"
                    />
                <state-display-info :info="state.display_info" v-if="state.display_info"/>
            </template>
            <searchbar v-if="state_is(initial_state_key)" v-on:found="on_scan" :input_placeholder="search_input_placeholder"></searchbar>
            <searchbar v-if="state_is('scan_location')" v-on:found="on_scan" :input_placeholder="search_input_placeholder" :input_data_type="'location'"></searchbar>
            <user-confirmation v-if="need_confirmation" v-on:user-confirmation="on_user_confirm" v-bind:question="user_notification.message"></user-confirmation>
            <operation-detail :operation="state.data"></operation-detail>
            <last-operation v-if="state_is('show_completion_info')" v-on:confirm="state.on_confirm"></last-operation>
            <cancel-button v-on:cancel="on_cancel" v-if="show_cancel_button"></cancel-button>
        </Screen>
    `,
    data: function() {
        return {
            usage: "single_pack_transfer",
            show_reset_button: true,
            initial_state_key: "start_scan_pack_or_location",
            current_state_key: "start_scan_pack_or_location",
            states: {
                show_completion_info: {
                    on_confirm: () => {
                        // TODO: turn the cone?
                        this.go_state("start");
                    },
                },
            },
        };
    },
});
