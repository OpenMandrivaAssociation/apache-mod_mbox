%define snap r670198

#Module-Specific definitions
%define mod_name mod_mbox
%define mod_conf A50_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary: 	Mailing list archive browser
Name: 		apache-%{mod_name}
Version: 	0.2
Release: 	%mkrel 1.%{snap}.10
License: 	Apache License
Group: 		System/Servers
URL: 		http://httpd.apache.org/mod_mbox/
Source0:	%{mod_name}-%{version}-%{snap}.tar.gz
Source1:	%{mod_conf}
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	file
BuildRequires:	automake
BuildRequires:	autoconf2.5
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
mod_mbox is a mailing list archive browser. Functionality includes:
     
 o A dynamic browsing interface, using AJAX (Asynchronous Javascript And XML)
 o A flat, Javascript-less interface, using static XHTML
 o Mail attachments and MIME parts viewing and downloading

%prep

%setup -q -n %{mod_name}

cp %{SOURCE1} %{mod_conf}

for i in `find . -type d -name .svn`; do
    if [ -e "$i" ]; then rm -rf $i; fi >&/dev/null
done

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build
export WANT_AUTOCONF_2_5=1
rm -f configure
rm -rf autom4te.cache
touch module-2.0/config.in config.in
libtoolize --copy --force; aclocal -I m4; automake --add-missing --copy --foreign; autoconf --force

%configure2_5x --localstatedir=/var/lib \
    --with-apxs=%{_sbindir}/apxs

%make

%install
rm -rf %{buildroot}

%makeinstall_std

mv %{buildroot}%{_libdir}/apache %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc CHANGES LICENSE NOTICE README STATUS scripts data
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/mod_*.so
%attr(0755,root,root) %{_bindir}/mod-mbox-util
