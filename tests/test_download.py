from unittest import TestCase
from unittest.mock import MagicMock, Mock

from goodoldgalaxy.download import Download


class TestDownload(TestCase):
    def test1_set_progress(self):
        mock_progress_function = MagicMock()
        download = Download("test_url", "test_save_location")
        download.register_progress_function(mock_progress_function)
        download.set_progress(50)
        kall = mock_progress_function.mock_calls[-1]
        name, args, kwargs = kall
        exp = 50
        obs = args[0]
        self.assertEqual(exp, obs)

    def test2_set_progress(self):
        mock_progress_function = MagicMock()
        download = Download("test_url", "test_save_location", out_of_amount=2)
        download.register_progress_function(mock_progress_function)
        download.set_progress(32)
        kall = mock_progress_function.mock_calls[-1]
        name, args, kwargs = kall
        exp = 16
        obs = args[0]
        self.assertEqual(exp, obs)

    def test1_finish(self):
        mock_finish_function = MagicMock()
        download = Download("test_url", "test_save_location")
        download.register_finish_function(mock_finish_function)
        download.finish()
        exp = 2
        obs = len(mock_finish_function.mock_calls)
        self.assertEqual(exp, obs)

    def test2_finish(self):
        mock_finish_function = MagicMock()
        mock_finish_function.side_effect = FileNotFoundError(Mock(status="Connection Error"))
        mock_cancel_function = MagicMock()
        download = Download("test_url", "test_save_location")
        download.register_finish_function(mock_finish_function)
        download.register_cancel_function(mock_cancel_function)
        download.finish()
        exp = 2
        obs = len(mock_cancel_function.mock_calls)
        self.assertEqual(exp, obs)

    def test_cancel(self):
        mock_cancel_function = MagicMock()
        download = Download("test_url", "test_save_location")
        download.register_cancel_function(mock_cancel_function)
        download.cancel()
        exp = 2
        obs = len(mock_cancel_function.mock_calls)
        self.assertEqual(exp, obs)
