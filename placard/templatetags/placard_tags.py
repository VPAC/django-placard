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


from django.http import QueryDict
from django import template
import re

import placard.models

register = template.Library()

@register.simple_tag
def slave_name(slave_id):
    return placard.models.get_slave_name_by_id(slave_id)

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

@register.inclusion_tag('placard/pagination.html')
def pagination(request, page_obj):
    context = {}
    context['request'] = request
    context['page_obj'] = page_obj
    return context

class url_with_param_node(template.Node):
    def __init__(self, copy, changes):
        self.copy = copy
        self.changes = []
        for key, newvalue in changes:
            newvalue = template.Variable(newvalue)
            self.changes.append( (key,newvalue,) )

    def render(self, context):
        if 'request' not in context:
            return ""

        request = context['request']

        result = {}

        if self.copy:
            result = request.GET.copy()
        else:
            result = QueryDict("",mutable=True)

        for key, newvalue in self.changes:
            newvalue = newvalue.resolve(context)
            result[key] = newvalue

        return "?" + result.urlencode()

@register.tag
def url_with_param(parser, token):
    bits = token.split_contents()
    qschanges = []

    bits.pop(0)

    copy = False
    if bits[0] == "copy":
        copy = True
        bits.pop(0)

    for i in bits:
        try:
            key, newvalue = i.split('=', 1);
            qschanges.append( (key,newvalue,) )
        except ValueError:
            raise template.TemplateSyntaxError, "Argument syntax wrong: should be key=value"
    return url_with_param_node(copy, qschanges)

