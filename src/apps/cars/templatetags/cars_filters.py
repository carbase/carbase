from django import template

register = template.Library()


@register.filter
def is_all_taxes_paid(car):
    for tax in car.tax_set.all():
        if not tax.is_paid:
            return False
    return True


@register.filter
def is_all_fines_paid(car):
    for fine in car.fine_set.all():
        if not fine.is_paid:
            return False
    return True
