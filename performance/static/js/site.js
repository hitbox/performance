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

function push_anchor() {
    // anchor variable pushed through templates
    if (typeof anchor === 'string') {
        if (window.location.hash !== anchor) {
            window.location.assign('#' + anchor);
        }
    }
}

function init_clicks() {
    // click other elements by id, on click
    const elements = document.querySelectorAll("[data-clicks]");
    if (elements) {
        for (let element of elements) {
            element.addEventListener("click", function(event) {
                event.preventDefault();
                for (let other_id of event.target.dataset.clicks.split(" ")) {
                    document.getElementById(other_id).click();
                }
            });
        }
    }
}

function init_textarea_resize() {
    // Automatically resize height of selected textareas.
    const textareas = document.querySelectorAll('textarea.auto-resize');

    for (const textarea of textareas) {

        function resize(textarea) {
            // Reset height.
            textarea.style.height = 'auto';
            // Set height to scroll height
            textarea.style.height = textarea.scrollHeight + 'px';
        }

        textarea.addEventListener('input', function() {
            resize(textarea);
        });
        resize(textarea);
    }
}

document.addEventListener("DOMContentLoaded", function(event) {
    initDataHref();
    initCloseButton();
    initDatePickers();
    initDangerButtons();
    initScrollToActive();
    push_anchor();
    init_clicks();
    init_textarea_resize();
});
