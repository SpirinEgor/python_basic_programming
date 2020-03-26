buttonNames = ['load-gifts-funfrom.me',
                'load-gifts-2cherry.ru',
                'load-gifts-podarki.ru',
                'delete-all'];

$(document).ready(function () {
    draw_table();
    for (let name of buttonNames) {
        setup_button(name)
    }
});

function setup_button(name) {
    document.getElementById(name).onclick = function () {
        document.getElementById(name).style.background = "red";
        postFromSrc("http://127.0.0.1:5000/" + name);
    };
}

function draw_table() {
    $('#table_body tr').remove()
    $.getJSON('http://127.0.0.1:5000/get_all', function (data) {
        $.each(data, function (key, val) {
            let row = "";
            $.each(val, function (key, val) {
                if (typeof(val) == "string" && val.trim().startsWith("http")) {
                    val = "<a href=" + val + ">" + val + "</a>"
                }
                row += '<td>' + val + '</td>';
            });
            $('#table_body').append('<tr>' + row + '</tr>');
        });
    });
}

function postFromSrc(url) {
    let promise = new Promise(function (resolve, reject) {
        $.get(url, function (data) {
            draw_table()
            for (let name of buttonNames) {
                document.getElementById(name).style.background = "#007bff";
            }
        });
    });
}
