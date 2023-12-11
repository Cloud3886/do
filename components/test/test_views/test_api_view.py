import pytest

from components.lib.views.api_view import ApiView
from components.test._components._testers import InstanceTester
from components.utils.extensions import hash_gen


class ApiViewTester(InstanceTester):
    def __init__(self, view: ApiView) -> None:
        self.view = view

    def test_view_name(self):
        assert self.view.name

    def test_view_endpoint(self):
        assert self.view.endpoint

    def test_view_reload(self):
        view = self.view.__class__(*self.view._class_args, **self.view._class_kwargs)
        print(vars(view))
        print(vars(self.view))
        assert vars(view) == vars(self.view)

    @staticmethod
    def create_view(endpoint: str, data="testing", name: str = None) -> ApiView:
        path = endpoint
        view_name = name

        class TView(ApiView):
            name = view_name or hash_gen()
            endpoint = path

            def get(self):
                return data

        return TView()
