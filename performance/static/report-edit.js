document.addEventListener("DOMContentLoaded", function(event) {
    // More human-friendly percent inputs
    var percentInputs = document.querySelectorAll('input.percent');
    for (var i = 0; i < percentInputs.length; i++) {
        if (percentInputs[i].value) {
            // Round to four decimal places and then to human friendly percentage.
            // convert to a float
            var v = parseFloat(percentInputs[i].value);
            // keep four digits after decimal
            // https://stackoverflow.com/a/11832950/2680592
            v = Math.round((v + Number.EPSILON) * 10000) / 10000;
            // percent
            v *= 100;
            // keep/pad to two digits after decimal
            percentInputs[i].value = v.toFixed(2);
        }
    }

    document.getElementById('reportform').addEventListener('submit', function() {
        for (var i = 0; i < percentInputs.length; i++) {
            if (percentInputs[i].value) {
                percentInputs[i].value /= 100;
            }
        }
    });
});
