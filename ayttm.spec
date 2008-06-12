%define name    ayttm 
%define version	0.5.0.10
%define fver	0.5.0-10
%define cvs	0
%if %cvs
%define release	%mkrel 0.%cvs.1
%else
%define release	%mkrel 1
%endif

# Enable to turn off stripping of binaries
%{?_without_stripping: %{expand: %%define __os_install_post %%{nil}}}

Summary:	Instant messaging client 
Name:		%{name}
Version:	%{version}
Release:	%{release}
License:	GPLv2+
Group:		Networking/Instant messaging
%if %cvs
Source:		%{name}-%{cvs}.tar.bz2
%else
Source:		%{name}-%{fver}.tar.bz2
%endif
Source10:	%{name}.16.png.bz2
Source11:	%{name}.32.png.bz2
Source12:	%{name}.48.png.bz2
Source20:	%{name}-puddles-smileys.tar.bz2
# From upstream CVS: replace a deprecated function (build fails without
# this) - AdamW 2007/11
Patch0:		ayttm-0.5.0.10-unref.patch
Obsoletes:	everybuddy
Provides:	everybuddy
URL:		http://ayttm.sourceforge.net
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	glib2-devel
BuildRequires:	gtk+2-devel
BuildRequires:	libltdl-devel
BuildRequires:	libesound-devel
BuildRequires:	libarts-devel
BuildRequires:	freetype-devel
BuildRequires:	gettext-devel
BuildRequires:	automake >= 1.6
BuildRequires:	libaspell-devel
BuildRequires:	libxpm-devel
BuildRequires:	libgpgme-devel < 0.4
BuildRequires:	openssl-devel
BuildRequires:	libjasper-devel
BuildRoot:	%{_tmppath}/%{name}-buildroot

%description
Ayttm is designed to become a Universal Instant Messaging client
designed to seamlessly integrate all existing Instant Messaging clients and
provide a single consistant user interface. Currently, Ayttm supports
sending and receiving messages via AOL, ICQ, Yahoo, MSN, IRC and Jabber.

%prep
%setup -q -n %{name}-%{fver}
%setup -q -n %{name}-%{fver} -T -D -a20
%patch0 -p1 -b .unref

%build
%if %cvs
./gen
%endif
#export GLIB_CONFIG=/usr/bin/glib-config
autoconf
%configure2_5x --enable-xft --enable-esd --disable-arts --enable-lj \
            --enable-jasper-filter --enable-smtp

# Parallel build fails - AdamW
make

%install
%__rm -rf %{buildroot}
%makeinstall 

# We don't need the .a files...
%__rm -f %{buildroot}/%{_libdir}/%{name}/*.a

mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/mandriva-%{name}.desktop << EOF
[Desktop Entry]
Name=Ayttm
Comment=Universal Instant Messaging Client
Exec=%{_bindir}/ayttm
Icon=%{name}
Terminal=false
Type=Application
Categories=Network;InstantMessaging;
EOF

%__mkdir -p %{buildroot}%{_iconsdir}/hicolor/{16x16,32x32,48x48}/apps
%__bzip2 -dc %{SOURCE10} > %{buildroot}%{_iconsdir}/hicolor/16x16/apps/%{name}.png
%__bzip2 -dc %{SOURCE11} > %{buildroot}%{_iconsdir}/hicolor/32x32/apps/%{name}.png
%__bzip2 -dc %{SOURCE12} > %{buildroot}%{_iconsdir}/hicolor/48x48/apps/%{name}.png

# Extra smileys
%__cp -a 'Puddles' %{buildroot}%{_datadir}/%{name}/smileys

# remove unpackaged files
%__rm -f %{buildroot}%{_sysconfdir}/X11/applnk/Internet/Ayttm.desktop
%__rm -f %{buildroot}%{_datadir}/applnk/Internet/ayttm.desktop
%__rm -f %{buildroot}%{_datadir}/gnome/apps/Internet/ayttm.desktop

%find_lang %name

%clean 
%__rm -rf %{buildroot}

%post
%if %mdkversion < 200900
%update_menus
%update_icon_cache hicolor
%endif

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

%if %mdkversion < 200900
%postun
%clean_menus
%clean_icon_cache hicolor
%endif

%files -f %name.lang
%defattr (-,root,root)
%doc doc/ AUTHORS ChangeLog INSTALL README TODO ABOUT-NLS
%{_bindir}/*
%{_mandir}/man1/*
%{_datadir}/applications/mandriva-%{name}.desktop
%{_datadir}/pixmaps/%{name}.png
%{_datadir}/%{name}
%{_libdir}/%{name}
%{_iconsdir}/hicolor/*/apps/%{name}.png
%config(noreplace) %{_sysconfdir}/%{name}rc

