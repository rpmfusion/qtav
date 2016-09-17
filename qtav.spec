# https://github.com/wang-bin/QtAV/commit/bc46ae44ac1406e575f9e694b556a7be2d55380e
%global commit0 bc46ae44ac1406e575f9e694b556a7be2d55380e
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

%global project QtAV
%global repo %{project}

Name:           qtav
Version:        1.11.0
Release:        0.5git%{shortcommit0}%{?dist}
Summary:        A media playback framework based on Qt and FFmpeg
License:        LGPLv2+ and GPLv3+ and BSD
Group:          Development/Libraries
Url:            http://www.qtav.org/
Source0:        https://github.com/wang-bin/QtAV/archive/%{commit0}/%{project}-%{commit0}.tar.gz#/%{project}-%{shortcommit0}.tar.gz

BuildRequires:  desktop-file-utils
BuildRequires:  qt5-qtbase-devel
BuildRequires:  qt5-qtdeclarative-devel
BuildRequires:  libass-devel
BuildRequires:  ffmpeg-devel
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
Requires: qt5-qtbase-devel

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
%autosetup -n %repo-%{commit0}

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
export CPATH="`pkg-config --variable=includedir libavformat`"
mkdir build; pushd build
%{_qt5_qmake} \
   QMAKE_CFLAGS="%{optflags}"                          \
   QMAKE_CXXFLAGS="%{optflags}"                        \
   QMAKE_LFLAGS="-Wl,--as-needed"                      \
   CONFIG+="no_rpath recheck config_libass_link debug" \
   ..
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

%post -n lib%{name} -p /sbin/ldconfig
%post -n lib%{name}widgets -p /sbin/ldconfig

%post players
/usr/bin/update-desktop-database &> /dev/null || :
touch --no-create %{_datadir}/icons/hicolor &>/dev/null ||:

%postun -n lib%{name} -p /sbin/ldconfig
%postun -n lib%{name}widgets -p /sbin/ldconfig

%postun players
/usr/bin/update-desktop-database &> /dev/null || :
if [ $1 -eq 0 ]; then
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null ||:
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans players
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

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
