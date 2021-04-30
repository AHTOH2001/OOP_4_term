from django import template

register = template.Library()


@register.simple_tag
def get_field_name(model, field_name):
    for fld in model._meta.fields:
        if fld.name == field_name:
            return fld.verbose_name
    raise KeyError(f"model {model} doesn't have field {field_name}")
