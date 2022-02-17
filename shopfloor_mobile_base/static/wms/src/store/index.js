const store = new Vuex.Store();

// This is called every time the Vuex store is updated
// so that the browser storage is updated accordingly.
store.subscribe((mutation, state) => {
    const state_key = mutation.type.split("_")[0];
    const module_name = state_key + "_module";
    const storage_key = "shopfloor_" + state_key;

    window.sessionStorage.setItem(
        storage_key,
        JSON.stringify({value: state[module_name][state_key]})
    );
});

export default store;
