import string
import math

def initialize_mean_bitmap():
    pass

def make_empty_bitmap(number_of_pixels):
    row_pixel_count = int(math.sqrt(number_of_pixels))
    bitmap = [[0 for x in xrange(row_pixel_count)] for x in xrange(row_pixel_count)] 
    return bitmap

def get_raw_sequence_bitmap(sequence, word_length, alphabet_size, number_of_pixels):
    #theres a way of mathematically calculating how many pixels we need, i just havent figured it out yet (annoying!)
    bitmap = make_empty_bitmap(number_of_pixels)
    for word_pos in range(len(sequence) - word_length + 1):
        word = sequence[word_pos:word_pos + word_length]
        pixel_pos = get_pixel(word)
        bitmap_row = pixel_pos[0]
        bitmap_col = pixel_pos[1]
        bitmap[bitmap_row][bitmap_col] += 1
    return bitmap

def get_letter_key_value(letter):
    return string.lowercase.index(letter)

def get_pixel(word):
    l = len(word)
    col = 0
    row = 0
    for n in range(l):
        letter = word[n]
        kn = get_letter_key_value(letter)
        col += (kn * 2 ** (l - n - 1)) % 2 ** (l - n)
        row += (kn // 2) * 2 ** (l - n - 1)
    return [row, col]

#print(get_raw_sequence_bitmap("ffffffffffffff",2, 4, 1024))