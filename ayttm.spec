Summary:	Instant messaging client 
Name:		ayttm
Version:	0.6.2
Release:	4
License:	GPLv2+
Group:		Networking/Instant messaging
Source:		http://downloads.sourceforge.net/project/ayttm/ayttm/%{version}/%{name}-%{version}.tar.bz2
Source10:	%{name}.16.png.bz2
Source11:	%{name}.32.png.bz2
Source12:	%{name}.48.png.bz2
Source20:	%{name}-puddles-smileys.tar.bz2
Patch0:		ayttm-0.6.2-fix-str-fmt.patch
Patch1:		ayttm-0.6.2-link.patch
Patch2:		ayttm-0.6.2-imagedir.patch
Obsoletes:	everybuddy
Provides:	everybuddy
URL:		https://ayttm.sourceforge.net
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	gettext-devel
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(gtk+-2.0)
BuildRequires:	libgpgme-devel
BuildRequires:	libltdl-devel
BuildRequires:	pkgconfig(enchant)
BuildRequires:	pkgconfig(esound)
BuildRequires:	pkgconfig(jasper)
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(x11)
BuildRequires:	pkgconfig(xpm)
BuildRequires:	pkgconfig(xscrnsaver)

%description
Ayttm is designed to become a Universal Instant Messaging client
designed to seamlessly integrate all existing Instant Messaging clients and
provide a single consistant user interface. Currently, Ayttm supports
sending and receiving messages via AOL, ICQ, Yahoo, MSN, IRC and Jabber.

%prep
%setup -q -n %{name}-%{version}
%setup -q -n %{name}-%{version} -T -D -a20
%patch0 -p0
%patch1 -p0
%patch2 -p0

%build
autoreconf -fi
%configure2_5x --enable-esd --disable-arts --enable-lj \
            --enable-jasper-filter --enable-smtp --disable-static

%make

%install
%makeinstall_std


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

rm -f %buildroot%_datadir/applnk/Internet/ayttm.desktop
rm -f %buildroot%_datadir/gnome/apps/Internet/ayttm.desktop

mkdir -p %{buildroot}%{_iconsdir}/hicolor/{16x16,32x32,48x48}/apps
bzip2 -dc %{SOURCE10} > %{buildroot}%{_iconsdir}/hicolor/16x16/apps/%{name}.png
bzip2 -dc %{SOURCE11} > %{buildroot}%{_iconsdir}/hicolor/32x32/apps/%{name}.png
bzip2 -dc %{SOURCE12} > %{buildroot}%{_iconsdir}/hicolor/48x48/apps/%{name}.png

# Extra smileys
cp -a 'Puddles' %{buildroot}%{_datadir}/%{name}/smileys

%find_lang %{name}

%post
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

%files -f %{name}.lang
%doc doc/ AUTHORS ChangeLog INSTALL README TODO ABOUT-NLS
%{_bindir}/*
%{_mandir}/man1/*
%{_datadir}/applications/mandriva-%{name}.desktop
%{_datadir}/%{name}
%{_libdir}/%{name}
%{_iconsdir}/hicolor/*/apps/%{name}.png
%config(noreplace) %{_sysconfdir}/%{name}rc

