$(document).ready(() => {
    let changer = async () => {
        search_string = $('#search').val()

        page_size = 20
        page_no = 1
        table_size = 0

        await $.getJSON(`/get/${search_string}/size`, json => {
            table_size = json.size
        })

        pages_cnt = Math.trunc(table_size / page_size)
        if (table_size % page_size != 0)
            pages_cnt += 1

        draw_table()
    }

    $('#search').change(changer)
    changer()
});

let draw_table = () => {
    $('#list').html('')

    pager = $(`<a class="list-group-item d-inline-flex justify-content-between align-items-center"></a>`)
    prev = $(`<span class="">Previous</span>`)
    next = $(`<span class="">Next</span>`)
    progress = $(`<span class="">${page_no} / ${pages_cnt}</span>`)

    pager.append(prev)
    pager.append(progress)
    pager.append(next)
    
    next.click(() => {
        if (pages_cnt > page_no) {
            page_no++
            draw_table()
        }
    })
    
    prev.click(() => {
        if (0 < page_no) {
            page_no--
            draw_table()
        }
    })

    $('#list').append(pager)

    $.getJSON(`/get/${search_string}/${page_size}/${page_no * page_size - page_size}`, json => {
        $.each(json, (_, val) => {
            let row_elem = $(`<div></div>`)
            let base = $(`<a class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"></a>`)
            let chapters = $(`<div></div>`)
            chapters.hide()

            base.click(e => {
                base.toggleClass('active')
                chapters.toggle('display')
            })

            img = $(`<span><img src="${val.cover}" height=100px></span>`)
            link = $(`<span> ${val.title} </span>`)
            //link.attr('href', val.link)
            link.css('color', 'black')
            base.append(img)
            base.append(link)
            base.append(`<span class="badge badge-primary badge-pill">${val.chapters.length}</span>`)

            for (chapter of val.chapters) {
                let ch_el = $(`<a
                    class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
                    href="${chapter.link}">
                    Volume ${chapter.volume} Chapter ${chapter.chapter}</a>`)
                ch_el.css('color', 'black')
                chapters.append(ch_el)
            }

            row_elem.append(base)
            row_elem.append(chapters)

            $('#list').append(row_elem);
        })
    })
}
