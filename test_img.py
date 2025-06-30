import unittest
import numpy as np
import os

# Assuming img.py and odl.py are in the same directory or accessible via PYTHONPATH
import img
import odl

# Define paths to sample files (assuming they are in a 'samples' subdirectory)
SAMPLES_DIR = 'samples'
LBL_FILE_VALID = os.path.join(SAMPLES_DIR, '3531ML1023500011404703C00_DRXX.LBL')
IMG_FILE_FOR_LBL_VALID = os.path.join(SAMPLES_DIR, '3531ML1023500011404703C00_DRXX.IMG')
# This IMG file seems to be binary from the start, without an embedded label
IMG_FILE_BINARY_NO_LABEL = IMG_FILE_FOR_LBL_VALID
# New IMG file with a confirmed embedded label
IMG_FILE_WITH_EMBEDDED_LABEL = os.path.join(SAMPLES_DIR, '4264MR1062180161604559I01_DXXX.IMG')

class TestOdlTypeToNumpyDtype(unittest.TestCase):
    def test_valid_types(self):
        # (pds_sample_type, pds_sample_bits) -> expected_numpy_dtype
        test_cases = [
            ('MSB_UNSIGNED_INTEGER', 16, '>u2'),
            ('LSB_UNSIGNED_INTEGER', 16, '<u2'),
            ('MSB_SIGNED_INTEGER', 16, '>i2'),
            ('LSB_SIGNED_INTEGER', 16, '<i2'),
            ('UNSIGNED_INTEGER', 8, '>u1'), # Assuming UNSIGNED_INTEGER defaults to MSB if not specified
            ('MSB_UNSIGNED_INTEGER', 8, '>u1'),
            ('IEEE_REAL', 32, '>f4'),
            ('IEEE_DOUBLE', 64, '>f8'),
        ]
        for sample_type, sample_bits, expected_dtype in test_cases:
            with self.subTest(sample_type=sample_type, sample_bits=sample_bits):
                dtype = img.odl_type_to_numpy_dtype(sample_type, sample_bits)
                self.assertEqual(dtype, expected_dtype)

    def test_unknown_type(self):
        """Test that an unknown sample type raises a ValueError."""
        with self.assertRaises(ValueError):
            img.odl_type_to_numpy_dtype('UNKNOWN_TYPE', 32)

class TestReadLblImg(unittest.TestCase):
    # From 3531ML1023500011404703C00_DRXX.LBL:
    # RECORD_BYTES                        = 2304
    # ^IMAGE = ("3531ML1023500011404703C00_DRXX.IMG")
    # IMAGE/BANDS                           = 3
    # IMAGE/SAMPLE_TYPE                     = MSB_UNSIGNED_INTEGER
    # IMAGE/SAMPLE_BITS                     = 16
    # IMAGE/LINES                           = 432
    # IMAGE/LINE_SAMPLES                    = 1152
    EXPECTED_SHAPE = (3, 432, 1152) # Bands, Lines, Samples
    EXPECTED_DTYPE = '>u2' # MSB_UNSIGNED_INTEGER, 16 bits

    def test_read_with_lbl_only(self):
        """Test reading when only LBL path is provided, IMG path inferred."""
        self.assertTrue(os.path.exists(LBL_FILE_VALID), f"LBL file missing: {LBL_FILE_VALID}")
        self.assertTrue(os.path.exists(IMG_FILE_FOR_LBL_VALID), f"IMG file missing: {IMG_FILE_FOR_LBL_VALID}")

        image_data = img.read_lbl_img(lbl_path=LBL_FILE_VALID)
        self.assertIsInstance(image_data, np.ndarray)
        self.assertEqual(image_data.shape, self.EXPECTED_SHAPE)
        self.assertEqual(image_data.dtype, np.dtype(self.EXPECTED_DTYPE))

    def test_read_with_explicit_lbl_and_img(self):
        """Test reading when both LBL and IMG paths are provided."""
        self.assertTrue(os.path.exists(LBL_FILE_VALID), f"LBL file missing: {LBL_FILE_VALID}")
        self.assertTrue(os.path.exists(IMG_FILE_FOR_LBL_VALID), f"IMG file missing: {IMG_FILE_FOR_LBL_VALID}")

        image_data = img.read_lbl_img(lbl_path=LBL_FILE_VALID, img_path=IMG_FILE_FOR_LBL_VALID)
        self.assertIsInstance(image_data, np.ndarray)
        self.assertEqual(image_data.shape, self.EXPECTED_SHAPE)
        self.assertEqual(image_data.dtype, np.dtype(self.EXPECTED_DTYPE))

    def test_lbl_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            img.read_lbl_img(lbl_path='non_existent_label.LBL')

    def test_img_file_not_found_inferred(self):
        # Create a dummy LBL file for this test
        dummy_lbl_path = os.path.join(SAMPLES_DIR, 'dummy.LBL')
        with open(dummy_lbl_path, 'w') as f:
            f.write('PDS_VERSION_ID = PDS3\n')
            f.write('RECORD_BYTES = 1024\n')
            f.write('^IMAGE = "dummy.IMG"\n') # Points to a non-existent IMG
            f.write('IMAGE/BANDS = 1\n')
            f.write('IMAGE/SAMPLE_TYPE = MSB_UNSIGNED_INTEGER\n')
            f.write('IMAGE/SAMPLE_BITS = 8\n')
            f.write('IMAGE/LINES = 10\n')
            f.write('IMAGE/LINE_SAMPLES = 10\n')
            f.write('END\n')

        with self.assertRaises(FileNotFoundError):
            img.read_lbl_img(lbl_path=dummy_lbl_path)

        os.remove(dummy_lbl_path) # Clean up

    def test_img_file_not_found_explicit(self):
        with self.assertRaises(FileNotFoundError):
            img.read_lbl_img(lbl_path=LBL_FILE_VALID, img_path='non_existent_image.IMG')

    def test_missing_metadata_in_lbl(self):
        """Test behavior when LBL file is missing crucial metadata."""
        dummy_lbl_path = os.path.join(SAMPLES_DIR, 'incomplete.LBL')
        with open(dummy_lbl_path, 'w') as f:
            f.write('PDS_VERSION_ID = PDS3\n')
            # Missing IMAGE/BANDS, IMAGE/LINES etc.
            f.write('END\n')

        # odl.py's get(..., cast=int) on a None value will raise TypeError
        with self.assertRaises(TypeError):
            img.read_lbl_img(lbl_path=dummy_lbl_path)

        os.remove(dummy_lbl_path)


