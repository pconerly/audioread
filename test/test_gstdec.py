import os
import unittest
import audioread

gstAvailible = audioread._gst_available()
if gstAvailible:
    from audioread import gstdec


testFilename = os.path.abspath(os.path.join('test', 'fixtures', 'sample.mp3'))
rowLookup = [
    b'\x01\x00',
    b'w\x00',
    b'\xf6&',
    b'\xe8/',
    b'v4',
    b'f5',
    b'~7',
    b'\x9a7',
    b'C\t',
    b'\xfb\xff',
]
numSamples = 512

print('gstAvailible', gstAvailible)
@unittest.skipIf(not gstAvailible, 'Not supported')
class TestGstDec(unittest.TestCase):

    def test_open_as_generator(self):
        result = []
        with gstdec.GstAudioFile(testFilename, block_samples=numSamples) as input_file:
            gen = input_file.read_data()
            try:
                while True:
                    data = next(gen)
                    result.append(data)
            except StopIteration:
                pass

        self.assertEqual(len(bytes(result[0])), numSamples*2)
        self.assertEqual(len(rowLookup), len(result))
        for i, row in enumerate(result):
            self.assertEqual(bytes(row[0:2]), rowLookup[i])


    def test_open_as_forloop(self):
        result = []
        with gstdec.GstAudioFile(testFilename, block_samples=numSamples) as input_file:
            for buf in input_file:
                result.append(buf)

        for i, row in enumerate(result):
            self.assertEqual(bytes(row[0:2]), rowLookup[i])

    def test_seek(self):
        result = []
        with gstdec.GstAudioFile(testFilename, block_samples=numSamples) as input_file:
            gen = input_file.read_data()

            # move forward
            row = next(gen)
            row = next(gen)
            row = next(gen)

            # go back
            input_file.seek(512)
            row = next(gen)
            self.assertEqual(bytes(row[0:2]), rowLookup[1])
            row = next(gen)
            self.assertEqual(bytes(row[0:2]), rowLookup[2])
