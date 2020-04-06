export var HomePage = Vue.component("home-page", {
    computed: {
        navigation() {
            return this.$root.config.get("menus");
        },
    },
    props: ["routes"],
    template: `
        <Screen
            title="Barcode scanner"
            klass="home"
            :show-menu="false"
            >
            <v-list>
                <v-list-item
                    v-for="item in navigation"
                    :key="item.id"
                    :href="'#/' + item.process.code"
                    link
                    >
                    <v-list-item-content>
                        <v-list-item-title>{{ item.name }}</v-list-item-title>
                    </v-list-item-content>
                </v-list-item>
            </v-list>

            <v-alert tile class="mt10" color="warning" v-if="$root.demo_mode">DEMO MODE ON</v-alert>
        </Screen>
    `,
});
