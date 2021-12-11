"""Utils tests."""

# Utils
from utils.serializers import is_asuka_picture

# Tests
import unittest


class UtilsTestCase(unittest.TestCase):
    """Utils test case."""

    def test_is_asuka_picture(self):
        """Verifies that it can make a request
        and identifies the ´Asuka Langley´ pictures.
        """
        correct_asuka_picture_url = "https://res.cloudinary.com/neuromodmedia/image/upload/v1638719077/test/asuka_example_xwv1i6.jpg"
        wrong_asuka_picture_url = "https://res.cloudinary.com/neuromodmedia/image/upload/v1638719218/test/wrong_asuka_example_g1f3mp.jpg"

        assert is_asuka_picture(image_url=correct_asuka_picture_url) == True
        assert is_asuka_picture(image_url=wrong_asuka_picture_url) == False
