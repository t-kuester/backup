import os
import unittest

from backup_model import Configuration, Directory, write_to_json, load_from_json
from config import open_config

TEST_CONFIG = "./test.json"
TEST_FILE = "./src/test.txt"


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
		pass
	
	def test_create_zip(self):
		pass
		
	def test_create_tar(self):
		pass
		
	def test_calc_include_no_backup(self):
		pass
		
	def test_calc_include_modified(self):
		pass
		
	def test_calc_include_no_changes(self):
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


class TestCore(unittest.TestCase):
	
	pass


if __name__ == "__main__":
	unittest.main()
