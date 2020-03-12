import {demotools} from './demo.core.js';

var DEMO_CLUSTER_PICKING_1 = {
    "find_batch": {
        "next_state": "confirm_start",
        "data": {
            "confirm_start": {
                "id": 100,
                "name": "BATCH001",
                "picking_count": 3,
                "move_line_count": 6,
                "pickings": [demotools.makePicking(), demotools.makePicking()],
            },
        },
    },
    "list_batch": {
        "next_state": "manual_selection",
        "message": {
            "message_type": "success",
            "message": "Previous line postponed",
        },
        "data": {
            // Next line to process
            "manual_selection": {
                "records": demotools.batchList(15),
            },
        },
    },
    "select": {
        "next_state": "confirm_start",
        "data": {
            "confirm_start": {
                "id": 100,
                "name": "BATCHXXX",
                "picking_count": 3,
                "move_line_count": 6,
                "pickings": [demotools.makePicking(), demotools.makePicking()],
            },
        },
    },
    "confirm_start": {
        "next_state": "start_line",
        "data": {
            "start_line": demotools.makeBatchPickingLine(),
        },
    },
    "unassign": {
        "next_state": "start",
    },
    "scan_line": {
        "next_state": "scan_destination",
        "data": {
            "scan_destination": {

            },
        },
    },
    "scan_destination_pack": {
        "ok": {
            "next_state": "start_line",
            "message": {
                "message_type": "success",
                "message": "Product 5 put in bin #2",
            },
            "data": {
                "start_line": demotools.makeBatchPickingLine(),
            },
        },
        "ko": {
            "next_state": "zero_check",
            "message": {
                "message_type": "info",
                "message": "Stock check required",
            },
            "data": {
                "zero_check": {},
            },
        },
    },
    "stock_is_zero": {
        "next_state": "start_line",
        "message": {
            "message_type": "success",
            "message": "Stock zero confirmed",
        },
        "data": {
            // Next line to process
            "start_line": demotools.makeBatchPickingLine(),
        },
    },
    "skip_line": {
        "next_state": "start_line",
        "message": {
            "message_type": "success",
            "message": "Previous line postponed",
        },
        "data": {
            // Next line to process
            "start_line": demotools.makeBatchPickingLine(),
        },
    },
    "stock_issue": {
        "next_state": "start_line",
        "message": {
            "message_type": "success",
            "message": "Stock out confirmed",
        },
        "data": {
            // Next line to process
            "start_line": demotools.makeBatchPickingLine(),
        },
    },
    "check_pack_lot": {},
    "prepare_unload": {
        "next_state": "unload_all",
        "data": {
            "unload_all": {

            },
        },
    },
    "set_destination_all": {
        "OK": {
            "next_state": "start_line",
            "message": {
                "message_type": "success",
                "message": "Destination set",
            },
            "data": {
                // Next line to process
                "start_line": demotools.makeBatchPickingLine(),
            },
        },
        "KO": {
            "next_state": "confirm_unload_all",
            "data": {
                // Next line to process
                "unload_all": {},
            },
            "message": {
                "message_type": "warning",
                "message": "Confirm you want to unload them all?",
            },
        },
    },
    "unload_split": {},
    "unload_scan_pack": {},
    "unload_scan_destination": {},
    "unload_router": {},
};

demotools.add_case('cluster_picking', DEMO_CLUSTER_PICKING_1);
