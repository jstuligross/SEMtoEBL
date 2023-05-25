import pixie
import csv

pix_per_mm = 1000 # pixels per mm (the code doesn't like it when we do larger numbers like 1500 for this)


def formatter(row):
    if float(row[4]) >= 1:
        return '%s\n%ss total\n%.2fs/pix\n%sx mag' % (row[2], row[3], float(row[4]), row[5])
    elif float(row[4]) >= 0.001:
        return '%s\n%ss total\n%.2fms/pix\n%sx mag' % (row[2], row[3], float(row[4])*1e3, row[5])
    else:
        return '%s\n%ss total\n%.2f\u03bcs/pix\n%sx mag' % (row[2], row[3], float(row[4])*1e6, row[5])


def make_preview(logFileName):
    '''
    This function produces a map of the photoresist. It uses the CSV log file 
    produced during lithography to create a PNG file which shows which images 
    are where on the chip. The images are not the right sizes, but they're in 
    the right places.

    The location of the origin (meaning the dot of scratched-off PMMA) is 
    indicated by the period in ".ORIGIN". There is a slight margin (0.15mm) 
    around the map to avoid cutting off the information. If more components are 
    added, this margin might need to be extended.
    '''
    
    # Find the dimensions of the lithograph
    file = open('logs/' + logFileName + '.csv', 'r', newline='')
    logReader = csv.reader(file, delimiter=',') 
    xRange = [0,0,0]
    yRange = [0,0,0]
    ct = 0
    row_length = 0
    closest_to_og = 0
    for row in logReader:
        if len(row) > 1 and row[0] != 'x (mm)': # if not a date and not a header
            if ct == 0:
                xRange = 3*[float(row[0])]
                yRange = 3*[float(row[1])]
                closest_to_og = float(row[0])**2 + float(row[1])**2
                ct += 1
            if float(row[0]) < xRange[0]:
                xRange[0] = float(row[0])
            elif float(row[0]) > xRange[1]:
                xRange[1] = float(row[0])
            if float(row[1]) < yRange[0]:
                yRange[0] = float(row[1])
            elif float(row[1]) > yRange[1]:
                yRange[1] = float(row[1])
            if float(row[0])**2 + float(row[1])**2 < closest_to_og:
                xRange[2] = float(row[0])
                yRange[2] = float(row[1])
    file.close()

    # endpt1 = [-xRange[0] * pix_per_mm, (yRange[0]) * pix_per_mm]
    # endpt2 = [-0.9*xRange[0] * pix_per_mm, (yRange[0]) * pix_per_mm]
    # add margins
    xRange[0] = min(xRange[0], -0.15) - 0.15
    xRange[1] = max(xRange[1], 0.55) + 0.15 # 0.55 because of the word "ORIGIN"
    yRange[0] = min(yRange[0], -0.15) - 0.15
    yRange[1] = max(yRange[1], 0.15) + 0.15


    width = int((xRange[1] - xRange[0])* pix_per_mm)
    height = int((yRange[1] - yRange[0])* pix_per_mm)

    endpt1 = [-xRange[0] * pix_per_mm, height + (0.15 - abs(yRange[2] - yRange[0])) * pix_per_mm]
    endpt2 = [endpt1[0] - 0.1*pix_per_mm, endpt1[1]]

    # endpt1[1] += height
    # endpt2[1] += height
    print(width,height)
    print(endpt1)
    print(endpt2)

    image = pixie.Image(width, height)
    image.fill(pixie.Color(1, 1, 1, 1))

    
    paint = pixie.Paint(pixie.SOLID_PAINT)
    paint.color = pixie.parse_color("#000000")

    ctx = image.new_context()
    ctx.stroke_style = paint
    ctx.line_width = pix_per_mm/100

    tick_to_linewidth = 1.5
    ctx.stroke_segment(*endpt1, *endpt2)
    ctx.stroke_segment(endpt1[0], endpt1[1] + ctx.line_width*tick_to_linewidth, endpt1[0], endpt1[1] - ctx.line_width*tick_to_linewidth)
    ctx.stroke_segment(endpt2[0], endpt2[1] + ctx.line_width*tick_to_linewidth, endpt2[0], endpt2[1] - ctx.line_width*tick_to_linewidth)
    ctx.stroke_segment((endpt1[0] + endpt2[0])/2.0, (endpt1[1] + endpt2[1])/2.0 + ctx.line_width*tick_to_linewidth*0.75, (endpt1[0] + endpt2[0])/2.0, (endpt1[1] + endpt2[1])/2.0 - ctx.line_width*tick_to_linewidth*0.75)
    # ctx.stroke_segment(endpt2[0], endpt2[1] + ctx.line_width*3, endpt2[0], endpt2[1] - ctx.line_width*3)
    font = pixie.read_font("Roboto-Regular_1.ttf")
    font.size = int(0.16 * pix_per_mm)

    image.fill_text(
        font,
        '.ORIGIN',
        bounds = pixie.Vector2(font.size*10,font.size),
        transform = pixie.translate(-xRange[0] * pix_per_mm,(height + yRange[0] * pix_per_mm)-font.size)
    )

    font.size = int(0.02 * pix_per_mm)

    image.fill_text(
        font,
        '100\u03bcm',
        bounds = pixie.Vector2(font.size*10,font.size),
        transform = pixie.translate((endpt1[0] + endpt2[0])/2.0 - font.size*1.2, endpt1[1] + font.size)
    )

    font.size = int(0.014 * pix_per_mm)

    file = open('logs/' + logFileName + '.csv', 'r', newline='')
    logReader = csv.reader(file, delimiter=',')
    for row in logReader:
        if len(row) > 1 and row[0] != 'x (mm)':
            pattern = pixie.read_image("images/" + row[2])
            image.draw(
                pattern,
                pixie.translate(-xRange[0] * pix_per_mm + float(row[0]) * pix_per_mm, (height + yRange[0] * pix_per_mm) - float(row[1]) * pix_per_mm) *
                pixie.scale(pix_per_mm/(10*pattern.width),pix_per_mm/(10*pattern.width))
            )
            image.fill_text(
                font,
                formatter(row),
                bounds=pixie.Vector2(font.size*200, font.size*200),
                transform = pixie.translate(
                -xRange[0] * pix_per_mm + float(row[0]) * pix_per_mm, (height + yRange[0] * pix_per_mm) - float(row[1]) * pix_per_mm - 5*font.size)
            )
    file.close()

    image.write_file("images/previews/" + logFileName + ".png")

