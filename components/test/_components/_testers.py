from typing import Protocol

import pytest


class InstanceTester(Protocol):
    def test(self):
        self.dynamic_test()

    def dynamic_test(self):
        for method in dir(self):
            if method.startswith("test") and method != "test":
                getattr(self, method)()


class ClassTester:
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def setup_method(self, method):
        pass

    def teardown_method(self, method):
        pass
