import unittest
import random
from lazbot import db, logger
from shutil import rmtree


class DbTest(unittest.TestCase):
    def setUp(self):
        db.setup({"data_dir": "/tmp/test_data"})

    def tearDown(self):
        rmtree("/tmp/test_data")

    def test_persistence(self):
        """Ensure that data stored is retrievable
        Data that is stored should be retrievable and deletable.
        """
        value = random.randint(1, 1000000)

        with logger.scope("persistent"):
            db["test_value"] = value

        with logger.scope("persistent"):
            self.assertEquals(value, db["test_value"])
            del db["test_value"]

        with logger.scope("persistent"):
            self.assertIsNone(db["test_value"])

    def test_isolation(self):
        """Ensure that data is stored in the specified namespace
        Data should be stored based on the current plugin context and it should
        not be polluted between plugin contexts.
        """
        with logger.scope("scope1"):
            db["test_value"] = 1

        with logger.scope("scope2"):
            self.assertIsNone(db["test_value"])

    def test_serialization(self):
        """Data of complex types is properly serialized
        Data is serialized from more complex types into the datastore and also
        retrieved and unserialzed properly.
        """
        data = {"foo": random.randint(1, 100), "bar": "baz"}

        with logger.scope("complex"):
            db["dict"] = data
            self.assertDictEqual(db["dict"], data)
