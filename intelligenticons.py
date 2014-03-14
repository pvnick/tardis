import string
import array 

class IntelligentIcon:
    alphabet_size = 8
    mean_bitmap = []
    bitmaps = []

    def initialize_mean_bitmap(self):
        pass

    def make_empty_bitmap(self, word_length):
        row_pixel_count = word_length * (self.alphabet_size + 1)
        bitmap = [[0 for x in xrange(row_pixel_count)] for x in xrange(row_pixel_count)] 
        return bitmap

    def add_raw_sequence_bitmap(self, word_length, sequence):
        bitmap = self.make_empty_bitmap(word_length)
        for word_pos in range(len(sequence) - word_length + 1):
            word = sequence[word_pos:word_pos + word_length]
            pixel_pos = self.get_pixel(word)
            bitmap_row = pixel_pos[0]
            bitmap_col = pixel_pos[1]
            bitmap[bitmap_row][bitmap_col] += 1
        self.bitmaps.append(bitmap)

    def get_letter_key_value(letter):
        return string.lowercase.index(letter)

    def get_pixel(self, word):
        l = len(word)
        col = 0
        row = 0
        for n in range(l):
            letter = word[n]
            kn = self.get_letter_key_value(letter)
            col += (kn * 2 ** (l - n - 1)) % 2 ** (l - n)
            row += (kn // 2) * 2 ** (l - n - 1)
        return [row, col]

#i = IntelligentIcon()
#i.add_raw_sequence_bitmap(3, "aaabbbcccdddeeefffggghhh")
#print(i.bitmaps)
#pix = get_pixel("ta")
