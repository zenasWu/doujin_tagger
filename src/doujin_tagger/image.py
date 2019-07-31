from io import BytesIO

from PIL import Image

COVER_FRONT = 3


class EmbeddedImage:
    """Embedded image, contains most of the properties needed
    for FLAC and ID3 images.
    """
    # or enter instead of init

    def __enter__(self):
        return self

    def __init__(self, bytesobj):
        self.fp = BytesIO()
        self.fp.write(bytesobj)
        with Image.open(self.fp) as im:
            self.width, self.height = im.size
            self.format = im.format
            self.mime_type = im.get_format_mimetype()
            # self._data = BytesIO()
            # im.save(self._data,format=im.format)

    def __repr__(self):
        return "<%s mime_type=%r width=%d height=%d>" % (
            type(self).__name__, self.mime_type, self.width, self.height)

    def read(self):
        self.fp.seek(0, 0)
        return self.fp.read()

    def __exit__(self, *exc):
        self.fp.close()
