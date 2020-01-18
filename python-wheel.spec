# The only function of bootstrap is that it disables the test suite:
#   bcond_with bootstrap = tests enabled
# RHEL7: Therefore we're leaving the bootstrap always on, as we don't carry the
# test dependencies in the minimal Python 3 stack in RHEL7.
%bcond_without bootstrap

# RHEL7: Disabled building of python2, but keeping it in the spec to keep the
# spec as similar as possible with RHEL8/Fedora
%bcond_with python2
%bcond_without python3

%global pypi_name wheel

Name:           python-%{pypi_name}
Version:        0.31.1
Release:        5%{?dist}
Summary:        Built-package format for Python

License:        MIT
URL:            https://github.com/pypa/wheel
Source0:        %{url}/archive/%{version}/%{pypi_name}-%{version}.tar.gz
BuildArch:      noarch

# We need to remove wheel's own implementation of crypto due to FIPS concerns.
# See more: https://bugzilla.redhat.com/show_bug.cgi?id=1722983
# Upstream commit: https://github.com/pypa/wheel/commit/d3f5918ccbb1c79e2fc42b7766626a0aa20dc438
Patch0: removed-wheel-signing-and-verifying-features.patch

%global _description \
A built-package format for Python.\
\
A wheel is a ZIP-format archive with a specially formatted filename and the\
.whl extension. It is designed to contain all the files for a PEP 376\
compatible install in a way that is very close to the on-disk format.

%description %{_description}

%if %{with python2}
%package -n     python2-%{pypi_name}
Summary:        %{summary}
BuildRequires:  python2-devel
BuildRequires:  python2-setuptools
%if %{without bootstrap}
BuildRequires:  python2-pytest
BuildRequires:  python2-pyxdg
BuildRequires:  python2-keyring
%endif
%{?python_provide:%python_provide python2-%{pypi_name}}

%description -n python2-%{pypi_name} %{_description}

Python 2 version.
%endif


%if %{with python3}
%package -n     python3-%{pypi_name}
Summary:        %{summary}
BuildRequires:  python3-devel
# RHEL7: python-wheel is rebuilt before the final build of python3, which
# adds the dependency on python3-rpm-generators, so we require it manually.
BuildRequires:  python3-rpm-generators
BuildRequires:  python3-setuptools
%if %{without bootstrap}
BuildRequires:  python3-pytest
BuildRequires:  python3-pyxdg
BuildRequires:  python3-keyring
%endif
%{?python_provide:%python_provide python3-%{pypi_name}}

# We're replacing the functionality of the python36 packages from EPEL
Provides: python36-wheel = %{version}-%{release}
Obsoletes: python36-wheel < %{version}-%{release}

%description -n python3-%{pypi_name} %{_description}

Python 3 version.
%endif


%prep
%autosetup -n %{pypi_name}-%{version} -p1
# remove unneeded shebangs
sed -ie '1d' %{pypi_name}/{egg2wheel,wininst2wheel}.py


%build
%if %{with python2}
%py2_build
%endif
%if %{with python3}
%py3_build
%endif


%install
%if %{with python3}
%py3_install
mv %{buildroot}%{_bindir}/%{pypi_name}{,-%{python3_version}}
ln -s %{pypi_name}-%{python3_version} %{buildroot}%{_bindir}/%{pypi_name}-3
%endif

%if %{with python2}
%py2_install
mv %{buildroot}%{_bindir}/%{pypi_name}{,-%{python2_version}}
ln -s %{pypi_name}-%{python2_version} %{buildroot}%{_bindir}/%{pypi_name}-2
ln -s %{pypi_name}-2 %{buildroot}%{_bindir}/%{pypi_name}
%endif

%if %{without bootstrap}
%check
rm setup.cfg
%if %{with python2}
PYTHONPATH=%{buildroot}%{python2_sitelib} py.test-2 -v --ignore build
%endif
%if %{with python3}
PYTHONPATH=%{buildroot}%{python3_sitelib} py.test-3 -v --ignore build
%endif
%endif

