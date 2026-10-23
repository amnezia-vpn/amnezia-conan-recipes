from conan import ConanFile
from conan.tools.layout import basic_layout
from conan.tools.files import download, copy, get

import os

class V2rayRulesDat(ConanFile):
    name = "v2ray-rules-dat"

    def layout(self):
        basic_layout(self, build_folder=".")

    def source(self):
        download(self, **self.conan_data["sources"][str(self.version)]["geoip.dat"], filename="geoip.dat")
        download(self, **self.conan_data["sources"][str(self.version)]["geosite.dat"], filename="geosite.dat")

    def package(self):
        copy(self, "*.dat", src=self.build_folder, dst=self.package_folder)

    def package_info(self):
        self.cpp_info.set_property("cmake_target_name", "Loyalsoldier::v2ray-rules-dat")
        self.cpp_info.set_property("cmake_extra_variables", {
            "GEOSITE_DAT_PATH": os.path.join(self.package_folder, "geosite.dat").replace("\\", "/"),
            "GEOIP_DAT_PATH": os.path.join(self.package_folder, "geoip.dat").replace("\\", "/")
        })
