$(document).ready(function () {
    draw_table()
});

function draw_table() {
    $('#table_body').html('');
    $.getJSON('http://127.0.0.1:5000/get_all', function (data) {
        $.each(data, function (key, val) {
            let row = "";
            spbu_identifier = 0
            msu_identifier = 10
            identifier = -1
            $.each(val, function (key, val) {
                if (val == "SPBU")
                    identifier = spbu_identifier

                if (val == "MSU")
                    identifier = msu_identifier

                identifier++
                if (identifier == spbu_identifier + 3){
                    if (val.startsWith("/"))
                        val = "https://spbu.ru" + val
                    if (val.slice(-1) == '/')
                        val = val.slice (0, -1)
                    val = "<a href=" + val + ">" + val + "</a>"
                }

                if (identifier == msu_identifier + 3){
                    if (val.startsWith("/"))
                        val = "https://msu.ru" + val
                    if (val.slice(-1) == '/')
                        val = val.slice (0, -1)
                    val = "<a href=" + val + ">" + val + "</a>"
                }
                
                row += '<td>' + val + '</td>';
            });
            $('#table_body').append('<tr>' + row + '</tr>');
        });
    });
}
