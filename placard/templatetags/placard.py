# Copyright 2012 VPAC
#
# This file is part of django-placard.
#
# django-placard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django-placard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with django-placard  If not, see <http://www.gnu.org/licenses/>.


from django import template
import re

register = template.Library()

@register.simple_tag
def active(request, pattern):
    if re.search('^%s/%s' % (request.META['SCRIPT_NAME'], pattern), request.path):
        return 'active'
    return ''

@register.inclusion_tag('placard/inlineformfield.html')
def inlineformfield(field1, field2, field3=None):
    return locals()

@register.inclusion_tag('placard/formfield.html')
def formfield(field):
    context = {}

    label_class_names = []
    if field.field.required:
        label_class_names.append('required')

    widget_class_name = field.field.widget.__class__.__name__.lower()
    if widget_class_name == 'checkboxinput':
        label_class_names.append('vCheckboxLabel')

    class_str = label_class_names and u' class="%s"' % u' '.join(label_class_names) or u''

    context['class'] = class_str
    context['formfield'] = field
    context['type'] = widget_class_name
    return context
