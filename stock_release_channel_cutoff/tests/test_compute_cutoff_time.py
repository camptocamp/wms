# Copyright 2023 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase


class TestStockReleaseChannel(TransactionCase):
    def setUp(self):
        super(TestStockReleaseChannel, self).setUp()
        self.stock_release_channel_default = self.env.ref(
            "stock_release_channel.stock_release_channel_default"
        )
        self.env.user.tz = "UTC"  # Timezone UTC

    def test_compute_cutoff_time(self):
        # Change the timezone to UTC+2
        self.env.user.tz = "Europe/Brussels"
        # Create a test record with a cutoff datetime in UTC
        self.stock_release_channel_default.write(
            {
                "cutoff_datetime": "2023-09-09 14:30:00",
            }
        )

        # Ensure the cutoff_time is correctly computed in the user's timezone
        # (We use 'UTC+2' for the test user)
        expected_time = "16:30"
        self.assertEqual(self.stock_release_channel_default.cutoff_time, expected_time)

        # Test the case when cutoff_datetime is empty
        self.stock_release_channel_default.write(
            {
                "cutoff_datetime": False,
            }
        )

        self.assertFalse(self.stock_release_channel_default.cutoff_time)

        # Test the case when the user's timezone is explicitly set to a specific value
        # (In this case, we assume 'America/New_York' timezone)
        user = self.env.user
        user.tz = "America/New_York"

        self.stock_release_channel_default.write(
            {
                "cutoff_datetime": "2023-09-08 14:30:00",
            }
        )

        # Ensure the cutoff_time is correctly computed in the custom timezone
        expected_time_custom_tz = (
            "10:30"  # Assuming 'America/New_York' timezone is UTC-4
        )
        self.assertEqual(
            self.stock_release_channel_default.cutoff_time, expected_time_custom_tz
        )
