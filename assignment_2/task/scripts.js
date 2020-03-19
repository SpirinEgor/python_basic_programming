"use strict";

$(document).ready(() => {
    window.row_class_no_act = 'list-group-item d-flex justify-content-between align-items-center'
    window.row_class = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center'

    let pager = `
        <a class="${window.row_class_no_act} pager">
            <span class="prev">Previous</span>
            <span class="progress">No pages</span>
            <span class="next">Next</span>
        </a>
    `

    $('body').html(`
        <div class="container mt-5">
        <input class="form-control form-control-lg" type="text" placeholder="Search" id='search'>
        <div class="container mt-5">
            <div class="list-group">
                ${pager}
                <div class='title-list'></div>
                ${pager}
            </div>
        </div>
        <div class="mt-5"></div>
        </div>
    `)

    let change_page_size = size => {
        window.page_size = size

        let list = $(`<div class="title-list"></div>`)

        let row = `
            <div class="title-row">
                <a class="${window.row_class} title-info">
                    <span><img height=100px class="title-img"></span>
                    <span style="color:black" class="title-name"></span>
                    <span class="badge badge-primary badge-pill title-count"></span>
                </a>
                <div style="display:none" class="title-chapters"></div>
            </div>
        `

        for (let i = 0; i < size; i++) {
            list.append(row)
        }

        list.find('.title-info').each((index, elem) => {
            $(elem).click(() => {
                $(elem).toggleClass('active')
                $(elem).siblings().toggle('display')
            })
        })

        $('.title-list').replaceWith(list)

        changer()
    }

    let changer = () => {
        window.search_string = $('#search').val()

        window.page_no = 1
        window.table_size = 0

        $.getJSON(`/get/${window.search_string}/size`, json => {
            window.table_size = json.size

            window.pages_cnt = Math.ceil(window.table_size / window.page_size)

            draw_table()
        })
    }

    $('.next').click(() => {
        if (window.pages_cnt > window.page_no) {
            window.page_no++
            draw_table()
        }
    })

    $('.prev').click(() => {
        if (0 < window.page_no) {
            window.page_no--
            draw_table()
        }
    })

    $('#search').change(changer)

    change_page_size(20)
    changer()
});

let draw_table = () => {
    $('.progress').html(`${window.page_no} / ${window.pages_cnt}`)
    $('#list').html('')

    $.getJSON(`/get/${window.search_string}/${window.page_size}/${window.page_no * window.page_size - window.page_size}`, draw_json)
}

let draw_json = json => {
    $('.title-row').each((index, elem) => {
        let info = json[index]

        $(elem).find('.title-img').attr('src', info.cover)
        $(elem).find('.title-name').html(info.title)
        $(elem).find('.title-count').html(info.chapters.length)

        let chapters = $(`<div style="display:none" class="title-chapters"></div>`)

        for (let chapter of info.chapters) {
            let ch_el = $(`
                <a class="${window.row_class}" href="${chapter.link}" style="color:black">
                    Volume ${chapter.volume} Chapter ${chapter.chapter}
                </a>
            `)
            chapters.append(ch_el)
        }

        $(elem).find('.title-chapters').replaceWith(chapters)
    })
}
