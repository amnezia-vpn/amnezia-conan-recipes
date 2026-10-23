from conan import ConanFile
from conan.tools.layout import basic_layout
from conan.tools.files import download, copy
from conan.errors import ConanInvalidConfiguration

import os

class WinSplitTunnel(ConanFile):
    name = "win-split-tunnel"
    settings = "os", "arch"

    @property
    def _sources(self):
        return self.conan_data["sources"][str(self.version)].get(str(self.settings.arch))

    def layout(self):
        basic_layout(self)

    def validate(self):
        if not str(self.settings.os).startswith("Windows"):
            raise ConanInvalidConfiguration(
                f"{self.name} v{self.version} supports only Windows"
            )
        if not self._sources:
            raise ConanInvalidConfiguration(
                f"{self.name} v{self.version} does not support {self.settings.arch}"
            )

    def build(self):
        download(self, **self._sources["mullvad-split-tunnel.cat"], filename=os.path.join("prebuilt", "mullvad-split-tunnel.cat"))
        download(self, **self._sources["mullvad-split-tunnel.inf"], filename=os.path.join("prebuilt", "mullvad-split-tunnel.inf"))
        download(self, **self._sources["mullvad-split-tunnel.pdb"], filename=os.path.join("prebuilt", "mullvad-split-tunnel.pdb"))
        download(self, **self._sources["mullvad-split-tunnel.sys"], filename=os.path.join("prebuilt", "mullvad-split-tunnel.sys"))

    def package(self):
        copy(self, "*", src=os.path.join(self.build_folder, "prebuilt"), dst=os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_target_name", "mullvad::win-split-tunnel")
        self.cpp_info.set_property("cmake_extra_variables", {
            "WIN_SPLIT_TUNNEL_BIN": os.path.join(self.package_folder, "bin").replace("\\", "/")
        })
