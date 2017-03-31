from unittest import TestCase
from ..library import LibraryMaker


class TestLibraryMaker(TestCase):
    def test_add_searchpath(self):
        lm = LibraryMaker("test")
        self.assertTrue(lm.add_search_path("."))
        self.assertFalse(lm.add_search_path("."))
        self.assertTrue(lm.add_search_path(".."))
        self.assertFalse(lm.add_search_path("not-exists"))

    def test_version(self):
        pass

    def test_process_files(self):
        pass

    def test_process_object_file(self):
        pass

    def test_process_object_doc(self):
        pass

    def test_fill_library_meta(self):
        pass

    def test_add_to_others(self):
        pass

    def test_add_to_cat(self):
        pass

    def test_xi_include(self):
        pass

    def test_sort_cat(self):
        pass

    def test_sort(self):
        pass

