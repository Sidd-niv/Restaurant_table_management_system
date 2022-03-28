from fpdf import FPDF


class PDF(FPDF):
    def header(self):
        # add logo in pdf
        self.image('static/images/Fynd.jpeg', 10, 8, 25)
        # font
        self.set_font('times', 'BU', 30)
        # Title tp the page
        self.cell(0, 10, "Hunger Fest", ln=True, align="C")
        # line break
        self.ln(20)

    # page footer
    def footer(self):
        # set position for footer
        self.set_y(-15)
        # set font
        self.set_font("times", "B", 10)
        # set page number
        self.cell(0, 10, "Page no.1", align="C")

def make_pdf(content_of_pdf: list):
    pdf = PDF(orientation="P", format="A4")
    pdf.add_page()  # it will add a page
    pdf.set_line_width(0.0)
    pdf.line(5.0, 5.0, 205.0, 5.0)  # top one
    pdf.line(5.0, 292.0, 205.0, 292.0)  # bottom one
    pdf.line(5.0, 5.0, 5.0, 292.0)  # left one
    pdf.line(205.0, 5.0, 205.0, 292.0)  # right one
    pdf.set_font(family="times", size=16)
    for line in content_of_pdf:
        pdf.cell(0, 10, txt=line, ln=True)
    pdf.output('Invoice.pdf', 'F')

make_pdf(["nsafnwof", "anfasnhfon"])

