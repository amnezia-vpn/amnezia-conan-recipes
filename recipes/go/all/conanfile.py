from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.layout import basic_layout
from conan.tools.files import get, copy

import os

class Golang(ConanFile):
    name = "go"
    settings = "os", "arch"

    @property
    def _sources(self):
        base = self.conan_data["sources"][str(self.version)]
        base_os = base.get(str(self.settings.os), None)
        if base_os is None:
            return None
        return base_os.get(str(self.settings.arch), None)

    def layout(self):
        basic_layout(self)

    def validate(self):
        if not self._sources:
            raise ConanInvalidConfiguration(
                f"{self.name} v{self.version} is not supported on {self.settings.os}/{self.settings.arch}"
            )
    
    def build(self):
        get(self, **self._sources, strip_root=True, destination="go")

    def package(self):
        copy(self, "*", src=os.path.join(self.build_folder, "go"), dst=self.package_folder)

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
