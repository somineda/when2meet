with
    url_code := <str>$url_code #인자로 받음
select (
    insert Meeting {
        url_code := url_code,
    }
) {url_code}
