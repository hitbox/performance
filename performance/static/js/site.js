"use strict";

function initDatePickers() {
    // flatpickr date entry

    function datepickerOnOpen(selectedDates, dateStr, datepicker) {
        // set the date to show on the open event because setting the
        // defaultDate actually populates the inputs.
        // fallbackDate: template injection
        datepicker.setDate(fallbackDate);
    }

    const elements = document.getElementsByClassName("date-entry");
    Array.prototype.forEach.call(elements, function(element, index) {
        flatpickr(element,
            {
                onOpen: datepickerOnOpen,
            }
        );
    });
}

function initDataHref() {
    // data-href
    // Make elements with data-href attributes clickable
    const elements = document.querySelectorAll("[data-href]");
    for (let i = 0; i < elements.length; i++) {
        elements[i].addEventListener("click", function() {
            location.href = this.getAttribute("data-href");
        });
        elements[i].addEventListener("auxclick", function() {
            window.open(this.getAttribute("data-href"), "_blank");
        });
    }

}

function initCloseButton() {
    // close button that deletes itself and parent
    const elements = document.querySelectorAll(".click.close");
    for (let i = 0; i < elements.length; i++) {
        elements[i].addEventListener("click", function() {
            this.parentNode.parentNode.removeChild(this.parentNode);
        });
    }
}

function initDangerButtons() {
    const select = "input[type=submit].danger";
    const dangerButtons = document.querySelectorAll(select);
    for (let button of dangerButtons) {
        button.addEventListener("click", function(event) {
            if (!confirm("Are you sure?")) {
                event.preventDefault();
            }
        });
    }
}

function initScrollToActive() {
    const el = document.querySelector("tr.active");
    if (el !== null) {
        const alignToTop = false;
        el.scrollIntoView(alignToTop);
    }
}

document.addEventListener("DOMContentLoaded", function(event) {
    initDataHref();
    initCloseButton();
    initDatePickers();
    initDangerButtons();
    initScrollToActive();
});
