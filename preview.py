import pixie
import csv


def make_preview(logFileName):
    file = open('logs/' + logFileName, 'r', newline='')
    logReader = csv.reader(file, delimiter=',') 
    xRange = [0,0]
    yRange = [0,0]
    for row in logReader:
        if len(row) == 5 and row[0] != 'x (mm)':
            if float(row[0]) < xRange[0]:
                xRange[0] = float(row[0])
            elif float(row[0]) > xRange[1]:
                xRange[1] = float(row[0])
            if float(row[1]) < yRange[0]:
                yRange[0] = float(row[1])
            elif float(row[1]) > yRange[1]:
                yRange[1] = float(row[1])
    file.close()
    xRange[0] -= 0.15
    xRange[1] = max(xRange[1], 0.55)
    yRange[0] -= 0.15
    yRange[1] += 0.15
    print(xRange)
    print(yRange)
    pix_per_mm = 1000 # pixels per mm

    width = int((xRange[1] - xRange[0])* pix_per_mm)
    height = int((yRange[1] - yRange[0])* pix_per_mm)

    image = pixie.Image(width, height)
    image.fill(pixie.Color(1, 1, 1, 1))


    font = pixie.read_font("Roboto-Regular_1.ttf")
    font.size = 160

    image.fill_text(
        font,
        '.ORIGIN',
        bounds = pixie.Vector2(font.size*10,font.size),
        transform = pixie.translate(-xRange[0] * pix_per_mm,(height + yRange[0] * pix_per_mm)-font.size)
    )

    font.size = 14

    def formatter(row):
        if float(row[4]) >= 1:
            return '%s\n%ss total\n%.2fs/pix' % (row[2], row[3], float(row[4]))
        elif float(row[4]) >= 0.001:
            return '%s\n%ss total\n%.2fms/pix' % (row[2], row[3], float(row[4])*1e3)
        else:
            return '%s\n%ss total\n%.2f\u03bcs/pix' % (row[2], row[3], float(row[4])*1e6)


    file = open('logs/' + logFileName, 'r', newline='')
    logReader = csv.reader(file, delimiter=',')
    for row in logReader:
        if len(row) == 5 and row[0] != 'x (mm)':
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
                -xRange[0] * pix_per_mm + float(row[0]) * pix_per_mm, (height + yRange[0] * pix_per_mm) - float(row[1]) * pix_per_mm - 4*font.size)
            )
    file.close()

    image.write_file("images/previews/preview_" + logFileName[:-4] + ".png")

make_preview('silicon1.csv')