import struct
import copy
import sys

def write_color_data(bmp_dib, output_filename, color_name, subpixel_color):
    output_filename.write('const uint8_t {}[] PROGMEM ={{'.format(color_name))
    
    for x in xrange(0, bmp_dib['width']):
        for y in xrange(0, bmp_dib['height']):
            output_filename.write('{}'.format(subpixel_color[y][x]))
            if not (x == bmp_dib['width']-1 and y == bmp_dib['height']-1):
                output_filename.write(', ')
            else:
                output_filename.write('};\n')
        output_filename.write('\n')


def main():

    #Read a bitmap image into memory
    image = open(sys.argv[1], "rb")
    image_data = image.read()

    #Create a list of bitmap DIB header fields we want to read
    bmp_dib_fields = ('size','image_data_start','header_size','width','height','bpp','compression','image_size')

    #read data from header into a C-like structure:
    #<: little endian
    #I: unsigned int32
    #i: signed int32
    #h: signed int16
    #x: padding
    dib = struct.unpack("<I4xIIii2xhII", image_data[2:38])

    #Combine list of fields and the raw data into a dictionary
    bmp_dib = dict(zip(bmp_dib_fields, dib))

    #initialize a counter for reading pixel information from file
    data_counter = bmp_dib['image_data_start']

    #initialize three arrays for holding the red, green, and blue data
    red_data  = [[0 for x in xrange(bmp_dib['width'])] for y in xrange(bmp_dib['height'])]
    green_data = copy.deepcopy(red_data)
    blue_data = copy.deepcopy(red_data)

    #loop through the bitmap data and fill in the three arrays for each color
    for y in xrange(bmp_dib['height']-1, -1, -1):
        for x in xrange(0, bmp_dib['width']):
            #read red, green, blue values for pixel
            b,g,r = image_data[data_counter:data_counter+3]

            red_data[y][x] = ord(r)
            green_data[y][x] = ord(g)
            blue_data[y][x] = ord(b)
            
            data_counter += 3
        #account for padding in the bitmap
        data_counter += (4-((bmp_dib['width']*3)%4))%4
     
    #create C and H files for the image to link with firmware
    c_file = open("image.c", "w")
    h_file = open("image.h", "w")

    h_file.write('#ifndef IMAGE_H_\n')
    h_file.write('#define IMAGE_H_\n')
    h_file.write('#include <stdint.h>\n')
    h_file.write('extern const uint8_t imgDataR[];\n')
    h_file.write('extern const uint8_t imgDataG[];\n')
    h_file.write('extern const uint8_t imgDataB[];\n')
    h_file.write('#define IMG_WIDTH ({})\n'.format(bmp_dib['width']))
    h_file.write('#define IMG_HEIGHT ({})\n'.format(bmp_dib['height']))
    h_file.write('#endif\n')

    c_file.write('#include "image.h"\n')
    c_file.write('#include <avr/pgmspace.h>\n')
    write_color_data(bmp_dib, c_file, 'imgDataR', red_data)
    write_color_data(bmp_dib, c_file, 'imgDataG', green_data)
    write_color_data(bmp_dib, c_file, 'imgDataB', blue_data)
    
if __name__ == '__main__':
    main()