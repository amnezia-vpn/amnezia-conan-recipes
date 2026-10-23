from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

import os

required_conan_version = ">=2.25"


class OpenVPN3(ConanFile):
    name = "openvpn"
    description = "OpenVPN 3 Core client library"
    homepage = "https://github.com/OpenVPN/openvpn3"
    license = "MPL-2.0 OR AGPL-3.0-only WITH openvpn3-openssl-exception"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "crypto": ["openssl", "mbedtls"],
    }
    default_options = {"crypto": "openssl"}

    def layout(self):
        basic_layout(self)

    def requirements(self):
        self.requires("asio/1.38.2")
        self.requires("lz4/[>=1.9]")
        self.requires("jsoncpp/[>=1.9.5]")
        self.requires("xxhash/[>=0.8.3]")
        if self.options.crypto == "openssl":
            self.requires("openssl/[>=3.0]@amnezia")
        else:
            self.requires("mbedtls/[>=3.0]")
        if self.settings.os == "Windows":
            self.requires("tap-windows6/[*]@amnezia")

    def package_id(self):
        self.info.settings.clear()

    def source(self):
        get(
            self,
            **self.conan_data["sources"][str(self.version)],
            strip_root=True,
        )

    def package(self):
        core_dst = os.path.join(self.package_folder, "src", "openvpn3")
        licenses_dst = os.path.join(self.package_folder, "licenses")

        copy(self, "LICENSE.md", src=self.source_folder, dst=licenses_dst)
        copy(
            self,
            "*",
            src=os.path.join(self.source_folder, "LICENSES"),
            dst=os.path.join(licenses_dst, "LICENSES"),
        )
        copy(
            self,
            "COPYRIGHT.MIT",
            src=os.path.join(self.source_folder, "tap-windows6"),
            dst=os.path.join(licenses_dst, "tap-windows6"),
        )
        copy(
            self,
            "*",
            src=os.path.join(self.source_folder, "openvpn"),
            dst=os.path.join(core_dst, "openvpn"),
        )
        copy(
            self,
            "ovpncli.?pp",
            src=os.path.join(self.source_folder, "client"),
            dst=os.path.join(core_dst, "client"),
        )

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "openvpn3")
        self.cpp_info.set_property("cmake_target_name", "amnezia::openvpn3")

        self.cpp_info.includedirs = ["src/openvpn3"]
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.resdirs = []

        self.cpp_info.sources = [
            "src/openvpn3/client/ovpncli.cpp",
            "src/openvpn3/openvpn/crypto/data_epoch.cpp",
        ]
        self.cpp_info.languages = ["C++"]

        self.cpp_info.defines = [
            "ASIO_STANDALONE",
            "USE_ASIO",
            "HAVE_LZ4",
            "OPENVPN_EXTERNAL_TUN_FACTORY",
            "OPENVPN_CORE_API_VISIBILITY_HIDDEN",
        ]
        if self.options.crypto == "openssl":
            self.cpp_info.defines.append("USE_OPENSSL")
        else:
            self.cpp_info.defines.append("USE_MBEDTLS")

        if self.settings.os == "Windows":
            self.cpp_info.defines.extend([
                # Expose the Windows APIs used by OpenVPN 3 Core.
                "_WIN32_WINNT=0x0600",
                # Shared Windows headers reference this ID without enabling TAP.
                "TAP_WIN_COMPONENT_ID=tap0901",
                # Standalone Asio has no local sockets on Windows.
                "ASIO_DISABLE_LOCAL_SOCKETS",
            ])
            # ovpncli.cpp exceeds MSVC's default object section limit.
            self.cpp_info.cxxflags.append("/bigobj")
            # OpenVPN 3 Core calls these Windows system APIs.
            self.cpp_info.system_libs.extend([
                "fwpuclnt",
                "iphlpapi",
                "wininet",
                "setupapi",
                "rpcrt4",
                "wtsapi32",
            ])
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks.extend([
                "CoreFoundation",
                "IOKit",
                "CoreServices",
                "SystemConfiguration",
            ])
            self.cpp_info.system_libs.append("pthread")
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
