%define name    ayttm 
%define version 0.4.6
%define release %mkrel 4

# Enable to turn off stripping of binaries
%{?_without_stripping: %{expand: %%define __os_install_post %%{nil}}}

# Define Mandrake Linux version we are building for
# (macro shamelessly stolen from the XFree86 spec file)
%define mdkversion %(perl -pe '/(\\d+)\\.(\\d)\\.?(\\d)?/; $_="$1$2".($3||0)' %{_sysconfdir}/mandrake-release)

# with xft
%define with_xft 0
%if %mdkversion >= 910
  %define with_xft 1
%endif

%if %mdkversion >= 1000
  %define menusection "Internet/Instant messaging"
%else
  %define menusection "Networking/Instant messaging"
%endif

%{?_with_xft: %{expand: %%define with_xft 1}}
%{?_without_xft: %{expand: %%define with_xft 0}}

Summary: Instant messaging client 
Name: %{name}
Version: %{version}
Release: %{release}
License: GPL
Group: Networking/Instant messaging
Source: %{name}-%{version}.tar.bz2
Source10: %{name}.16.png.bz2
Source11: %{name}.32.png.bz2
Source12: %{name}.48.png.bz2
Source20: %{name}-puddles-smileys.tar.bz2
# build fix for our current gcc (4.1)
Patch0: ayttm-0.4.6-lvalue_buildfix.patch
# patch to avoid ayttm to be linked against glib2
# (without this ayttm segfaults when started)
Patch1: ayttm-0.4.6-noglib2.patch
Obsoletes: everybuddy
Provides: everybuddy
URL: http://ayttm.sourceforge.net
BuildRequires: bison
BuildRequires: flex
BuildRequires: glib-devel
BuildRequires: gtk+-devel
BuildRequires: libltdl-devel
BuildRequires: libesound-devel
BuildRequires: libarts-devel
BuildRequires: freetype-devel
BuildRequires: libgdk-pixbuf2-devel
BuildRequires: gettext-devel
BuildRequires: automake >= 1.6
%if %mdkversion >= 920
BuildRequires: libaspell-devel
%else
BuildRequires: libpspell-devel
%endif
BuildRequires: libxpm-devel
BuildRequires: libgpgme03_6-devel
BuildRequires: openssl-devel
BuildRequires: libjasper-devel
ExclusiveArch: %{ix86}
BuildRoot: %{_tmppath}/%{name}-buildroot

%description
Ayttm is designed to become a Universal Instant Messaging client
designed to seamlessly integrate all existing Instant Messaging clients and
provide a single consistant user interface. Currently, Ayttm supports
sending and receiving messages via AOL, ICQ, Yahoo, MSN, IRC and Jabber.
Ayttm is a fork of everybuddy, which is being maintained and has bug
fixes made to it.  Everybuddy is now obsolete so you should use ayttm
instead.  To convert your prefs from everybuddy to ayttm start ayttm,
configure an account and then use the importer on the Edit menu.

%prep
#CVS build setup
#%setup -q -n %{name}-20030130
%setup -q
%patch0 -p1 -b .ayttm-0.4.6-lvalue_buildfix
%patch1 -p1 -b .noglib2
%setup -q -T -D -a20

%build
# gen is needed for CVS builds or anytime we
# patch the configure script.
#./gen
%if %with_xft
  WITH_XFT='--enable-xft'
%else
  WITH_XFT=''
%endif
export GLIB_CONFIG=/usr/bin/glib-config
autoconf
%configure $WITH_XFT --enable-esd --disable-arts --enable-lj \
            --enable-jasper-filter --enable-smtp
%make

%install
%__rm -rf $RPM_BUILD_ROOT
%makeinstall 

# We don't need the .a files...
%__rm -f %{buildroot}/%{_libdir}/%{name}/*.a

(cd $RPM_BUILD_ROOT
%__mkdir -p .%{_menudir}
%__cat > .%{_menudir}/%{name} <<EOF
?package(%{name}):\
command="%{_bindir}/ayttm"\
icon="%{name}.png"\
title="Ayttm"\
longtitle="Universal Instant Messaging Client"\
needs="x11"\
section=%{menusection}\
xdg="true"
EOF
)

mkdir -p $RPM_BUILD_ROOT%{_datadir}/applications
cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-%{name}.desktop << EOF
[Desktop Entry]
Encoding=UTF-8
Name=Ayttm
Comment=Universal Instant Messaging Client
Exec=%{_bindir}/ayttm
Icon=%{name}
Terminal=false
Type=Application
Categories=X-MandrivaLinux-Internet-InstantMessaging;Network;InstantMessaging;
EOF

%__mkdir -p $RPM_BUILD_ROOT%{_miconsdir}
%__mkdir -p $RPM_BUILD_ROOT%{_liconsdir}
%__bzip2 -dc %{SOURCE10} > $RPM_BUILD_ROOT%{_miconsdir}/%{name}.png
%__bzip2 -dc %{SOURCE11} > $RPM_BUILD_ROOT%{_iconsdir}/%{name}.png
%__bzip2 -dc %{SOURCE12} > $RPM_BUILD_ROOT%{_liconsdir}/%{name}.png

# Extra smileys
%__cp -a 'Puddles' $RPM_BUILD_ROOT%{_datadir}/%{name}/smileys

# remove unpackaged files
%__rm -f $RPM_BUILD_ROOT%{_sysconfdir}/X11/applnk/Internet/Ayttm.desktop
%__rm -f $RPM_BUILD_ROOT%{_datadir}/applnk/Internet/ayttm.desktop
%__rm -f $RPM_BUILD_ROOT%{_datadir}/gnome/apps/Internet/ayttm.desktop

%find_lang %name

%post
%{update_menus}

# Fix the paths to the modules in the prefs files...
# Note that $ has to be escaped so the shell doesn't wack 
# them.
%__perl <<EOP
while (my (@pwent) = getpwent()) {
  my \$homedir = \$pwent[7];
  my \$prefs;
  if (open PREFS, "<\$homedir/.ayttm/prefs") {
    while (<PREFS>) {
      s!%{_datadir}/%{name}/modules!%{_libdir}/%{name}!g;
      \$prefs .= \$_;
    }
    close PREFS;
    unless (rename("\$homedir/.ayttm/prefs","\$homedir/.ayttm/prefs.orig")) {
      warn "Cannot rename \$homedir/.ayttm/prefs to \$homedir/.ayttm/prefs.orig";
      next;
    }
    open PREFS, ">\$homedir/.ayttm/prefs";
    print PREFS \$prefs;
    close PREFS;
  }
}
EOP

%postun
%{clean_menus}

%files -f %name.lang
%defattr (-,root,root)
%doc doc/ AUTHORS COPYING ChangeLog INSTALL README TODO ABOUT-NLS
%{_bindir}/*
%{_mandir}/man1/*
%{_datadir}/applications/mandriva-%{name}.desktop
%{_datadir}/pixmaps/%{name}.png
%dir %_datadir/%name
%_datadir/%name/*
%dir %_libdir/%name
%_libdir/%name/*
%{_iconsdir}/*.png
%{_miconsdir}/*.png
%{_liconsdir}/*.png
%{_menudir}/*
%config(noreplace) %{_sysconfdir}/%{name}rc


%clean 
%__rm -rf $RPM_BUILD_ROOT

