# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import importlib

from django.apps import AppConfig


class IpVerificationConfig(AppConfig):
    name = "ip_verification"

    def _get_dotted_path_function(self, dotted_path):
        dotted_path = self.name + dotted_path if dotted_path.startswith(".") else dotted_path
        module_path, method_name = dotted_path.rsplit(".", 1)
        module_object = importlib.import_module(module_path)
        return getattr(module_object, method_name)

    @property
    def test_result_link_factory(self):
        dotted_path = ".tests.factories.test_result_link_factory"
        return self._get_dotted_path_function(dotted_path)

    @property
    def get_compute_secs(self):
        dotted_path = ".utils.get_compute_secs"
        return self._get_dotted_path_function(dotted_path)
