$(document).ready(function () {
    draw_table()
});

function draw_table() {
    $('#table_body').html('');
    $.getJSON('http://127.0.0.1:5000/get_all', function (data) {
        $.each(data, function (key, val) {
            let row = "";
            $.each(val, function (key, val) {
                row += '<td>' + val + '</td>';
            });
            $('#table_body').append('<tr>' + row + '</tr>');
        });
    });
}

const form = document.getElementById('form');
if (form.attachEvent) {
    form.attachEvent("submit", processForm);
} else {
    form.addEventListener("submit", processForm);
}
