from django_telegram.bot.renderers.qs2md import render_as_list


def test_render_as_list_less_10():
    data = render_as_list([{
        'id': 'id',
        'name': 'name',
        'status': 'pending',

    }])

    assert data == '``` Total: 1\n- name (id): pending\n ```'


def test_render_as_list_more_10():
    values = []
    for _i in range(1, 15):
        values.append({
            'id': _i,
            'name': f'{_i}_name',
            'status': f'{_i}_status',
        })

    data = render_as_list(values)

    assert data.startswith('``` Total: 14')
    assert data.endswith('... and 4 more ...```')
