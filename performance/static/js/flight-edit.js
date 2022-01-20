"use strict";

// javascript injection:
//     DIFF_MINUTES_URL,
//     FLIGHT_ID,

class DiffMinutesUpdate {
    constructor(targetId, estDateId, estTimeId, actDateId, actTimeId) {
        this.targetId = targetId;
        this.estDateId = estDateId;
        this.estTimeId = estTimeId;
        this.actDateId = actDateId;
        this.actTimeId = actTimeId;
    }

    fetchAndUpdate() {
        const targetId = this.targetId;
        const estimatedDate = document.getElementById(this.estDateId);
        const estimatedTime = document.getElementById(this.estTimeId);
        const actualDate = document.getElementById(this.actDateId);
        const actualTime = document.getElementById(this.actTimeId);

        fetch(DIFF_MINUTES_URL, {
            method: "POST",
            body: JSON.stringify({
                flightId: FLIGHT_ID,
                estimatedDate: estimatedDate.value,
                estimatedTime: estimatedTime.value,
                actualDate: actualDate.value,
                actualTime: actualTime.value,
            }),
            headers: {
                "Content-Type": "application/json; charset=utf-8",
            },
        }).then(function(response) {
            if (response.ok) {
                return response.json();
            }
        }).then(function(data) {
            const elem = document.getElementById(targetId);
            elem.value = data.minutes;
            elem.setAttribute("value", data.minutes);
        });
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const originDatetimeElements = document.querySelectorAll(
        ".flight.origin.date-entry,"
        + ".flight.origin.time-entry"
    )
    const destinationDatetimeElements = document.querySelectorAll(
        ".flight.destination.date-entry,"
        + ".flight.destination.time-entry"
    )

    const originDatetimeChange = new DiffMinutesUpdate(
        "origin-diff-minutes",
        "origin_departure_estimated_date",
        "origin_departure_estimated_time",
        "origin_departure_actual_date",
        "origin_departure_actual_time",
    );

    const destinationDatetimeChange = new DiffMinutesUpdate(
        "destination-diff-minutes",
        "destination_arrival_estimated_date",
        "destination_arrival_estimated_time",
        "destination_arrival_actual_date",
        "destination_arrival_actual_time",
    );

    originDatetimeElements.forEach(function(element) {
        element.addEventListener("change",
            originDatetimeChange.fetchAndUpdate.bind(originDatetimeChange)
        );
    });

    destinationDatetimeElements.forEach(function(element) {
        element.addEventListener("change",
            destinationDatetimeChange.fetchAndUpdate.bind(destinationDatetimeChange)
        );
    });

    originDatetimeChange.fetchAndUpdate();
    destinationDatetimeChange.fetchAndUpdate();

});

