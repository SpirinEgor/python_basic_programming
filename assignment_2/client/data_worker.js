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


function processForm(e) {
    if (e.preventDefault) e.preventDefault();
    let user_info = $('#form').serializeArray().reduce(function (obj, item) {
        obj[item.name] = item.value;
        return obj;
    }, {});
    let promise = new Promise(function(resolve, reject) {
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: "http://127.0.0.1:5000/new_year",
            data: JSON.stringify(user_info),
            dataType: "json",
            success: function (data) {
                resolve(data);
            },
            error: function (err) {
                reject(err);
            }
        });
    });

    promise.then(function (_) {
        draw_table();
    }).catch(function (err) {
        console.log("can't add new user: " + err);
    })

    // request.always(function (data) {
    //     draw_table();
    // });
}

const form = document.getElementById('form');
if (form.attachEvent) {
    form.attachEvent("submit", processForm);
} else {
    form.addEventListener("submit", processForm);
}
