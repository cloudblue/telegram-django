def render_as_list(queryset):
    qs_size = len(queryset)
    if qs_size <= 10:
        data_string = '\n'.join(['- {name} ({id}): {status}\n'.format(
            name=i["name"], id=i["id"], status=i["status"],
        ) for i in queryset])
        return f'``` Total: {qs_size}\n{data_string} ```'
    else:
        data_string = '\n'.join(['- {name} ({id}): {status}\n'.format(
            name=i["name"], id=i["id"], status=i["status"],
        ) for i in queryset[0:9]])
        return f'``` Total: {qs_size}\n{data_string}\n- ... and {qs_size - 10} more ...```'
