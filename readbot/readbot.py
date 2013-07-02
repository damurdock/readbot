import urlparse
import urllib2
import subprocess
import tempfile
import os
import atexit
import shutil

class ReadBot(object):

    def __init__(self, ocr_engine='tesseract', pdf_converter='ghostscript'):
        self.ocr_engine = ocr_engine
        self.pdf_converter = pdf_converter
        self.temp = tempfile.mkdtemp()
        atexit.register(shutil.rmtree,self.temp)


    def interpret(self, input_file):
        '''valid input is a file like object or string (url or path) to an image or pdf file'''
        if type(input_file) is str:
            input_file = self.open_url_or_file(input_file)

        ext = os.path.splitext(input_file.name)[1]

        if ext == '.pdf':
            input_file = self.pdf_to_img(input_file.name)

        ocr_result = self.run_ocr(input_file)

        return ocr_result

    def open_url_or_file(self, string_in):

        if self.is_url(string_in):

            url_file = urllib2.urlopen(string_in)
            uri = urlparse.urlparse(string_in).path
            ext = os.path.splitext(uri)[1]

            input_file = tempfile.NamedTemporaryFile(suffix=ext)
            open(input_file.name, 'rb+').write(url_file.read())

        else:

            try:
                input_file = open(string_in, 'rb+')
            except IOError:
                raise RuntimeError('File not found')

        return input_file

    def is_url(self, url):

        try:
            urllib2.urlopen(url)
            return True
        except (IOError, ValueError):
            return False

    def pdf_to_img(self, pdf):

        pdf_conversion  = tempfile.NamedTemporaryFile(suffix='.png')

        if self.pdf_converter == 'ghostscript':
            try:
                subprocess.call(['gs', '-sDEVICE=pngalpha', '-dNOPAUSE', '-dBATCH', '-sOutputFile=' +
                                self.temp + '/%d.png', '-r300', pdf])
                subprocess.call(['convert', self.temp + '/*.png' , '-append', pdf_conversion.name])

            except OSError:
                raise RuntimeError("Failed to convert pdf. Are Ghostscript (http://www.ghostscript.com/) and ImageMagick (http://www.imagemagick.org/) installed?")

        return pdf_conversion

    def run_ocr(self, input_file):

        engine = OcrEngine()

        if self.ocr_engine == 'tesseract':
            ocr_result = engine.tesseract(input_file,self.temp)

        return ocr_result


class OcrEngine(object):

    def tesseract(self, input_file, temp):

        try:
            subprocess.call(['tesseract', input_file.name,
                            temp + '/ocr_result'])
        except OSError:
            raise RuntimeError("Failed to run tesseract command. Is it installed? http://code.google.com/p/tesseract-ocr/")

        ocr_result = open(
            temp + '/ocr_result' + '.txt', 'rb+').read().strip()

        os.remove(temp + '/ocr_result' + '.txt')

        return ocr_result
