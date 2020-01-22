var homepage = Vue.component('home-page', {
    data: function(){ return {
        // This is kind of a duplicate to the Routes const in main.js
        // But can not workout how to pass props values through the render function
        'navigation': [
            {'name': 'Home', 'hash': '#'},
            {'name': 'PutAway', 'hash': '#putaway'},
            {'name': 'Pallet Transfer', 'hash': '#pallettransfer'},
        ]
    }},
    props:['routes'],
    template: `
    <div>
        <a v-for="nav in this.navigation" v-bind:href="nav.hash" class="btn btn-primary btn-lg btn-block">{{ nav.name }}</a>
    </div>

    `
});
