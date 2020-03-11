Vue.component('reset-screen-button', {
    props: ['show_reset_button'],
    methods: {
        reset: function () {
            this.$emit('reset');
        },
    },
    template: `
        <div class="action reset">
            <v-form class="m-t5" v-if="show_reset_button" v-on:reset="reset">
                <v-btn depressed x-large @click="reset">Reset</v-btn>
            </v-form>
        </div>
    `,
});

Vue.component('cancel-button', {
    template: `
        <div class="action reset">
            <v-btn depressed x-large color="error" v-on:click="$emit('cancel')">Cancel</v-btn>
        </div>
    `,
});

// TODO: could be merged w/ userConfirmation
Vue.component('last-operation', {
    // Props: ['info'],
    data: function () {
        return {'info': {}};
    },
    template: `
    <div class="last-operation">
        <v-dialog persistent fullscreen tile value=true>
            <v-alert tile type="info" prominent transition="scale-transition">
                <v-card outlined color="blue lighten-1" class="message mt-10">
                    <v-card-title>This was the last operation of the document.</v-card-title>
                    <v-card-text>The next operation is ready to be processed.</v-card-text>
                </v-card>
                <v-form class="mt-10">
                    <v-btn x-large color="success" @click="$emit('confirm')">OK</v-btn>
                </v-form>
            </v-alert>
        </v-dialog>
    </div>
    `,
});


Vue.component('get-work', {
    template: `
    <div class="get-work fullscreen-buttons fullscreen-buttons-50">
      <v-btn id="btn-get-work" color="success" @click="$emit('get_work')">
          Get work
      </v-btn>
      <v-btn id="btn-manual" color="default" @click="$emit('manual_selection')">
          Manual selection
      </v-btn>
    </div>
    `,
});


Vue.component('stock-zero-check', {
    template: `
    <div class="stock-zero-check">
      <v-dialog fullscreen tile value=true class="actions fullscreen">
        <v-card>
          <div class="button-list button-vertical-list">
            <v-row align="center">
              <v-col class="text-center" cols="12">
                <v-btn depressed x-large color="primary" @click="$emit('action', 'action_confirm_zero')">Confirm stock = 0</v-btn>
              </v-col>
            </v-row>
            <v-row align="center">
              <v-col class="text-center" cols="12">
                <v-btn depressed x-large color="warning" @click="$emit('action', 'action_confirm_not_zero')">Confirm stock NOT empty</v-btn>
              </v-col>
            </v-row>
          </div>
        </v-card>
      </v-dialog>
    </div>
  `,
});


Vue.component('manual-select', {
    props: {
        'records': {
            'type': Array,
            'default': [],
        },
        'key_value': {
            'type': String,
        },
        'key_title': {
            'type': String,
            'default': 'name',
        },
    },
    data: function () {
        return {'selected': null};
    },
    methods: {
        // NOTE: v-list-item-group should be able to work w/ `v-model`.
        // For some reason, it does not work here.
        // At the same time is preferable to have a place to hook to
        // in case you want to customize its behavior.
        updateSelected (selectedItem) {
            this.selected = selectedItem;
        },
    },
    mounted: function () {
        if (this.records.length && !this.selected) {
            this.updateSelected(this.records[0][this.key_value]);
        }
    },
    template: `
    <div class="manual-select with-bottom-actions">
      <v-card outlined>
        <v-list shaped v-if="records.length">
          <v-list-item-group mandatory color="success">
            <v-list-item v-for="rec in records" :key="rec[key_value]" @click="updateSelected(rec[key_value])" :data-id="rec[key_value]">
              <v-list-item-content>
                <v-list-item-title v-text="rec[key_title]"></v-list-item-title>
                <!-- TODO: this part is harcoded and works only for picking batch selection
                We should find a way to pass this content dynamically.
                We don't have labels so we cannot just loop on them.
                -->
                <v-list-item-action-text>Operations: {{ rec.picking_count }}</v-list-item-action-text>
                <v-list-item-action-text>Lines: {{ rec.move_line_count }}</v-list-item-action-text>
              </v-list-item-content>
            </v-list-item>
          </v-list-item-group>
        </v-list>
        <v-alert tile type="error" v-if="!records.length">
          No record found.
        </v-alert>
      </v-card>
      <v-row class="actions bottom-actions" v-if="records.length">
        <v-col>
          <v-btn color="success" @click="$emit('select', selected)">
            Start
          </v-btn>
        </v-col>
        <v-col>
          <v-btn color="default" @click="$emit('back')" class="float-right">
            Back
          </v-btn>
        </v-col>
      </v-row>
    </div>
  `,
});


Vue.component('state-display-info', {
    props: {
        'info': Object,
    },
    template: `
  <div class="state-display-info" v-if="info.title">
    <div class="container">
      <v-alert tile dense outlined type="info">
        <div class="state-title text--secondary">{{ info.title }}</div>
      </v-alert>
    </div>
  </div>
`,
});
