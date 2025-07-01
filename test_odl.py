import unittest
import odl
import datetime # Import the datetime module

import os # Make sure os is imported

# Path to the sample LBL file we'll use for many tests
SAMPLE_LBL_FILE = 'samples/3531ML1023500011404703C00_DRXX.LBL'
# Path to the new sample IMG file that has an embedded label
SAMPLE_IMG_WITH_EMBEDDED_LABEL = os.path.join('samples', '4264MR1062180161604559I01_DXXX.IMG')
# Path to an IMG file confirmed NOT to have an embedded label (can be same as old LBL's IMG)
SAMPLE_IMG_WITHOUT_EMBEDDED_LABEL = os.path.join('samples', '3531ML1023500011404703C00_DRXX.IMG')


class TestODLParser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Parse the sample LBL file once for all tests in this class."""
        cls.label_parser = odl.ODL()
        with open(SAMPLE_LBL_FILE, 'r', encoding='latin-1') as f:
            cls.parsed_label_data = cls.label_parser.parse(f)

        # cls.img_label_parser = odl.ODL()
        # with open(SAMPLE_IMG_FILE_WITH_LABEL, 'r') as f_img:
        #     cls.parsed_img_label_data = cls.img_label_parser.parse(f_img)
        # The SAMPLE_IMG_FILE_WITH_LABEL ('...DRXX.IMG') does not appear to have an embedded text label.
        # The parsing of this file results in an empty dictionary because it's binary.
        # The test for this functionality (test_parse_img_file_with_embedded_label) has been removed
        # as we don't have a suitable sample IMG file with a known embedded label.
        pass


    def test_parse_simple_string_value(self):
        """Test parsing a simple string value."""
        self.assertEqual(self.parsed_label_data.get('PDS_VERSION_ID'), 'PDS3')
        self.assertEqual(self.label_parser.get('PDS_VERSION_ID'), 'PDS3')

    def test_parse_integer_value(self):
        """Test parsing a value that should be interpretable as an integer."""
        self.assertEqual(self.parsed_label_data.get('RECORD_BYTES'), '2304') # Raw parse is string
        self.assertEqual(self.label_parser.get('RECORD_BYTES', cast=int), 2304)
        self.assertEqual(self.label_parser.get('PLANET_DAY_NUMBER', cast=int), 3531)

    def test_parse_string_value_with_quotes(self):
        """Test parsing a string value that is enclosed in quotes in the LBL file."""
        # MSL:ACTIVE_FLIGHT_STRING_ID         = "B"
        self.assertEqual(self.parsed_label_data.get('MSL:ACTIVE_FLIGHT_STRING_ID'), '"B"')
        self.assertEqual(self.label_parser.get('MSL:ACTIVE_FLIGHT_STRING_ID'), '"B"')
        # The parser currently keeps the quotes if they are part of the value.
        # This might be a point of discussion: should it strip them?
        # For now, testing current behavior.

    def test_get_non_existent_key(self):
        """Test retrieving a non-existent key."""
        self.assertIsNone(self.parsed_label_data.get('NON_EXISTENT_KEY'))
        self.assertIsNone(self.label_parser.get('NON_EXISTENT_KEY'))

    def test_parse_isoc_datetime(self):
        """Test parsing a standard ISO format datetime (YYYY-MM-DDTHH:MM:SS.sss)."""
        # PRODUCT_CREATION_TIME               = 2022-10-08T07:25:34.055
        expected_dt = datetime.datetime(2022, 10, 8, 7, 25, 34, 55000)
        self.assertEqual(self.label_parser.get('PRODUCT_CREATION_TIME', cast=odl.ISOC), expected_dt)

    def test_parse_isod_datetime(self):
        """Test parsing a mission-specific day-based datetime (Sol-DDDDMHH:MM:SS.sss)."""
        # MSL:LOCAL_MEAN_SOLAR_TIME           = "Sol-03531M11:20:54.594"
        # Note: The quotes are part of the value in the LBL
        expected_sol = 3531
        expected_time = datetime.time(11, 20, 54, 594000)
        # The current ISOD parser likely expects the raw string without quotes.
        # We need to fetch the raw value first if it's quoted.
        raw_lmst = self.label_parser.get('MSL:LOCAL_MEAN_SOLAR_TIME') # This will be "\"Sol-03531M11:20:54.594\""

        # We need a way to pass the unquoted string to ISOD if it's a cast function
        # or the get method should handle unquoting before casting.
        # For now, let's assume we want to test the ISOD function directly or improve 'get' later.

        # Test odl.ISOD directly with the unquoted string
        sol, lmst_time = odl.ISOD(raw_lmst.strip('"'))
        self.assertEqual(sol, expected_sol)
        self.assertEqual(lmst_time, expected_time)

        # Test via the get method, assuming it might need adjustment or ISOD handles quotes
        # This might fail if 'get' passes the quotes to ISOD and ISOD doesn't strip them.
        # Based on README, `label_parser.get('MSL:LOCAL_MEAN_SOLAR_TIME', cast=odl.ISOD)` should work.
        # This implies ISOD or the casting mechanism in `get` handles the quotes.
        retrieved_sol, retrieved_lmst_time = self.label_parser.get('MSL:LOCAL_MEAN_SOLAR_TIME', cast=odl.ISOD)
        self.assertEqual(retrieved_sol, expected_sol)
        self.assertEqual(retrieved_lmst_time, expected_time)

    def test_parse_array_of_integers(self):
        """Test parsing an array of integer values."""
        # ROVER_MOTION_COUNTER = (96, 0, 0, 0, 0, 0, 74, 32, 0, 0 )
        expected_array = [96, 0, 0, 0, 0, 0, 74, 32, 0, 0]
        # get_array should directly cast elements
        self.assertEqual(self.label_parser.get_array('ROVER_MOTION_COUNTER', cast=int), expected_array)

    def test_parse_array_of_floats_scientific_notation(self):
        """Test parsing an array of floats in scientific notation within a group."""
        # MODEL_COMPONENT_1 = ( 8.792020e-01, 4.466344e-01, -1.962631e+00 )
        # This is inside GEOMETRIC_CAMERA_MODEL_PARMS group
        expected_array = [8.792020e-01, 4.466344e-01, -1.962631e+00]
        # Need to use the group path
        retrieved_array = self.label_parser.get_array('GEOMETRIC_CAMERA_MODEL_PARMS/MODEL_COMPONENT_1', cast=float)
        self.assertIsNotNone(retrieved_array)
        self.assertEqual(len(retrieved_array), len(expected_array))
        for r, e in zip(retrieved_array, expected_array):
            self.assertAlmostEqual(r, e, places=6) # Using assertAlmostEqual for floats

    def test_parse_value_in_group(self):
        """Test parsing a value from within a GROUP."""
        # FILTER_NAME = MASTCAM_L0_CLEAR (inside GEOMETRIC_CAMERA_MODEL_PARMS)
        self.assertEqual(self.label_parser.get('GEOMETRIC_CAMERA_MODEL_PARMS/FILTER_NAME'), 'MASTCAM_L0_CLEAR')

    def test_parse_value_in_object(self):
        """Test parsing a value from within an OBJECT structure."""
        # OBJECT = IMAGE ... LINES = 432 ... END_OBJECT = IMAGE
        self.assertEqual(self.label_parser.get('IMAGE/LINES', cast=int), 432)

    def test_parse_multiline_array(self):
        """Test parsing an array that spans multiple lines."""
        # ROVER_MOTION_COUNTER_NAME = ("SITE", "DRIVE", "POSE",
        #                              "ARM", "CHIMRA", "DRILL",
        #                              "RSM", "HGA",
        #                              "DRT", "IC")
        expected_array = ["SITE", "DRIVE", "POSE", "ARM", "CHIMRA", "DRILL", "RSM", "HGA", "DRT", "IC"]
        # The parser should strip the quotes from each element if they are part of the string literal in ODL
        # but not if they are part of the data itself. PDS3 can be tricky here.
        # Current parser behavior seems to keep quotes if present around individual elements.
        # Let's check the raw parsed value first.
        raw_value = self.parsed_label_data.get('ROVER_MOTION_COUNTER_NAME')
        # Example: ('"SITE"', '"DRIVE"', ...)
        # The get_array method with cast=str should give strings.
        retrieved_array = self.label_parser.get_array('ROVER_MOTION_COUNTER_NAME', cast=str)
        self.assertEqual(retrieved_array, expected_array)

    def test_parse_new_img_file_with_embedded_label(self):
        """Test parsing the new IMG file known to have an embedded ODL label."""
        self.assertTrue(os.path.exists(SAMPLE_IMG_WITH_EMBEDDED_LABEL),
                        f"Sample IMG file with embedded label missing: {SAMPLE_IMG_WITH_EMBEDDED_LABEL}")

        parser = odl.ODL()
        with open(SAMPLE_IMG_WITH_EMBEDDED_LABEL, 'r', encoding='latin-1') as f_img:
            # The ODL parser's try-except for UnicodeDecodeError should handle the binary part
            parsed_data = parser.parse(f_img)

        self.assertIsNotNone(parsed_data, "Parsing the IMG file with embedded label should return a dict.")
        self.assertGreater(len(parsed_data), 0, "Parsed data from IMG file should not be empty.")

        # Assertions based on previously inspected label content
        self.assertEqual(parser.get('PDS_VERSION_ID'), 'PDS3')
        self.assertEqual(parser.get('RECORD_TYPE'), 'FIXED_LENGTH')
        self.assertEqual(parser.get('RECORD_BYTES', cast=int), 160)
        self.assertEqual(parser.get('LABEL_RECORDS', cast=int), 160)
        self.assertEqual(parser.get('^IMAGE', cast=int), 161)
        self.assertEqual(parser.get('PRODUCT_ID'), '"4264MR1062180161604559I01_DXXX"')

        # Assertions for IMAGE object parameters
        self.assertEqual(parser.get('IMAGE/INTERCHANGE_FORMAT'), 'BINARY')
        self.assertEqual(parser.get('IMAGE/LINES', cast=int), 144)
        self.assertEqual(parser.get('IMAGE/LINE_SAMPLES', cast=int), 160)
        self.assertEqual(parser.get('IMAGE/SAMPLE_TYPE'), 'UNSIGNED_INTEGER')
        self.assertEqual(parser.get('IMAGE/SAMPLE_BITS', cast=int), 8)
        self.assertEqual(parser.get('IMAGE/BANDS', cast=int), 3)
        self.assertEqual(parser.get('IMAGE/BAND_STORAGE_TYPE'), 'BAND_SEQUENTIAL')

        # Assertion for datetime with 'Z' suffix
        expected_dt = datetime.datetime(2025, 1, 29, 23, 8, 51, 917000)
        self.assertEqual(parser.get('PRODUCT_CREATION_TIME', cast=odl.ISOC), expected_dt)


    # def test_parse_img_file_with_embedded_label(self):
    #     """Test parsing an IMG file that contains an embedded ODL label."""
    #     # This test is removed because the sample IMG file (3531ML..._DRXX.IMG)
    #     # does not appear to contain an embedded text ODL label.
    #     # If a suitable sample IMG file with a known embedded label becomes available,
    #     # this test (and the corresponding setup in setUpClass) can be reinstated.
    #     # Check a known value from the embedded label of the IMG file
    #     # Assuming the .IMG file's embedded label is similar or identical to the .LBL file for these fields
    #     # self.assertEqual(self.img_label_parser.get('PDS_VERSION_ID'), 'PDS3')
    #     # self.assertEqual(self.img_label_parser.get('RECORD_BYTES', cast=int), 2304)
    #     # Example: Check a value specific to image object if it differs or is present
    #     # self.assertEqual(self.img_label_parser.get('IMAGE/LINES', cast=int), 432)
    #     pass


    def test_casting_error_robustness(self):
        """Test how get handles casting errors (e.g. string to int)."""
        # PDS_VERSION_ID = PDS3. Casting 'PDS3' to int should fail.
        # The current behavior of `odl.py` might be to raise a ValueError.
        # Test that it raises an appropriate exception.
        with self.assertRaises(ValueError):
            self.label_parser.get('PDS_VERSION_ID', cast=int)

    def test_get_array_on_scalar_value(self):
        """Test behavior of get_array when the key points to a scalar value."""
        # PDS_VERSION_ID is a scalar.
        # What should get_array return? None? Raise error? Return a list with one item?
        # Based on typical PDS tools, it might return a list with the single item, or None/error.
        # Let's assume for now it might return a list with the single item if castable.
        # Or it could raise an error if it expects a sequence.
        # This needs clarification from odl.py's design or observed behavior.
        # get_array should return None if the value is not a valid ODL sequence string.
        self.assertIsNone(self.label_parser.get_array('PDS_VERSION_ID', cast=str))
        self.assertIsNone(self.label_parser.get_array('PDS_VERSION_ID', cast=int)) # Also with other casts

    def test_comments_ignored(self):
        """Test that comments are ignored and do not interfere with parsing."""
        # /* FILE DATA ELEMENTS */
        # This is a comment. The parser should ignore it.
        # We can verify this by ensuring keys around comments are parsed correctly.
        self.assertEqual(self.label_parser.get('PDS_VERSION_ID'), 'PDS3') # Before comment
        self.assertEqual(self.label_parser.get('RECORD_TYPE'), 'FIXED_LENGTH') # After comment

    def test_units_in_values(self):
        """Test parsing values that have units specified, e.g., <ms>."""
        # EXPOSURE_DURATION = 5.6 <ms>
        # The parser should ideally separate the value from the unit.
        # Current behavior in README example: `label_parser.get( 'START_TIME', cast=odl.ISOC )`
        # suggests that for datetimes it handles it. What about simple numeric values with units?
        raw_exposure = self.label_parser.get('INSTRUMENT_STATE_PARMS/EXPOSURE_DURATION')
        self.assertEqual(raw_exposure, '5.6 <ms>') # Assuming it keeps the unit for now if not casting

        # How does casting work?
        # If we cast to float, does it extract 5.6? Or fail?
        # This is an important behavior to define/test.
        # For now, let's assume it might fail if not handled.
        with self.assertRaises(ValueError): # Or TypeError, depending on implementation
            self.label_parser.get('INSTRUMENT_STATE_PARMS/EXPOSURE_DURATION', cast=float)

        # If it's expected to extract the value:
        # self.assertEqual(self.label_parser.get('INSTRUMENT_STATE_PARMS/EXPOSURE_DURATION', cast=float), 5.6)
        # This test will help clarify the current behavior.


if __name__ == '__main__':
    unittest.main()
