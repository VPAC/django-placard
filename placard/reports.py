# Copyright 2010 VPAC
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


from django.http import HttpResponse
from django.template import defaultfilters

import datetime
from cStringIO import StringIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib import colors

import placard.models

PAGE_WIDTH = portrait(A4)[0]    

def user_list_pdf(request):
    if request.GET.has_key('group'):
        try:
            group = placard.models.group.objects.get(gidNumber=request.GET['group'])
        except  placard.models.group.DoesNotExist:
            group = None
    else:
        group = None

    if group is not None:
        user_list = group.secondary_accounts.all()
    else:
        user_list = placard.models.account.objects.all()

    today = datetime.date.today()
    response = HttpResponse(mimetype='application/pdf')
    
    def myFirstPage(canvas, doc):
        # Header
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.drawCentredString(PAGE_WIDTH/2, 30, "VPAC")
        canvas.drawString(540, 30, "Page %d" % doc.page)
        canvas.drawString(50, 30, defaultfilters.date(today, "j, F Y"))
        canvas.restoreState()

    def myLaterPages(canvas, doc):
        canvas.saveState()
        
        # Footer
        canvas.setFont('Times-Roman', 8)
        canvas.drawCentredString(PAGE_WIDTH/2, 30, "VPAC")
        canvas.drawString(540, 30, "Page %d" % doc.page)
        canvas.drawString(50, 30, defaultfilters.date(today, "j, F Y"))
        canvas.restoreState()


    fname = "phone_list.pdf"
    response['Content-Disposition'] = 'attachment; filename= ' + fname
    

    data_dic = [[str(x.cn), str(getattr(x, 'telephoneNumber', '')), str(getattr(x, 'mobile', '')), str(getattr(x, 'mail', '')), str(getattr(x, 'l', ''))] for x in user_list ]

    data_list = list(data_dic)
    
    buffer = StringIO()
    doc = SimpleDocTemplate(buffer)
    doc.pagesize = portrait(A4)
    doc.topMargin = 40
    story = []

    table_style = TableStyle(
        [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
         ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
         ]
    )

    # build the tables per unit
    # table
    item_list = [[ 'Name', 'Telephone', 'Mobile', 'Email', 'Location']]
    item_list.extend(data_list)
    t = Table(item_list)
    t.hAlign = 'LEFT'
    t.setStyle(table_style)
    story.append(t)
    doc.build(story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)
        
    # Close the PDF object cleanly.
    pdf = buffer.getvalue()
    buffer.close()
    # Get the value of the StringIO buffer and write it to the response.
    response.write(pdf)
    return response
