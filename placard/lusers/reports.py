from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.template import defaultfilters
import datetime
from cStringIO import StringIO
from decimal import Decimal
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.lib.units import cm
from reportlab.lib import colors
from placard.client import LDAPClient

def user_list_pdf(request):
    conn = LDAPClient()
    user_list = conn.get_users()
    today = datetime.date.today()
    response = HttpResponse(mimetype='application/pdf')
    
    def myFirstPage(canvas, doc):
        # Header
        canvas.saveState()

        #ratio = n.get_photo_width() / _width
        #canvas.drawImage("%s/img/logo.jpg" % settings.MEDIA_ROOT, 35, 710)#, width=97, height=50)
        #canvas.setFillColorRGB(1,1,1)
        canvas.setFont("Helvetica", 20)   
        canvas.drawString(100, 800, 'staff phone list')        

        # Footer
        canvas.setFont('Times-Roman',9)
        canvas.drawCentredString(PAGE_WIDTH /2,30, "VPAC")
        canvas.drawString(540, 30, "Page %d" % doc.page)
        canvas.drawString(50,30, defaultfilters.date(today, "j, F Y"))
        canvas.restoreState()

    def myLaterPages(canvas, doc):
        canvas.saveState()
        
        # Footer
        canvas.setFont('Times-Roman',9)
        canvas.drawCentredString(PAGE_WIDTH /2,30, "VPAC")
        canvas.drawString(540, 30, "Page %d" % doc.page)
        canvas.drawString(50,30, defaultfilters.date(today, "j, F Y"))
        canvas.restoreState()


    fname = "phone_list.pdf"
    response['Content-Disposition'] = 'attachment; filename= ' + fname
    

    data_dic = [[str(x.cn), str(getattr(x, 'telephoneNumber', '')), str(getattr(x, 'mobile', '')), str(getattr(x, 'mail', ''))] for x in user_list ]

    data_list = list(data_dic)
    
    #PAGE_HEIGHT = landscape(A4)[1]
    #PAGE_WIDTH = landscape(A4)[0]
    PAGE_HEIGHT = portrait(A4)[1]
    PAGE_WIDTH = portrait(A4)[0]
    

    buffer = StringIO()
    doc = SimpleDocTemplate(buffer)
    #doc.pagesize = landscape(A4)
    doc.pagesize = portrait(A4)
    doc.topMargin = 50
    story = []
    category = ParagraphStyle(
        name="category",
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=colors.Color(0.2,0.2,0.4),
        spaceBefore=20,spaceAfter=10
    )
    row_colours = [ colors.white, colors.lavenderblush, colors.white, colors.lavenderblush ]
    table_style = TableStyle(
        [('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
         ('BOX', (0,0), (-1,-1), 0.25, colors.black),
        # ('ALIGN',(0,0), (-1,0),'CENTER'),
        # ('LINEBELOW',(2,-2),(-1,-2),0.5,colors.black),
        # ('LINEBELOW',(0,0),(-1,0),0.5,colors.black),
        # ('FONT',(0,0),(-1,0),"Helvetica-Bold"),
         #('ALIGN', (2,-3), (2,-1), 'RIGHT'),
        # ('ALIGN', (2,0), (2,-1), 'RIGHT'),
        # ('ALIGN', (0,0), (0,-1), 'RIGHT'),
        # ('ALIGN', (3,0), (3,-1), 'RIGHT'),
        # ('RIGHTPADDING', (2,0), (2,-1), 100),
        # ('FONT', (2,-3), (2,-1), "Helvetica-Bold"),
        # ('LINEABOVE',(0,-3),(-1,-3),0.5,colors.black),
         #('ROWBACKGROUNDS',(0,1), (-1,-1), row_colours),
         #('BACKGROUND', (0,0), (-1,0), colors.lavender),
         ]
    )

    # build the tables per unit
    # table
    item_list = [[ 'name','telephone', 'mobile', 'email']]
    #temp_list = data_list
        # clean e[1], by removing category.
        #temp_list = [seq[1:] for seq in temp_list]
    item_list.extend(data_list)
        # draw table
    t = Table(item_list)#, colWidths=[50,380,10,10])
    t.hAlign = 'LEFT'
    t.setStyle(table_style)
    story.append(t)
       # t.setStyle(table_style)
    doc.build(story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)
        
    # Close the PDF object cleanly.
    pdf = buffer.getvalue()
    buffer.close()
    # Get the value of the StringIO buffer and write it to the response.
    response.write(pdf)
    return response
