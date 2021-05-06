'use strict';

let viewModel = {};

document.addEventListener("DOMContentLoaded", function(event) {
    let httpRequest = new XMLHttpRequest();

    if (!httpRequest) {
        throw 'unable to create XMLHttpRequest'
    }

    httpRequest.onreadystatechange = alertContents;
    httpRequest.open('GET', testurl);
    httpRequest.send();

    function alertContents() {
        if (httpRequest.readyState === XMLHttpRequest.DONE) {
            if (httpRequest.status === 200) {
                let data = JSON.parse(httpRequest.responseText);
                viewModel = ko.mapping.fromJS(data);
                ko.applyBindings(viewModel);
            }
        }
    }
});
