document.addEventListener("DOMContentLoaded", function () {
    // Add 'readonly' attribute to date pickers and dropdowns on focus
    document.querySelectorAll("input[type='text'], .Select-input input").forEach(function (input) {
        input.setAttribute("readonly", true);
    });

    // Remove 'readonly' when the input loses focus
    document.querySelectorAll("input[type='text'], .Select-input input").forEach(function (input) {
        input.addEventListener("focus", function () {
            input.setAttribute("readonly", true);
        });
    });
});