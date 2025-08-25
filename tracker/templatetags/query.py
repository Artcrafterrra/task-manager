from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def url_with_query(context, base_url, **kwargs):

    request = context["request"]
    params = request.GET.copy()
    for k, v in kwargs.items():
        if v is None:
            params.pop(k, None)
        else:
            params[k] = v
    query = params.urlencode()
    return f"{base_url}?{query}" if query else base_url