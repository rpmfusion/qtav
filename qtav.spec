%global project QtAV
%global repo %{project}

# QTAV's builds fail with FFMpeg-5*
# https://bugzilla.rpmfusion.org/show_bug.cgi?id=6271
%if 0%{?fedora} > 35
%bcond_without oldffmpeg
%else
%bcond_with oldffmpeg
%endif

Name:           qtav
Version:        1.13.0
Release:        19%{?dist}
Summary:        A media playback framework based on Qt and FFmpeg
License:        LGPLv2+ and GPLv3+ and BSD
URL:            http://www.qtav.org/
Source0:        https://github.com/wang-bin/QtAV/archive/v%{version}/%{project}-%{version}.tar.gz
Patch0:         https://github.com/wang-bin/QtAV//commit/5abba7f0505e75fceabd4dd8992a7e02bb149d64.patch#/fix_qt514_build.patch

# Fix builds with Qt-5.15.1
Patch1:         %{name}-fix_Qt515_builds.patch

# Exclude avresample library (bug #5350)
Patch2:         %{name}-avoid-avresample_dependency.patch

# Fix avutil test during configuration
# https://bugzilla.rpmfusion.org/show_bug.cgi?id=6271
Patch3:         %{name}-fix-avutil_test.patch

BuildRequires:  desktop-file-utils
BuildRequires:  qt5-qtbase-devel
BuildRequires:  qt5-qtdeclarative-devel
BuildRequires:  qt5-qtquickcontrols
BuildRequires:  qt5-qtsvg-devel
BuildRequires:  libass-devel
%if %{with oldffmpeg}
BuildRequires:  compat-ffmpeg4-devel
%else
BuildRequires:  ffmpeg-devel
%endif
BuildRequires:  openal-soft-devel
BuildRequires:  libXv-devel
BuildRequires:  libva-devel
BuildRequires:  pulseaudio-libs-devel
BuildRequires:  dos2unix
Requires:       hicolor-icon-theme

%description
QtAV is a multimedia playback library based on Qt and FFmpeg.
It can help you to write a player with less effort than ever before.

Features include:
  * Hardware decoding suppprt: DXVA2, VAAPI, VDA, CedarX, CUDA.
  * OpenGL and ES2 support for Hi10P and other 16-bit YUV videos.
  * Video capture in rgb and yuv format.
  * OSD and custom filters.
  * filters in libavfilter, for example stero3d, blur.
  * Subtitle.
  * Transform video using GraphicsItemRenderer. (rotate, shear, etc)
  * Playing frame by frame (currently support forward playing).
  * Playback speed control. At any speed.
  * Variant streams: locale file, http, rtsp, etc.
  * Choose audio channel.
  * Choose media stream, e.g. play a desired audio track.
  * Multiple render engine support. Currently supports QPainter, GDI+, Direct2D,
    XV and OpenGL(and ES2).
  * Dynamically change render engine when playing.
  * Multiple video outputs for 1 player.
  * Region of interest(ROI), i.e. video cropping.
  * Video eq: brightness, contrast, saturation, hue.
  * QML support as a plugin. Most playback APIs are compatible with QtMultiMedia
    module.

%package -n lib%{name}
Summary: QtAV library
Requires: ffmpeg

%description -n lib%{name}
QtAV is a multimedia playback library based on Qt and FFmpeg.
It can help you to write a player with less effort than ever before.

This package contains the QtAV library.

%package -n lib%{name}widgets
Summary: QtAV Widgets module
Requires: libqtav%{?_isa} = %{version}-%{release}

%description -n lib%{name}widgets
QtAV is a multimedia playback library based on Qt and FFmpeg.
It can help you to write a player with less effort than ever before.

This package contains a set of widgets to play media.

%package devel
Summary: QtAV development files
Requires: libqtav%{?_isa} = %{version}-%{release}
Requires: libqtavwidgets%{?_isa} = %{version}-%{release}
Requires: qt5-qtbase-devel%{?_isa}

%description devel
QtAV is a multimedia playback library based on Qt and FFmpeg.
It can help you to write a player with less effort than ever before.

This package contains the header development files for building some
QtAV applications using QtAV headers.

%package qml-module
Summary: QtAV QML module

%description qml-module
QtAV is a multimedia playback library based on Qt and FFmpeg.
It can help you to write a player with less effort than ever before.

This package contains the QtAV QML module for Qt declarative.

%package players
Summary: QtAV/QML players
License: GPLv3
Requires: libqtav%{?_isa} = %{version}-%{release}
Requires: libqtavwidgets%{?_isa} = %{version}-%{release}
Requires: qtav-qml-module%{?_isa} = %{version}-%{release}

