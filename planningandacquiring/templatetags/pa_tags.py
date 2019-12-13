from django import template
register = template.Library()

@register.filter
def index(List, i):

    return List[int(i)]


@register.filter
def name(List, i):
    item = List[int(i)]
    name = item.name

    return name


@register.filter
def breed(List, i):
    item = List[int(i)]
    breed = item.breed

    return breed


@register.filter
def color(List, i):
    item = List[int(i)]
    color = item.color

    return color

@register.filter
def age(List, i):
    item = List[int(i)]
    age = item.age

    return age

@register.filter
def litter_no(List, i):
    item = List[int(i)]
    litter_no = item.litter_no

    return litter_no

@register.filter
def capability(List, i):
    item = List[int(i)]
    capability = item.capability

    return capability

