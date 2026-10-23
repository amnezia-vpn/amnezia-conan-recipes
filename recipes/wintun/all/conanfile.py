from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.layout import basic_layout
from conan.tools.files import get, copy

import os

class Wintun(ConanFile):
    name = "wintun"
    settings = "os", "arch"

    def layout(self):
        basic_layout(self)

    def validate(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("wintun is only available on Windows")

    @property
    def _dll_arch(self):
        return {
            "x86_64": "amd64",
            "armv8": "arm64",
            "x86": "x86",
            "armv7": "arm",
        }[str(self.settings.arch)]

    def build(self):
        get(self, **self.conan_data["sources"][str(self.version)], strip_root=True)

    def package(self):
        copy(self, "wintun.h",
             src=os.path.join(self.build_folder, "include"),
             dst=os.path.join(self.package_folder, "include"))
        copy(self, "wintun.dll",
             src=os.path.join(self.build_folder, "bin", self._dll_arch),
             dst=os.path.join(self.package_folder, "bin"),
             keep_path=False)

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.set_property("cmake_target_name", "amnezia::wintun")