class TestReadImg(unittest.TestCase):
    def test_read_img_with_binary_file_no_label(self):
        """
        Test read_img with an IMG file that does not have an embedded ODL label.
        It should fail gracefully because odl.py will parse an empty label,
        leading to TypeErrors when trying to cast None from label_parser.get().
        """
        self.assertTrue(os.path.exists(IMG_FILE_BINARY_NO_LABEL), f"IMG file missing: {IMG_FILE_BINARY_NO_LABEL}")
        # Expect TypeError because label lookups for cast=int will get None, int(None) -> TypeError
        with self.assertRaises(TypeError): # Should still fail if label parsing results in None for essential fields
            img.read_img(img_path=IMG_FILE_BINARY_NO_LABEL)

    def test_read_img_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            img.read_img(img_path='non_existent_image.IMG')

    def test_read_img_with_embedded_label_success(self):
        """Test read_img with the new IMG file that has an embedded label."""
        self.assertTrue(os.path.exists(IMG_FILE_WITH_EMBEDDED_LABEL),
                        f"Sample IMG file with embedded label missing: {IMG_FILE_WITH_EMBEDDED_LABEL}")

        image_data = img.read_img(img_path=IMG_FILE_WITH_EMBEDDED_LABEL)
        self.assertIsInstance(image_data, np.ndarray)

        # Expected values from 4264MR1062180161604559I01_DXXX.IMG label:
        # IMAGE/BANDS = 3
        # IMAGE/LINES = 144
        # IMAGE/LINE_SAMPLES = 160
        # IMAGE/SAMPLE_TYPE = UNSIGNED_INTEGER (implies MSB for numpy if not specified)
        # IMAGE/SAMPLE_BITS = 8
        expected_shape = (3, 144, 160)
        expected_dtype = '>u1' # MSB Unsigned Integer, 1 byte (8 bits)

        self.assertEqual(image_data.shape, expected_shape)
        self.assertEqual(image_data.dtype, np.dtype(expected_dtype))

        # Verify that data was actually read - check total size
        # Total elements = 3 * 144 * 160 = 69120
        # Total bytes = 69120 * 1 (byte per element for u1) = 69120
        # From label: FILE_RECORDS = 592, LABEL_RECORDS = 160, RECORD_BYTES = 160
        # Image records = 592 - 160 = 432
        # Image bytes = 432 * 160 = 69120 bytes. This matches.
        self.assertEqual(image_data.size, expected_shape[0] * expected_shape[1] * expected_shape[2])

if __name__ == '__main__':
    # Create samples dir if it doesn't exist, for dummy file creation
    if not os.path.exists(SAMPLES_DIR):
        os.makedirs(SAMPLES_DIR)
    unittest.main()
