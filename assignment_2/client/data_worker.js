$(document).ready(function () {
    draw_table()
    document.getElementById('load-src1').onclick = function(){
        document.getElementById('load-src1').style.background = "red";
        postFromSrc("http://127.0.0.1:5000/src_1");
    }
    document.getElementById('load-src2').onclick = function(){
        postFromSrc("http://127.0.0.1:5000/src_2");
    }
    document.getElementById('load-src3').onclick = function(){
        postFromSrc("http://127.0.0.1:5000/src_3"); 
    }
    document.getElementById('delete-all').onclick = function(){
        postFromSrc("http://127.0.0.1:5000/delete_all");
    }
});

function draw_table() {
    $('#table_body tr').remove()
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

function postFromSrc(url) {
    let promise = new Promise(function(resolve, reject) {
        $.get( url, function( data ) {
            draw_table()
            document.getElementById('load-src1').style.background = "#007bff";
          });
    });
}
