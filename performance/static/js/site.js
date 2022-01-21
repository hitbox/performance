"use strict";

const currentTheme = localStorage.getItem(LOCALDATA_THEME_KEY);
document.documentElement.setAttribute("data-theme", currentTheme);

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

function initLightDarkMode() {
    // Hook up dark/light mode toggle
    const currentTheme = localStorage.getItem(LOCALDATA_THEME_KEY);
    const checked = currentTheme && currentTheme === "dark";
    const themeToggles = document.getElementsByClassName("theme-toggler");
    for (let i = 0; i < themeToggles.length; i++) {
        themeToggles[i].checked = checked;
        themeToggles[i].addEventListener("change", function(e) {
            let themeName = e.target.checked ? "dark" : "light";
            document.documentElement.setAttribute("data-theme", themeName);
            localStorage.setItem(LOCALDATA_THEME_KEY, themeName);
        }, false);
    }
}

function initDataHref() {
    // data-href
    // Make elements with data-href attributes clickable
    let elements = document.querySelectorAll("[data-href]");
    for (let i = 0; i < elements.length; i++) {
        elements[i].addEventListener("click", function() {
            location.href = this.getAttribute("data-href");
        });
    }

}

function initCloseButton() {
    // close button that deletes itself and parent
    let elements = document.querySelectorAll(".click.close");
    for (let i = 0; i < elements.length; i++) {
        elements[i].addEventListener("click", function() {
            this.parentNode.parentNode.removeChild(this.parentNode);
        });
    }
}

document.addEventListener("DOMContentLoaded", function(event) {
    initLightDarkMode();
    initDataHref();
    initCloseButton();
    initDatePickers();
});
