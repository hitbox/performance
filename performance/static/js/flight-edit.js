"use strict";

// javascript injection:
//     FLIGHT_CALCS: url to get calculations and autofill from.

// indicate to the updates that the form is submitting and they shouldn't bother.
let isSubmitting = false;

class FormUpdater {
    /*
     * Update estimated/actual difference minutes, and delay codes placeholder
     * for late minutes, on changes.
     */
    constructor(
        diffMinutesId,
        delayCodesId,
        estDateId,
        estTimeId,
        actDateId,
        actTimeId,
    ) {
        this.diffMinutesId = diffMinutesId;
        this.delayCodesId = delayCodesId;
        this.estDateId = estDateId;
        this.estTimeId = estTimeId;
        this.actDateId = actDateId;
        this.actTimeId = actTimeId;
    }

    fetchAndUpdate() {
        if (isSubmitting) {
            return
        }
        // save copies for promises below
        const diffMinutesId = this.diffMinutesId;
        const delayCodesId = this.delayCodesId;

        const delayCodes = document.getElementById(this.delayCodesId).value;
        const estimatedDate = document.getElementById(this.estDateId);
        const estimatedTime = document.getElementById(this.estTimeId);
        const actualDate = document.getElementById(this.actDateId);
        const actualTime = document.getElementById(this.actTimeId);
        const params = {
            fallbackDate: fallbackDate,
            delayCodes: delayCodes,
            estimatedDate: estimatedDate.value,
            estimatedTime: estimatedTime.value,
            actualDate: actualDate.value,
            actualTime: actualTime.value,
        }

        fetch(FLIGHT_CALCS, {
            method: "POST",
            body: JSON.stringify(params),
            headers: {
                "Content-Type": "application/json; charset=utf-8",
            },
        }).then(function(response) {
            if (response.ok) {
                return response.json();
            }
        }).then(function(data) {
            if (data) {
                // TODO: flash if value has changed.
                // Estimated/Actual Difference Minutes
                const diffMinutesElem = document.getElementById(diffMinutesId);
                diffMinutesElem.value = data.minutes;
                // update value attribute for css
                diffMinutesElem.setAttribute("value", data.minutes);
                // Delay Codes
                const delayCodesElem = document.getElementById(delayCodesId);
                delayCodesElem.value = data.delays_string
                delayCodesElem.setAttribute("value", data.delays_string);
            }
        });
    }
}

function initUpdaters() {
    // get array of date and time fields
    const originElements = document.querySelectorAll(
        ".flight.origin.date-entry,"
        + ".flight.origin.time-entry"
    )
    const destinationElements = document.querySelectorAll(
        ".flight.destination.date-entry,"
        + ".flight.destination.time-entry"
    )

    // updater objects
    const originDatetimeChange = new FormUpdater(
        "origin-diff-minutes",
        originDelayCodesId,
        "origin_departure_estimated_date",
        "origin_departure_estimated_time",
        "origin_departure_actual_date",
        "origin_departure_actual_time",
    );
    const destinationDatetimeChange = new FormUpdater(
        "destination-diff-minutes",
        destinationDelayCodesId,
        "destination_arrival_estimated_date",
        "destination_arrival_estimated_time",
        "destination_arrival_actual_date",
        "destination_arrival_actual_time",
    );

    // bind context
    const onChangeOrigin = originDatetimeChange.fetchAndUpdate.bind(originDatetimeChange);
    const onChangeDestination = destinationDatetimeChange.fetchAndUpdate.bind(destinationDatetimeChange);

    // on changes in dates or times update from server
    originElements.forEach(function(element) {
        element.addEventListener("change", onChangeOrigin);
    });
    destinationElements.forEach(function(element) {
        element.addEventListener("change", onChangeDestination);
    });

    document.getElementById(
        originDelayCodesId
    ).addEventListener(
        "change", onChangeOrigin
    );

    document.getElementById(
        destinationDelayCodesId
    ).addEventListener(
        "change", onChangeDestination
    );

    // initial update
    originDatetimeChange.fetchAndUpdate();
    destinationDatetimeChange.fetchAndUpdate();

    // on submit set global to avoid calculation calls that will fail
    const forms = document.getElementsByTagName("form");
    if (forms.length !== 1) {
        alert("Please alert developer.");
    }
    forms[0].addEventListener("submit", function(event) {
        isSubmitting = true;
    });
}

function initDeleteConfirm() {
    const deleteButton = document.getElementById("delete");
    if (!deleteButton) {
        alert("Clicking delete will not prompt first!");
    }
    deleteButton.addEventListener("click", function(event) {
        if (!confirm("Delete this flight?")) {
            event.preventDefault();
        }
    });
}

document.addEventListener("DOMContentLoaded", function() {
    // template injection
    if (isEdit) {
        initDeleteConfirm();
    }
    initUpdaters();
});

