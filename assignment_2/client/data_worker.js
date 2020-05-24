$(document).ready(function () {
    draw_tree();
});

function subtree_to_html(subtree) {
    if (typeof(subtree) != 'object')
        return subtree.toString();
    let res = '';
    for (let key in subtree)
        res += '<li>' + key + ': ' + subtree_to_html(subtree[key]) + '</li>';
    return '<ul type="none">' + res + '</ul>';
}

function draw_tree() {
    $('#tree').html('');
    $.getJSON('http://127.0.0.1:5000/get_accounts', function (data) {
        $.each(data, function (key, val) {
            $('#tree').append(
                '<ul type="none"><li>' +
                    val['name'] + ' (' + val['screen_name'] + '): ' +
                    subtree_to_html(val['profile']) +
                '</li></ul>');
        });
    });
}

function processForm(e) {
    if (e.preventDefault) e.preventDefault();
    let screen_name = $('#screen_name')[0].value;
    $.get('http://127.0.0.1:5000/add_account?screen_name=' + screen_name,
        function (data) {
            if (data == 'OK') {
                draw_tree();
            } else {
                console.log("Can't add new account");
            }
        });
}

const form = document.getElementById('form');
if (form.attachEvent) {
    form.attachEvent("submit", processForm);
} else {
    form.addEventListener("submit", processForm);
}
