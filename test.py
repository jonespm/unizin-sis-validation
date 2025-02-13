# local modules
from dbqueries import QUERIES
import validate

# standard modules
from datetime import datetime, timedelta
import pandas as pd
import pytz
import unittest


class TestFlagRaising(unittest.TestCase):

    def test_udw_table_counts_check(self):
        # Set up
        udw_table_counts_df = pd.DataFrame({
            'table_name': [
                'ASSIGNMENT_DIM',
                'COURSE_DIM',
                'COURSE_SCORE_FACT',
                'ENROLLMENT_TERM_DIM',
                'PSEUDONYM_DIM',
                'SUBMISSION_COMMENT_DIM',
                'SUBMISSION_DIM',
                'SUBMISSION_FACT',
                'USER_DIM',
            ],
            'record_count': [1000, 1000, 1000, 0, 1000, 1000, 1000, 1000, 0]
        })
        query_dict = QUERIES['udw_table_counts']
        # Test
        checks_result = validate.run_checks_on_output(query_dict['checks'], udw_table_counts_df)
        self.assertCountEqual(
            ['table_name', 'record_count', 'not_zero'],
            checks_result.checked_output_df.columns.to_list()
        )
        self.assertTrue(checks_result.flags == ["RED"])
        result_text = validate.generate_result_text(query_dict['query_name'], checks_result.checked_output_df)
        self.assertEqual(result_text.count('<-- "not_zero" condition failed'), 2)

    def test_unizin_metadata_check(self):
        # Set up
        delta_obj = timedelta(days=-3)
        three_days_ago = datetime.now(tz=pytz.UTC) + delta_obj
        unizin_metadata_df = pd.DataFrame({
            'key': ['schemaversion', 'canvasdatadate'],
            'value': ['X.X.X', three_days_ago.isoformat()]
        })
        query_dict = QUERIES['unizin_metadata']
        # Test
        checks_result = validate.run_checks_on_output(query_dict['checks'], unizin_metadata_df)
        self.assertCountEqual(
            ['key', 'value', 'less_than_two_days'],
            checks_result.checked_output_df.columns.to_list()
        )
        self.assertTrue(checks_result.flags == ["YELLOW"])
        result_text = validate.generate_result_text(query_dict['query_name'], checks_result.checked_output_df)
        self.assertIn('<-- "less_than_two_days" condition failed', result_text)


unittest.main()