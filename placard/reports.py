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

import placard.views

PAGE_WIDTH = portrait(A4)[0]    

class PdfResponseMixin(placard.views.AccountList):
    response_class = HttpResponse

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        response_kwargs['content_type'] = 'application/pdf'
#        response_kwargs = ['Content-Disposition'] = 'attachment; filename= ' + self.fname
        return self.response_class(
            self.convert_context_to_pdf(context),
            **response_kwargs
        )

class PdfAccountList(PdfResponseMixin, placard.views.AccountList):
#    fname = "phone_list.pdf"
    paginate_by = None

    def convert_context_to_pdf(self, context):
        user_list = context['user_list']

        today = datetime.date.today()

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
             ('LINEABOVE',(0,0),(-1,0),1,colors.black),
             ('LINEBELOW',(0,0),(-1,0),1,colors.black),
             ('LINEBELOW',(0,-1),(-1,-1),1,colors.black),
             ('LINEBEFORE',(0,0),(0,-1),1,colors.black),
             ('LINEAFTER',(-1,0),(-1,-1),1,colors.black),
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
        return pdf
