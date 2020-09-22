import tempfile

from PIL import Image


def generate_test_image(file_format='.jpg'):
    image = Image.new('RGB', (100, 100), 'white')
    tmp_file = tempfile.NamedTemporaryFile(suffix=file_format)
    image.save(tmp_file.name)

    return tmp_file