%description players
QtAV is a multimedia playback framework based on Qt and FFmpeg.
High performance. User & developer friendly.

This package contains the QtAV based players.

%prep
%autosetup -n %repo-%{version} -N

%patch -P0 -p1 -b .backup
%patch -P1 -p1 -b .backup
%patch -P2 -p1 -b .backup
%if %{with oldffmpeg}
%patch -P3 -p1 -b .backup
%endif

# E: script-without-shebang /usr/share/icons/hicolor/scalable/apps/QtAV.svg
# ignore them src/QtAV.svg: SVG Scalable Vector Graphics image

# delete .jar File from examples
rm -rf examples/QMLPlayer/android/gradle/wrapper/gradle-wrapper.jar

# W: doc-file-dependency /usr/share/doc/qtav-devel/examples/QMLPlayer/android/gradlew /usr/bin/env
# An included file marked as %%doc creates a possible additional dependency in
# the package.  Usually, this is not wanted and may be caused by eg. example
# scripts with executable bits set included in the package's documentation.
chmod -x examples/QMLPlayer/android/gradlew

# prepare example dir for -devel
mkdir -p _tmpdoc/examples
cp -pr examples/* _tmpdoc/examples

%build
mkdir -p build; pushd build
%if %{with oldffmpeg}
export CPATH=" -I%{_includedir}/compat-ffmpeg4"
%{_qt5_qmake} \
   QMAKE_CFLAGS="${RPM_OPT_FLAGS} -I%{_includedir}/compat-ffmpeg4" \
   QMAKE_CXXFLAGS="${RPM_OPT_FLAGS} -I%{_includedir}/compat-ffmpeg4" \
   QMAKE_LFLAGS="${RPM_LD_FLAGS} -L%{_libdir}/compat-ffmpeg4 -lavformat -lavcodec -lavutil -lavdevice -lavfilter -lswscale -lswresample" \
   QMAKE_STRIP="" \
   CONFIG+="no_rpath recheck config_libass_link release" ..
%else
export CPATH="`pkg-config --variable=includedir libswresample`"
%{_qt5_qmake} \
   QMAKE_CFLAGS="${RPM_OPT_FLAGS}" \
   QMAKE_CXXFLAGS="${RPM_OPT_FLAGS}" \
   QMAKE_LFLAGS="${RPM_LD_FLAGS}" \
   QMAKE_STRIP="" \
   CONFIG+="no_rpath recheck config_libass_link release" ..
%endif
%make_build

%install
%make_install INSTALL_ROOT=%{buildroot} -C build

rm -rf %{buildroot}%{_datadir}/doc/*
rm -rf %{buildroot}%{_qt5_archdatadir}/bin/libcommon.*
rm -rf %{buildroot}%{_qt5_headerdir}/*.h
install -d %{buildroot}%{_bindir}
ln -sfv %{_qt5_bindir}/Player %{buildroot}%{_bindir}
ln -sfv %{_qt5_bindir}/QMLPlayer %{buildroot}%{_bindir}
install -D src/QtAV.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/QtAV.svg

# library links
ln -sfv %{_libdir}/libQtAV.so %{buildroot}%{_libdir}/libQt5AV.so
ln -sfv %{_libdir}/libQtAVWidgets.so %{buildroot}%{_libdir}/libQt5AVWidgets.so

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/*.desktop

%files -n lib%{name}
%doc README.md Changelog
%license lgpl-2.1.txt
%{_libdir}/libQtAV.so.*

%files -n lib%{name}widgets
%{_libdir}/libQtAVWidgets.so.*

%files devel
%{_qt5_headerdir}/QtAV/*
%{_qt5_headerdir}/QtAVWidgets/*
%dir %{_qt5_headerdir}/QtAV/
%dir %{_qt5_headerdir}/QtAVWidgets/
%{_libdir}/libQtAV.so
%{_libdir}/libQtAV.prl
%{_libdir}/libQt5AV.so
%{_libdir}/libQtAVWidgets.so
%{_libdir}/libQtAVWidgets.prl
%{_libdir}/libQt5AVWidgets.so
%{_qt5_archdatadir}/mkspecs/features/av.prf
%{_qt5_archdatadir}/mkspecs/features/avwidgets.prf
%{_qt5_archdatadir}/mkspecs/modules/qt_lib_av.pri
%{_qt5_archdatadir}/mkspecs/modules/qt_lib_avwidgets.pri
%{_qt5_archdatadir}/mkspecs/modules/qt_lib_av_private.pri
%{_qt5_archdatadir}/mkspecs/modules/qt_lib_avwidgets_private.pri

%files qml-module
%doc README.md Changelog
%license lgpl-2.1.txt
%{_qt5_archdatadir}/qml/QtAV/libQmlAV.so
%{_qt5_archdatadir}/qml/QtAV/plugins.qmltypes
%{_qt5_archdatadir}/qml/QtAV/qmldir
%{_qt5_archdatadir}/qml/QtAV/Video.qml
%dir %{_qt5_archdatadir}/qml/QtAV/

%files players
%doc README.md Changelog
%license gpl-3.0.txt
%{_qt5_bindir}/Player
%{_qt5_bindir}/QMLPlayer
%{_bindir}/Player
%{_bindir}/QMLPlayer
%{_datadir}/applications/Player.desktop
%{_datadir}/applications/QMLPlayer.desktop
%{_datadir}/icons/hicolor/*/apps/QtAV.svg

