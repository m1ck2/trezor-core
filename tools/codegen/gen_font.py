#!/usr/bin/env python3

# script used to generate /embed/extmod/modtrezorui/font_*_*.c


import freetype

MIN_GLYPH = ord(' ')
MAX_GLYPH = ord('~')

FONT_BPP = 4

# metrics explanation: https://www.freetype.org/freetype2/docs/glyphs/metrics.png


def process_face(name, style, size):
    print('Processing ... %s %s %s' % (name, style, size))
    face = freetype.Face('/usr/share/fonts/truetype/%s-%s.ttf' % (name, style))
    face.set_pixel_sizes(0, size)
    fontname = '%s_%s_%d' % (name.lower(), style.lower(), size)
    with open('font_%s.h' % fontname, 'wt') as f:
        f.write('#include <stdint.h>\n\n')
        f.write('extern const uint8_t * const Font_%s_%s_%d[%d + 1 - %d];\n' % (name, style, size, MAX_GLYPH, MIN_GLYPH))
    with open('font_%s.c' % fontname, 'wt') as f:
        f.write('#include "font_%s.h"\n\n' % fontname)
        f.write('// first two bytes are width and height of the glyph\n')
        f.write('// third, fourth and fifth bytes are advance, bearingX and bearingY of the horizontal metrics of the glyph\n')
        f.write('// rest is packed 4-bit glyph data\n\n')
        for i in range(MIN_GLYPH, MAX_GLYPH + 1):
            c = chr(i)
            face.load_char(c, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_NORMAL)
            bitmap = face.glyph.bitmap
            metrics = face.glyph.metrics
            assert metrics.width // 64 == bitmap.width
            assert metrics.height // 64 == bitmap.rows
            assert metrics.horiAdvance % 64 == 0
            assert metrics.horiBearingX % 64 == 0
            assert metrics.horiBearingY % 64 == 0
            assert bitmap.width == bitmap.pitch
            assert len(bitmap.buffer) == bitmap.pitch * bitmap.rows
            print('Loaded glyph "%c" ... %d x %d @ %d grays (%d bytes)' % (c, bitmap.width, bitmap.rows, bitmap.num_grays, len(bitmap.buffer)))
            f.write('/* %c */ static const uint8_t Font_%s_%s_%d_glyph_%d[] = { %d, %d, %d, %d, %d' % (c, name, style, size, i, bitmap.width, bitmap.rows, metrics.horiAdvance // 64, metrics.horiBearingX // 64, metrics.horiBearingY // 64))
            buf = list(bitmap.buffer)
            if len(buf) > 0:
                if FONT_BPP == 2:
                    for _ in range(4 - len(buf) % 4):
                        buf.append(0)
                    buf = [((a & 0xC0) | ((b & 0xC0) >> 2) | ((c & 0xC0) >> 4) | ((d & 0xC0) >> 6)) for a, b, c, d in [buf[i:i + 4] for i in range(0, len(buf), 4)]]
                elif FONT_BPP == 4:
                    if len(buf) % 2 > 0:
                        buf.append(0)
                    buf = [((a & 0xF0) | (b >> 4)) for a, b in [buf[i:i + 2] for i in range(0, len(buf), 2)]]
                f.write(', ' + ', '.join(['%d' % x for x in buf]))
            f.write(' };\n')
        f.write('\nconst uint8_t * const Font_%s_%s_%d[%d + 1 - %d] = {\n' % (name, style, size, MAX_GLYPH, MIN_GLYPH))
        for i in range(MIN_GLYPH, MAX_GLYPH + 1):
            f.write('    Font_%s_%s_%d_glyph_%d,\n' % (name, style, size, i))
        f.write('};\n')


process_face('Roboto', 'Regular', 20)
process_face('Roboto', 'Bold', 20)
process_face('RobotoMono', 'Regular', 20)
