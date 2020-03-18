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

function parsingCitilinkForm() {
        let promise = new Promise(function(resolve, reject) {
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: "http://127.0.0.1:5000/parse_citilink",
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
    });
}

function parsingWildberriesForm() {
        let promise = new Promise(function(resolve, reject) {
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: "http://127.0.0.1:5000/parse_wildberries",
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
        console.log("can't parse site: " + err);
    });
}

const form = document.getElementById("btn-handler");
if (form.attachEvent) {
    form.attachEvent("submit", function (e){
        if (e.target.id === "citilink"){
            parsingCitilinkForm(e);
        }
        else parsingWildberriesForm(e);
    });
} else {
    form.addEventListener("submit", function (e){
        if (e.target.id === "citilink"){
            parsingCitilinkForm(e);
        }
        else parsingWildberriesForm(e);
    });
}
