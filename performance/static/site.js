var currentTheme = localStorage.getItem(LOCALDATA_THEME_KEY);
document.documentElement.setAttribute("data-theme", currentTheme);

document.addEventListener("DOMContentLoaded", function(event) {
    var i;
    var currentTheme = localStorage.getItem(LOCALDATA_THEME_KEY);
    var checked = currentTheme && currentTheme === "dark";
    var themeToggles = document.getElementsByClassName("theme-toggler");
    for (i = 0; i < themeToggles.length; i++) {
        themeToggles[i].checked = checked;
        themeToggles[i].addEventListener("change", function(e) {
            var themeName = e.target.checked ? "dark" : "light";
            document.documentElement.setAttribute("data-theme", themeName);
            localStorage.setItem(LOCALDATA_THEME_KEY, themeName);
        }, false);
    }

    // make elements with data-href attributes clickable
    //elements = document.querySelectorAll("[data-href]");
    //for (i = 0; i < elements.length; i++) {
    //    elements[i].addEventListener("click", function() {
    //        location.href = this.getAttribute("data-href");
    //    });
    //}

    // flatpickr date entry
    // NOTE: flatpickr makes another element for altInput and that screws
    //       everything up!
    var elements;
    elements = document.getElementsByClassName("date-entry");
    Array.prototype.forEach.call(elements, function(element, index) {
        flatpickr(element);
    });
    //for (i = 0; i < elements.length; i++) {
    //    flatpickr(elements[i], {
    //        "altInput": true,
    //        "altFormat": "F j, Y",
    //        "dateFormat": "Y-m-d",
    //    });
    //}

});