%if %{with python2}
%files -n python2-%{pypi_name}
%license LICENSE.txt
%doc CHANGES.txt README.rst
%{_bindir}/%{pypi_name}
%{_bindir}/%{pypi_name}-2
%{_bindir}/%{pypi_name}-%{python2_version}
%{python2_sitelib}/%{pypi_name}*
%endif

%if %{with python3}
%files -n python3-%{pypi_name}
%license LICENSE.txt
%doc CHANGES.txt README.rst
%{_bindir}/%{pypi_name}-3
%{_bindir}/%{pypi_name}-%{python3_version}
%{python3_sitelib}/%{pypi_name}*
%endif

%changelog
* Mon Jul 22 2019 Tomas Orsava <torsava@redhat.com> - 0.31.1-5
- Removed wheel's own implementation of crypto due to FIPS concerns
Resolves: rhbz#1722983

* Mon Jan 14 2019 Lumír Balhar <lbalhar@redhat.com> - 0.31.1-4
- Converting specfile from F29 to RHEL7
- Disabled building of the Python 2 subpackage
- Disabled tests (by setting the bootstrap on - see note)
- Removed python-wheel-wheel package with the wheel of wheel
Resolves: rhbz#1660574

* Wed Aug 15 2018 Miro Hrončok <mhroncok@redhat.com> - 1:0.31.1-3
- Create python-wheel-wheel package with the wheel of wheel

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.31.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Sat Jul 07 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1:0.31.1-1
- Update to 0.31.1

* Mon Jun 18 2018 Miro Hrončok <mhroncok@redhat.com> - 1:0.30.0-3
- Rebuilt for Python 3.7

* Wed Jun 13 2018 Miro Hrončok <mhroncok@redhat.com> - 1:0.30.0-2
- Bootstrap for Python 3.7

* Fri Feb 23 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1:0.30.0-1
- Update to 0.30.0

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.30.0a0-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Aug 29 2017 Tomas Orsava <torsava@redhat.com> - 0.30.0a0-8
- Switch macros to bcond's and make Python 2 optional to facilitate building
  the Python 2 and Python 3 modules

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.30.0a0-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.30.0a0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Jan 03 2017 Charalampos Stratakis <cstratak@redhat.com> - 0.30.0a0-5
- Enable tests

* Fri Dec 09 2016 Charalampos Stratakis <cstratak@redhat.com> - 0.30.0a0-4
- Rebuild for Python 3.6 without tests

* Tue Dec 06 2016 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 0.30.0a0-3
- Add bootstrap method

* Mon Sep 19 2016 Charalampos Stratakis <cstratak@redhat.com> - 0.30.0a0-2
- Use the python_provide macro

* Mon Sep 19 2016 Charalampos Stratakis <cstratak@redhat.com> - 0.30.0a0-1
- Update to 0.30.0a0
- Added patch to remove keyrings.alt dependency

* Wed Aug 10 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.29.0-1
- Update to 0.29.0
- Cleanups and fixes

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.26.0-3
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.26.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Oct 13 2015 Robert Kuska <rkuska@redhat.com> - 0.26.0-1
- Update to 0.26.0
- Rebuilt for Python3.5 rebuild

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.24.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue Jan 13 2015 Slavek Kabrda <bkabrda@redhat.com> - 0.24.0-3
- Make spec buildable in EPEL 6, too.
- Remove additional sources added to upstream tarball.

* Sat Jan 03 2015 Matej Cepl <mcepl@redhat.com> - 0.24.0-2
- Make python3 conditional (switched off for RHEL-7; fixes #1131111).

* Mon Nov 10 2014 Slavek Kabrda <bkabrda@redhat.com> - 0.24.0-1
- Update to 0.24.0
- Remove patches merged upstream

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.22.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri Apr 25 2014 Matej Stuchlik <mstuchli@redhat.com> - 0.22.0-3
- Another rebuild with python 3.4

* Fri Apr 18 2014 Matej Stuchlik <mstuchli@redhat.com> - 0.22.0-2
- Rebuild with python 3.4

* Thu Nov 28 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 0.22.0-1
- Initial package.
