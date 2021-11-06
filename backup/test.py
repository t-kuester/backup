import os
import unittest

from backup_model import Configuration, Directory, write_to_json, load_from_json
import backup_core
from config import open_config, USER_DIR

TEST_CONFIG = "./test.json"
TEST_FILE = "./test.txt"


class TestModel(unittest.TestCase):

	def tearDown(self):
		"""remove config file from last test after each test case"""
		for f in [TEST_CONFIG, TEST_FILE]:
			if os.path.isfile(f):
				os.remove(f)

	def test_config_json(self):
		"""test basic JSON serialization and deserialization"""
		conf = Configuration("target-pattern", [])
		conf.directories.extend([Directory("/path/to/foo", "zip"),
								 Directory("/path/to/bar", "tar.gz", 1.23, True),
								 Directory("/path/to/blub", "tar", 4.56, False, True)])
		string = write_to_json(conf)
		conf2 = load_from_json(string)
		self.assertEqual(conf, conf2)
		self.assertEqual(string, write_to_json(conf2))

	def test_config_create(self):
		"""test creation of empty default config if none exists"""
		self.assertFalse(os.path.isfile(TEST_CONFIG))
		with open_config(TEST_CONFIG) as conf:
			pass
		self.assertTrue(os.path.isfile(TEST_CONFIG))

	def test_config_load_save(self):
		"""test modifying, saving, and reloading the config"""
		with open_config(TEST_CONFIG) as conf1:
			conf1.directories.append(Directory("/path/to/foo", "zip", 1.23, True))
		with open_config(TEST_CONFIG) as conf2:
			self.assertEqual(conf1, conf2)

	def test_backup_filenames(self):
		"""test derivation of target filename"""
		date = backup_core.get_date()
		time = backup_core.get_date(add_time=True)
		conf = Configuration("~/BACKUP {date}/{parent}/{dirname} {datetime}{inc}", [])
		self.assertEqual(
			backup_core.get_target_file(conf, Directory("/abs/path/to/file~nothome", "zip")),
			f"{USER_DIR}/BACKUP {date}/abs/path/to/file~nothome {time}.zip"
		)
		self.assertEqual(
			backup_core.get_target_file(conf, Directory("/abs/.hidden/.alsohidden/not.hidden", "tar", incremental=True)),
			f"{USER_DIR}/BACKUP {date}/abs/_hidden/_alsohidden/not.hidden {time}_inc.tar"
		)

	def test_create_zip(self):
		"""test creation of zip file"""
		pass

	def test_create_tar(self):
		"""test creation of tar file"""
		pass

	def test_calc_include(self):
		"""test directories to include with (a) no prior backup, (b) modified files, (c) no changes"""
		pass


	"""
	determine backup dir from date, relative path, also for hidden files, etc.
	remove last changed from model, but compute for "include?"
	test include conculation
	also with non-existing directories, or directories that are not folders
	test create backup, see of files exist
	create backup, decompress files with zip/tar tool, compare directories
	create backup when file with same name already exists
	create zip, check size (should at least be somewhat smaller)
	"""


if __name__ == "__main__":
	unittest.main()
