import unittest
from unittest.mock import MagicMock, mock_open, patch
from goodoldgalaxy.game import Game


class MyTestCase(unittest.TestCase):
    def test_strip_within_comparison(self):
        game1 = Game("!@#$%^&*(){}[]\"'_-<>.,;:")
        game2 = Game("")
        game3 = Game("hallo")
        game4 = Game("Hallo")
        game5 = Game("Hallo!")
        self.assertEqual(game1, game2)
        self.assertNotEqual(game2, game3)
        self.assertEqual(game3, game4)
        self.assertEqual(game3, game5)

    def test_local_and_api_comparison(self):
        larry1_api = Game("Leisure Suit Larry 1 - In the Land of the Lounge Lizards", game_id=1207662033)
        larry1_local_gog = Game("Leisure Suit Larry", install_dir="/home/user/Games/Leisure Suit Larry",
                                game_id=1207662033)
        larry1_local_goodoldgalaxy = Game("Leisure Suit Larry",
                                       install_dir="/home/wouter/Games/Leisure Suit Larry 1 - In the Land of the Lounge Lizards",
                                       game_id=1207662033)

        self.assertEqual(larry1_local_gog, larry1_local_goodoldgalaxy)
        self.assertEqual(larry1_local_goodoldgalaxy, larry1_api)
        self.assertEqual(larry1_local_gog, larry1_api)

        larry2_api = Game("Leisure Suit Larry 2 - Looking For Love (In Several Wrong Places)", game_id=1207662053)
        larry2_local_goodoldgalaxy = Game("Leisure Suit Larry 2",
                                       install_dir="/home/user/Games/Leisure Suit Larry 2 - Looking For Love (In Several Wrong Places)",
                                       game_id=1207662053)
        larry2_local_gog = Game("Leisure Suit Larry 2", install_dir="/home/user/Games/Leisure Suit Larry 2",
                                game_id=1207662053)

        self.assertNotEqual(larry1_api, larry2_api)
        self.assertNotEqual(larry2_local_gog, larry1_api)
        self.assertNotEqual(larry2_local_gog, larry1_local_gog)
        self.assertNotEqual(larry2_local_gog, larry1_local_goodoldgalaxy)
        self.assertNotEqual(larry2_local_goodoldgalaxy, larry1_api)
        self.assertNotEqual(larry2_local_goodoldgalaxy, larry1_local_goodoldgalaxy)

    def test_local_comparison(self):
        larry1_local_gog = Game("Leisure Suit Larry", install_dir="/home/user/Games/Leisure Suit Larry",
                                game_id=1207662033)
        larry1_vga_local_gog = Game("Leisure Suit Larry VGA", install_dir="/home/user/Games/Leisure Suit Larry VGA",
                                    game_id=1207662043)

        self.assertNotEqual(larry1_local_gog, larry1_vga_local_gog)

    def test1_validate_if_installed_is_latest(self):
        game = Game("Version Test game")
        game.installed_version = "gog-2"
        game.read_installed_version = MagicMock()
        installers = [{'os': 'windows', 'version': '1.0'}, {'os': 'mac', 'version': '1.0'},
                      {'os': 'linux', 'version': 'gog-2'}]
        expected = True
        observed = game.validate_if_installed_is_latest(installers)
        self.assertEqual(expected, observed)

    def test2_validate_if_installed_is_latest(self):
        game = Game("Version Test game")
        game.installed_version = "91.8193.16"
        game.read_installed_version = MagicMock()
        installers = [{'os': 'windows', 'version': '81.8193.16'}, {'os': 'mac', 'version': '81.8193.16'},
                      {'os': 'linux', 'version': '81.8193.16'}]
        expected = False
        observed = game.validate_if_installed_is_latest(installers)
        self.assertEqual(expected, observed)

    def test1_get_install_directory_name(self):
        game = Game("Get Install Directory Test1")
        expected = "Get Install Directory Test1"
        observed = game.get_install_directory_name()
        self.assertEqual(expected, observed)

    def test2_get_install_directory_name(self):
        game = Game("Get\r Install\n Directory Test2!@#$%")
        expected = "Get Install Directory Test2"
        observed = game.get_install_directory_name()
        self.assertEqual(expected, observed)

    @unittest.mock.patch('os.path.isfile')
    def test1_read_installed_version(self, mock_isfile):
        mock_isfile.return_value = True
        gameinfo = """Beneath A Steel Sky
gog-2
20150
en-US
1207658695
1207658695
664777434"""
        with patch("builtins.open", mock_open(read_data=gameinfo)):
            game = Game("Game Name test1")
        expected = "gog-2"
        observed = game.installed_version
        self.assertEqual(expected, observed)

    @unittest.mock.patch('os.path.isfile')
    def test2_read_installed_version(self, mock_isfile):
        mock_isfile.return_value = False
        gameinfo = """Beneath A Steel Sky
    gog-2
    20150
    en-US
    1207658695
    1207658695
    664777434"""
        with patch("builtins.open", mock_open(read_data=gameinfo)):
            game = Game("Game Name test2")
        expected = ""
        observed = game.installed_version
        self.assertEqual(expected, observed)

    @unittest.mock.patch('os.path.isfile')
    def test1_get_dlc_status(self, mock_isfile):
        mock_isfile.side_effect = [False, True]
        json_content = '[{"Neverwinter Nights: Wyvern Crown of Cormyr": "not-installed", ' \
                       '"Neverwinter Nights: Infinite Dungeons": "updatable", "Neverwinter Nights: Pirates of ' \
                       'the Sword Coast": "installed"}, {}]'
        with patch("builtins.open", mock_open(read_data=json_content)):
            game = Game("Game Name test1")
            game.read_installed_version = MagicMock()
            game.installed_version = "1"
            dlc_status = game.get_dlc_status("Neverwinter Nights: Wyvern Crown of Cormyr", "")
        expected = "not-installed"
        observed = dlc_status
        self.assertEqual(expected, observed)

    @unittest.mock.patch('os.path.isfile')
    def test2_get_dlc_status(self, mock_isfile):
        mock_isfile.side_effect = [False, True]
        json_content = '[{"Neverwinter Nights: Wyvern Crown of Cormyr": "not-installed", ' \
                       '"Neverwinter Nights: Infinite Dungeons": "updatable", "Neverwinter Nights: Pirates of ' \
                       'the Sword Coast": "installed"}, {}]'
        with patch("builtins.open", mock_open(read_data=json_content)):
            game = Game("Game Name test2")
            game.read_installed_version = MagicMock()
            game.installed_version = "1"
            dlc_status = game.get_dlc_status("Neverwinter Nights: Infinite Dungeons", "")
        expected = "updatable"
        observed = dlc_status
        self.assertEqual(expected, observed)

    @unittest.mock.patch('os.path.isfile')
    def test3_get_dlc_status(self, mock_isfile):
        mock_isfile.side_effect = [False, False]
        json_content = '[{"Neverwinter Nights: Wyvern Crown of Cormyr": "not-installed", ' \
                       '"Neverwinter Nights: Infinite Dungeons": "updatable", "Neverwinter Nights: Pirates of ' \
                       'the Sword Coast": "installed"}, {}]'
        with patch("builtins.open", mock_open(read_data=json_content)):
            game = Game("Game Name test2")
            game.read_installed_version = MagicMock()
            game.installed_version = "1"
            dlc_status = game.get_dlc_status("Neverwinter Nights: Infinite Dungeons", "")
        expected = "not-installed"
        observed = dlc_status
        self.assertEqual(expected, observed)

    @unittest.mock.patch('os.path.isfile')
    def test1_set_dlc_status(self, mock_isfile):
        mock_isfile.return_value = True
        json_content = '[{"Neverwinter Nights: Wyvern Crown of Cormyr": "not-installed", ' \
                       '"Neverwinter Nights: Infinite Dungeons": "updatable", "Neverwinter Nights: Pirates of ' \
                       'the Sword Coast": "installed"}, {}]'
        dlc_name = "Neverwinter Nights: Wyvern Crown of Cormyr"
        dlc_status = True
        with patch("builtins.open", mock_open(read_data=json_content)) as m:
            game = Game("Game Name test2")
            game.read_installed_version = MagicMock()
            game.installed_version = "1"
            game.set_dlc_status(dlc_name, dlc_status, "")
        mock_c = m.mock_calls
        write_string = ""
        for kall in mock_c:
            name, args, kwargs = kall
            if name == "().write":
                write_string = "{}{}".format(write_string, args[0])
        expected = '[{"Neverwinter Nights: Wyvern Crown of Cormyr": "installed", ' \
                   '"Neverwinter Nights: Infinite Dungeons": "updatable", "Neverwinter Nights: Pirates of ' \
                   'the Sword Coast": "installed"}, {"Neverwinter Nights: Wyvern Crown of Cormyr": ""}]'
        observed = write_string
        self.assertEqual(expected, observed)

    @unittest.mock.patch('os.path.isfile')
    def test2_set_dlc_status(self, mock_isfile):
        mock_isfile.return_value = False
        dlc_name = "Neverwinter Nights: Test DLC"
        dlc_status = False
        with patch("builtins.open", mock_open()) as m:
            game = Game("Game Name test2")
            game.read_installed_version = MagicMock()
            game.installed_version = "1"
            game.set_dlc_status(dlc_name, dlc_status, "")
        mock_c = m.mock_calls
        write_string = ""
        for kall in mock_c:
            name, args, kwargs = kall
            if name == "().write":
                write_string = "{}{}".format(write_string, args[0])
        expected = '[{"Neverwinter Nights: Test DLC": "not-installed"}, {}]'
        observed = write_string
        self.assertEqual(expected, observed)

    @unittest.mock.patch('os.path.isfile')
    def test1_get_dlc_status_version(self, mock_isfile):
        mock_isfile.side_effect = [False, True]
        json_content = '[{"Neverwinter Nights: Wyvern Crown of Cormyr": "not-installed", ' \
                       '"Neverwinter Nights: Infinite Dungeons": "installed", "Neverwinter Nights: Pirates of ' \
                       'the Sword Coast": "installed"}, {"Neverwinter Nights: Wyvern Crown of Cormyr": ' \
                       '"81.8193.16", "Neverwinter Nights: Infinite Dungeons": "81.8193.17", "Neverwinter Nights: ' \
                       'Pirates of the Sword Coast": "81.8193.18"}] '
        with patch("builtins.open", mock_open(read_data=json_content)):
            game = Game("Game Name test2")
            game.read_installed_version = MagicMock()
            game.installed_version = "1"
            dlc_status = game.get_dlc_status("Neverwinter Nights: Infinite Dungeons", "81.8193.16")
        expected = "updatable"
        observed = dlc_status
        self.assertEqual(expected, observed)

    @unittest.mock.patch('os.path.isfile')
    def test2_get_dlc_status_version(self, mock_isfile):
        mock_isfile.side_effect = [False, True]
        json_content = '[{"Neverwinter Nights: Wyvern Crown of Cormyr": "updatable", ' \
                       '"Neverwinter Nights: Infinite Dungeons": "installed", "Neverwinter Nights: Pirates of ' \
                       'the Sword Coast": "installed"}, {"Neverwinter Nights: Wyvern Crown of Cormyr": ' \
                       '"81.8193.16", "Neverwinter Nights: Infinite Dungeons": "81.8193.17", "Neverwinter Nights: ' \
                       'Pirates of the Sword Coast": "81.8193.18"}] '
        with patch("builtins.open", mock_open(read_data=json_content)):
            game = Game("Game Name test2")
            game.read_installed_version = MagicMock()
            game.installed_version = "1"
            dlc_status = game.get_dlc_status("Neverwinter Nights: Wyvern Crown of Cormyr", "")
        expected = "updatable"
        observed = dlc_status
        self.assertEqual(expected, observed)

    @unittest.mock.patch('os.path.isfile')
    def test3_get_dlc_status_version(self, mock_isfile):
        mock_isfile.side_effect = [False, True]
        json_content = '[{"Neverwinter Nights: Wyvern Crown of Cormyr": "updatable", ' \
                       '"Neverwinter Nights: Infinite Dungeons": "installed", "Neverwinter Nights: Pirates of ' \
                       'the Sword Coast": "installed"}, {"Neverwinter Nights: Wyvern Crown of Cormyr": ' \
                       '"81.8193.16", "Neverwinter Nights: Infinite Dungeons": "81.8193.17", "Neverwinter Nights: ' \
                       'Pirates of the Sword Coast": "81.8193.18"}] '
        with patch("builtins.open", mock_open(read_data=json_content)):
            game = Game("Game Name test2")
            game.read_installed_version = MagicMock()
            game.installed_version = "1"
            dlc_status = game.get_dlc_status("Neverwinter Nights: Infinite Dungeons", "81.8193.17")
        expected = "installed"
        observed = dlc_status
        self.assertEqual(expected, observed)

    @unittest.mock.patch('os.path.isfile')
    def test1_set_dlc_status_version(self, mock_isfile):
        mock_isfile.return_value = True
        json_content = '[{"Neverwinter Nights: Wyvern Crown of Cormyr": "not-installed", ' \
                       '"Neverwinter Nights: Infinite Dungeons": "updatable", "Neverwinter Nights: Pirates of ' \
                       'the Sword Coast": "installed"}, {}]'
        dlc_name = "Neverwinter Nights: Wyvern Crown of Cormyr"
        dlc_status = True
        with patch("builtins.open", mock_open(read_data=json_content)) as m:
            game = Game("Game Name test2")
            game.read_installed_version = MagicMock()
            game.installed_version = "1"
            game.set_dlc_status(dlc_name, dlc_status, "81.8193.17")
        mock_c = m.mock_calls
        write_string = ""
        for kall in mock_c:
            name, args, kwargs = kall
            if name == "().write":
                write_string = "{}{}".format(write_string, args[0])
        expected = '[{"Neverwinter Nights: Wyvern Crown of Cormyr": "installed", ' \
                   '"Neverwinter Nights: Infinite Dungeons": "updatable", "Neverwinter Nights: Pirates of ' \
                   'the Sword Coast": "installed"}, {"Neverwinter Nights: Wyvern Crown of Cormyr": "81.8193.17"}]'
        observed = write_string
        self.assertEqual(expected, observed)


if __name__ == '__main__':
    unittest.main()
