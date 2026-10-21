
/** @odoo-module **/

import { Component, onWillStart, proxy, signal } from "@odoo/owl";
import { useDateTimePicker } from "@web/core/datetime/datetime_picker_hook";
import {
    deserializeDate,
    formatDate,
    today,
} from "@web/core/l10n/dates";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class WorkshopDashboard extends Component {
    static template = "workshop_service.WorkshopDashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.loadSequence = 0;
        const todayString = today().toISODate();
        this.state = proxy({
            dateFrom: todayString,
            dateTo: todayString,
            workshop: "all",
            loading: true,
            error: "",
            data: {
                metrics: {
                    total: 0,
                    open: 0,
                    completed: 0,
                    pending: 0,
                },
                locations: [],
                recent_orders: [],
                can_create_order: false,
                can_read_orders: false,
                can_manage_locations: false,
            },
        });
        this.dateRangeRef = signal.ref();
        const dashboard = this;
        this.datePicker = useDateTimePicker(
            {
                target: this.dateRangeRef,
                getInputs: () => [],
                get pickerProps() {
                    return {
                        type: "date",
                        range: true,
                        value: [
                            deserializeDate(dashboard.state.dateFrom),
                            deserializeDate(dashboard.state.dateTo),
                        ],
                    };
                },
                onApply(value) {
                    const selectedDates = Array.isArray(value)
                        ? value
                        : [value, value];
                    const startDate = selectedDates[0] || selectedDates[1];
                    const endDate = selectedDates[1] || startDate;
                    if (!startDate || !endDate) {
                        return;
                    }
                    dashboard.state.dateFrom = startDate.toISODate();
                    dashboard.state.dateTo = endDate.toISODate();
                    dashboard.loadData();
                },
            },
            { useOwlHooks: true }
        );
        onWillStart(() => this.loadData());
    }

    openDateRangePicker() {
        this.datePicker.open(0);
    }

    dateRangeLabel() {
        const startDate = deserializeDate(this.state.dateFrom);
        const endDate = deserializeDate(this.state.dateTo);
        if (this.state.dateFrom === this.state.dateTo) {
            return formatDate(startDate);
        }
        return `${formatDate(startDate)} - ${formatDate(endDate)}`;
    }

    setWorkshop(event) {
        this.state.workshop = event.target.value;
        this.loadData();
    }

    selectWorkshop(event) {
        const locationId = event.currentTarget.dataset.locationId;
        this.state.workshop =
            this.state.workshop === locationId ? "all" : locationId;
        this.loadData();
    }

    isWorkshopSelected(locationId) {
        return this.state.workshop === String(locationId);
    }

    workshopCardClass(locationId) {
        return this.isWorkshopSelected(locationId)
            ? "o_workshop_location_card active"
            : "o_workshop_location_card";
    }

    async loadData() {
        const sequence = ++this.loadSequence;
        this.state.loading = true;
        this.state.error = "";
        try {
            const locationId =
                this.state.workshop === "all"
                    ? false
                    : Number(this.state.workshop);
            const data = await this.orm.call(
                "workshop.order",
                "get_dashboard_data",
                [this.state.dateFrom, this.state.dateTo, locationId]
            );
            if (sequence !== this.loadSequence) {
                return;
            }
            if (data.error) {
                this.state.error = data.error;
                return;
            }
            this.state.data = data;
        } catch (error) {
            if (sequence === this.loadSequence) {
                this.state.error =
                    error.data?.message ||
                    error.message ||
                    "No se pudo cargar el dashboard.";
            }
        } finally {
            if (sequence === this.loadSequence) {
                this.state.loading = false;
            }
        }
    }

    newOrder() {
        const context = { default_origin: "workshop" };
        if (this.state.workshop !== "all") {
            context.default_location_id = Number(this.state.workshop);
        }
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Nueva orden",
            res_model: "workshop.order",
            views: [[false, "form"]],
            context,
            target: "current",
        });
    }

    openOrders() {
        this.action.doAction("workshop_service.action_workshop_orders");
    }

    openOrder(orderId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "workshop.order",
            res_id: orderId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    openLocations() {
        this.action.doAction("workshop_service.action_workshop_locations");
    }
}

registry.category("actions").add(
    "workshop_service.dashboard",
    WorkshopDashboard
);
