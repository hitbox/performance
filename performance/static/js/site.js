"use strict";

// query user's preference
const mediaQueryPrefersDark = window.matchMedia("(prefers-color-scheme: dark)");

// Update data-theme attribute from local storage or media query as soon as possible.
let currentTheme = localStorage.getItem(LOCALDATA_THEME_KEY);
if (!currentTheme || currentTheme === "os") {
    // check client or operating system preference
    currentTheme = mediaQueryPrefersDark.matches ? "dark": "";
}
document.documentElement.setAttribute("data-theme", currentTheme);

function initLightDarkMode() {
    // DOM should be ready

    // listen data-theme attribute changes
    // NOTE: does not fire for initial page load
    const observer = new MutationObserver(
        function callback(mutationsList, observer) {
            for (let mutation of mutationsList) {
                if (mutation.type === "attributes" && mutation.attributeName === "data-theme") {
                    // save theme locally
                    const themeName = document.documentElement.getAttribute("data-theme");
                    localStorage.setItem(LOCALDATA_THEME_KEY, themeName);
                }
            }
        });
    observer.observe(document.documentElement, {"attributes": true});

    // listen media query changes
    mediaQueryPrefersDark.addEventListener("change", function(event) {
        // update our dark theme attribute if the media query changes to prefer dark
        document.documentElement.setAttribute("data-theme", event.matches ? "dark" : "");
    });

    //
    // initial update toggle button from attribute
    const themeName = document.documentElement.getAttribute("data-theme");
    // initial update toggle state

    const themeSelect = document.getElementById("select-theme");

    themeSelect.value = themeName;

    function updateLabels() {
        for (let label of themeSelect.labels) {
            let index = themeSelect.selectedIndex;
            let option = themeSelect.options[index];
            label.innerHTML = option.innerHTML;
            label.title = option.title;
        }
    }

    updateLabels();

    for (let label of themeSelect.labels) {
        label.addEventListener("click", function(event) {
            // cycle through options
            themeSelect.selectedIndex = (themeSelect.selectedIndex + 1) % themeSelect.options.length;
            updateLabels();
            document.documentElement.setAttribute("data-theme", themeSelect.value);
        });
    }

    themeSelect.addEventListener("change", function(event) {
        updateLabels();
    });

    // scripting is controlling now, hide <select>
    themeSelect.style.display = "none";
}

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

document.addEventListener("DOMContentLoaded", function(event) {
    initLightDarkMode();
    initDataHref();
    initCloseButton();
    initDatePickers();
});
