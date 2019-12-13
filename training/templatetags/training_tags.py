from django import template
register = template.Library()


@register.filter
def skill_score(List, i):
    if List[i] == List[-1]:
        result = "Recommended!"
    else:
        result = ""

    return result

@register.filter
def star_times(number):
    return range(number)

@register.filter
def star_left(number):
    return range(4 - number)

@register.filter
def to_ordinal(numb):
    if numb < 20: #determining suffix for < 20
        if numb == 1:
            suffix = 'st'
        elif numb == 2:
            suffix = 'nd'
        elif numb == 3:
            suffix = 'rd'
        else:
            suffix = 'th'
    else:   #determining suffix for > 20
        tens = str(numb)
        tens = tens[-2]
        unit = str(numb)
        unit = unit[-1]
        if tens == "1":
           suffix = "th"
        else:
            if unit == "1":
                suffix = 'st'
            elif unit == "2":
                suffix = 'nd'
            elif unit == "3":
                suffix = 'rd'
            else:
                suffix = 'th'
    return str(numb)+ suffix