%changelog
* Fri Aug 02 2024 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 1.13.0-19
- Rebuilt for https://fedoraproject.org/wiki/Fedora_41_Mass_Rebuild

* Sun Feb 04 2024 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 1.13.0-18
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Wed Aug 02 2023 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 1.13.0-17
- Rebuilt for https://fedoraproject.org/wiki/Fedora_39_Mass_Rebuild

* Sun Aug 07 2022 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 1.13.0-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild and ffmpeg
  5.1

* Thu Apr 07 2022 Antonio Trande <sagitter@fedoraproject.org> - 1.13.0-15
- Use compat-ffmpeg4 in Fedora 36+ (rfbz#6271)

* Tue Apr 05 2022 Leigh Scott <leigh123linux@gmail.com> - 1.13.0-14
- Rebuild for new QT5

* Wed Feb 09 2022 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 1.13.0-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Fri Nov 12 2021 Leigh Scott <leigh123linux@gmail.com> - 1.13.0-12
- Rebuilt for new ffmpeg snapshot

* Tue Aug 03 2021 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1.13.0-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Thu Feb 04 2021 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1.13.0-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Wed Jan 20 2021 Antonio Trande <sagitter@fedoraproject.org> - 1.13.0-9
- Fix bug #5350

* Fri Jan 01 2021 Leigh Scott <leigh123linux@gmail.com> - 1.13.0-8
- Rebuilt for new ffmpeg snapshot

* Tue Sep 29 2020 Antonio Trande <sagitter@fedoraproject.org> - 1.13.0-7
- Rebuild for Qt_5.15.1

* Tue Aug 18 2020 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1.13.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Apr 29 2020 Leigh Scott <leigh123linux@gmail.com> - 1.13.0-5
- Rebuild for QT-5.14

* Sat Feb 22 2020 RPM Fusion Release Engineering <leigh123linux@googlemail.com> - 1.13.0-4
- Rebuild for ffmpeg-4.3 git

* Wed Feb 05 2020 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1.13.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Mon Oct 07 2019 Leigh Scott <leigh123linux@googlemail.com> - 1.13.0-2
- Rebuild for new Qt5 version

* Sun Aug 11 2019 Antonio Trande <sagitter@fedoraproject.org> - 1.13.0-1
- Release 1.13.0
- Switch to libswresample (rpf-bug #5350)

* Wed Aug 07 2019 Leigh Scott <leigh123linux@gmail.com> - 1.12.1-0.2.20180118gitbbf3c64
- Rebuild for new ffmpeg version

* Thu Apr 18 2019 Leigh Scott <leigh123linux@googlemail.com> - 1.12.1-0.1.20180118gitbbf3c64
- Rebuild for QT-5.12
- Remove Group tag
- Fix URL tag
- Fix bad git versioning
- Fix Source tag

* Mon Mar 04 2019 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1.12.0-11.gitbbf3c64
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Sun Aug 19 2018 Leigh Scott <leigh123linux@googlemail.com> - 1.12.0-10.gitbbf3c64
- Rebuilt for Fedora 29 Mass Rebuild binutils issue

* Fri Jul 27 2018 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1.12.0-9.gitbbf3c64
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Sun Jun 17 2018 Leigh Scott <leigh123linux@googlemail.com> - 1.12.0-8.gitbbf3c64
- Rebuild for new libass version
- Remove obsolete scriptlets

* Thu Mar 08 2018 RPM Fusion Release Engineering <leigh123linux@googlemail.com> - 1.12.0-7.gitbbf3c64
- Rebuilt for new ffmpeg snapshot

* Thu Mar 01 2018 RPM Fusion Release Engineering <leigh123linux@googlemail.com> - 1.12.0-6.gitbbf3c64
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Fri Jan 19 2018 Leigh Scott <leigh123linux@googlemail.com> - 1.12.0-5.gitbbf3c64
- Update to newer snapshot to fix ffmpeg build issue

* Thu Jan 18 2018 Leigh Scott <leigh123linux@googlemail.com> - 1.12.0-4.gitcbab79e
- Rebuilt for ffmpeg-3.5 git

* Mon Jan 15 2018 Nicolas Chauvet <kwizart@gmail.com> - 1.12.0-3.gitcbab79e
- Update to VA-API 1.0.0

* Thu Aug 31 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 1.12.0-2.gitcbab79e
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Thu Jun 29 2017 Martin Gansser <martinkg@fedoraproject.org> - 1.12.0-1gitcbab79e
- Update to 1.12.0-1gitcbab79e
- Add BR qt5-qtsvg-devel

* Sat Apr 29 2017 Leigh Scott <leigh123linux@googlemail.com> - 1.11.0-5.gitcf78e27
- Rebuild for ffmpeg update

* Mon Mar 20 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 1.11.0-4.gitcf78e27
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Oct 17 2016 Martin Gansser <martinkg@fedoraproject.org> - 1.11.0-3.gitcf78e27
- Fix BZ#4294: https://fedoraproject.org/wiki/Packaging:Versioning#Post-Release_packages

* Mon Sep 19 2016 Martin Gansser <martinkg@fedoraproject.org> - 1.11.0-2gitcf78e27
- Update to 1.11.0-2gitcf78e27

* Sat Sep 17 2016 Antonio Trande <sagitter@fedoraproject.org> - 1.11.0-1.gitbc46ae4
- Disable debug config
- Fix Release tag (this is a post-stable-release)
- Add qt5-qtquickcontrols as BR package
- Add QMAKE_STRIP=""

* Sat Sep 17 2016 Leigh Scott <leigh123linux@googlemail.com> - 1.11.0-0.6gitbc46ae4
- Add redhat flags to LDFLAGS

* Sat Sep 17 2016 Martin Gansser <martinkg@fedoraproject.org> - 1.11.0-0.5gitbc46ae4
- Update to 1.11.0-0.5gitbc46ae4
- Dropped config option no_config_tests

* Fri Sep 02 2016 Martin Gansser <martinkg@fedoraproject.org> - 1.11.0-0.4gitc5db90b
- Disabled config test by adding no_config_tests

* Mon Aug 29 2016 Martin Gansser <martinkg@fedoraproject.org> - 1.11.0-0.3gitc5db90b
- update to last git release

* Sun Jul 24 2016 Martin Gansser <martinkg@fedoraproject.org> - 1.11.0-0.2git116b90d
- update to last git release

* Tue Jun 21 2016 Martin Gansser <martinkg@fedoraproject.org> - 1.11.0-0.1git3b418cb
- update to last git release

* Thu Mar 24 2016 Martin Gansser <martinkg@fedoraproject.org> - 1.10.0-0.2gitd930be8
- update to last git release
- added debug flag
- renamed player to Player due conflicts with the package player

* Fri Mar 18 2016 Martin Gansser <martinkg@fedoraproject.org> - 1.10.0-0.1git97e5d32
- update to last git release

* Tue Feb 09 2016 Martin Gansser <martinkg@fedoraproject.org> - 1.9.0-0.5gited374dc
- update to last git release
- spec file cleanup
- removed BR portaudio-devel

* Sun Feb 07 2016 Martin Gansser <martinkg@fedoraproject.org> - 1.9.0-0.4gite7da6d1
- added QMAKE_LFLAGS flag due unused-direct-shlib-dependency warnings
- update to last git release

* Sun Feb 07 2016 Martin Gansser <martinkg@fedoraproject.org> - 1.9.0-0.3gitfafd3b0
- corrected license tag
- added QMAKE flag CONFIG+=no_rpath
- added Requires ffmpeg to libqtav sub-package
- removed ldconfig for devel sub-package
- append private-devel files to devel sub-package
- removed jar file
- removed documentation and license files from devel and libqtavwidgets sub-package
- removed empty sdk sub-package

* Sat Feb 06 2016 Martin Gansser <martinkg@fedoraproject.org> - 1.9.0-0.2gitfafd3b0
- added BR desktop-file-utils
- corrected Pre-Release tag
- deleted llvm stuff
- fix Optimization flags are not honored

* Wed Feb 03 2016 Martin Gansser <martinkg@fedoraproject.org> - 1.9.0-0.1gitfafd3b0
- initial build
