# Use PAM for pserver autentization
%define pamified 1
# Use kerberos
%define kerberized 1  

Summary: A version control system
Name: cvs
Version: 1.11.23
Release: 11%{?dist}
License: GPL+ and GPLv2+ and LGPL+
Group: Development/Tools
Source0: ftp://ftp.gnu.org/non-gnu/cvs/source/stable/%{version}/cvs-%{version}.tar.bz2
Source1: cvs.xinetd
Source2: cvs.pam
Source3: cvs.sh
Source4: cvs.csh
URL: http://www.cvshome.org/
Requires(post): /sbin/install-info
Requires(preun): /sbin/install-info
Requires: vim-minimal
Buildroot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: autoconf >= 2.58, automake >= 1.7.9, libtool, zlib-devel, vim-minimal
%if %{kerberized}
BuildRequires: krb5-devel
%endif
%if %{pamified}
BuildRequires: pam-devel
%endif

Patch0: cvs-1.11.22-cvspass.patch
Patch1: cvs-1.11.19-extzlib.patch
Patch2: cvs-1.11.19-netbsd-tag.patch
Patch3: cvs-1.11.19-abortabort.patch
Patch4: cvs-1.11.1p1-bs.patch
Patch5: cvs-1.11.21-proxy.patch
Patch7: cvs-1.11.19-logmsg.patch
Patch8: cvs-1.11.19-tagname.patch
Patch9: cvs-1.11.19-comp.patch
Patch11: cvs-1.11.19-tmp.patch
Patch12: cvs-1.11.21-pam.patch
Patch13: cvs-1.11.21-diff.patch
Patch14: cvs-1.11.21-diff-kk.patch
Patch15: cvs-1.11.21-sort.patch
#Patch16: cvs-1.11.22-free.patch //unneeded
Patch17: cvs-1.11.22-ipv6-proxy.patch
#Patch18: cvs-1.11.22-diff-rm.patch
Patch19: cvs-1.11.23-getline64.patch
Patch20: cvs-1.11.22-stdinargs.patch
# Bug #530097
Patch21: cvs-1.11.23-sanity.patch


%description
CVS (Concurrent Versions System) is a version control system that can
record the history of your files (usually, but not always, source
code). CVS only stores the differences between versions, instead of
every version of every file you have ever created. CVS also keeps a log
of who, when, and why changes occurred.

CVS is very helpful for managing releases and controlling the
concurrent editing of source files among multiple authors. Instead of
providing version control for a collection of files in a single
directory, CVS provides version control for a hierarchical collection
of directories consisting of revision controlled files. These
directories and files can then be combined together to form a software
release.

%prep
%setup -q
%patch0 -p1 -b .cvspass
%patch1 -p1 -b .extzlib
%patch2 -p1 -b .netbsd-tag
%patch3 -p1 -b .abortabort
%patch4 -p1 -b .bs
%patch5 -p1 -b .proxy
%patch7 -p1 -b .log
%patch8 -p1
%patch9 -p1
%patch11 -p1 -b .tmp

%if %{pamified}
%patch12 -p1 -b .pam
%endif

%patch13 -p1 -b .diff
%patch14 -p1 -b .diff-kk
%patch15 -p1 -b .env
#%patch16 -p1 -b .free
%patch17 -p1 -b .ipv6
#%patch18 -p1 -b .diff-rm
%patch19 -p1 -b getline64
%patch20 -p1 -b .stdinargs
%patch21 -p1 -b .sanity

# Apply a patch to the generated files, OR
# run autoreconf and require autoconf >= 2.58, automake >= 1.7.9
iconv -f ISO-8859-1 -t UTF-8 < FAQ > FAQ.UTF8
touch -r FAQ FAQ.UTF8
mv FAQ.UTF8 FAQ

%build

autoreconf

%if %{pamified} 
PAM_CONFIG="--enable-pam"
%endif

%if %{kerberized}
	k5prefix=`krb5-config --prefix`
	CPPFLAGS=-I${k5prefix}/include/kerberosIV; export CPPFLAGS
	CFLAGS=-I${k5prefix}/include/kerberosIV; export CFLAGS
	LIBS="-lk5crypto"; export LIBS
	KRB_CONFIG="--with-gssapi --without-krb4 --enable-encryption"
%endif

%configure CFLAGS="$CFLAGS $RPM_OPT_FLAGS -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE" \
  $PAM_CONFIG $KRB_CONFIG CSH=/bin/csh

make

%check
if [ `id -u` -ne 0 ] ; then
	make check
fi

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
make DESTDIR="$RPM_BUILD_ROOT" install
# forcefully compress the info pages so that install-info will work properly
# in the %%post
gzip $RPM_BUILD_ROOT/%{_infodir}/cvs* || true
rm -f $RPM_BUILD_ROOT/%{_infodir}/dir
install -D -m 644 %{SOURCE1} $RPM_BUILD_ROOT/%{_sysconfdir}/xinetd.d/%{name}
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/%{name}
%if %{pamified}
install -D -m 644 %{SOURCE2} $RPM_BUILD_ROOT/%{_sysconfdir}/pam.d/cvs
%endif
install -D -m 644 %{SOURCE3} $RPM_BUILD_ROOT/%{_sysconfdir}/profile.d/cvs.sh
install -D -m 644 %{SOURCE4} $RPM_BUILD_ROOT/%{_sysconfdir}/profile.d/cvs.csh
# Don't let find provides to add csh to automatic requires
chmod a-x $RPM_BUILD_ROOT/%{_datadir}/%{name}/contrib/sccs2rcs


%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%post
/sbin/install-info /%{_infodir}/cvs.info.gz /%{_infodir}/dir &> /dev/null
/sbin/install-info /%{_infodir}/cvsclient.info.gz /%{_infodir}/dir &> /dev/null
:

%preun
if [ $1 = 0 ]; then
	/sbin/install-info --delete /%{_infodir}/cvs.info.gz /%{_infodir}/dir &> /dev/null
	/sbin/install-info --delete /%{_infodir}/cvsclient.info.gz /%{_infodir}/dir &> /dev/null
fi
:

%files
%defattr(-,root,root)
%doc AUTHORS BUGS COPYING* DEVEL-CVS FAQ HACKING MINOR-BUGS NEWS
%doc PROJECTS TODO README
%{_bindir}/*
%{_mandir}/*/*
%{_infodir}/*.info*
%{_datadir}/%{name}
%config(noreplace) %{_sysconfdir}/xinetd.d/%{name}
%dir %{_localstatedir}/%{name}
%config(noreplace) %{_sysconfdir}/pam.d/*
%config(noreplace) %{_sysconfdir}/profile.d/*

%changelog
* Wed Apr 21 2010 Petr Pisar <ppisar@redhat.com> 1.11.23-11
- Fix sanity check test suite (getopt quotation and file mode listing) as per
  bug #530097

* Mon Mar  1 2010 Jiri Moskovcak <jmoskovc@redhat.com> 1.11.23-10
- fixed license
- Related: #543948

* Tue Jan 12 2010 Jiri Moskovcak <jmoskovc@redhat.com> 1.11.23-9
- spec file fixes based on review
- Related: #543948

* Fri Oct 16 2009 Jiri Moskovcak <jmoskovc@redhat.com> 1.11.23-8
- fixed install with --excludedocs rhbz#515981

* Wed Sep 16 2009 Tomas Mraz <tmraz@redhat.com> 1.11.23-7
- Use password-auth common PAM configuration

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.11.23-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon May 25 2009  Jiri Moskovcak <jmoskovc@redhat.com> - 1.11.23.5
- added support for passing arguments thru stdin (patch from arozansk@redhat.com)
- Resolves: #501942

* Wed Apr 08 2009 Adam Jackson <ajax@redhat.com> 1.11.23-4
- Disable krb4 support to fix F12 buildroots.

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.11.23-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Jul 15 2008 Tom "spot" Callaway <tcallawa@redhat.com> 1.11.23-2
- fix license tag
- fix patches to apply with fuzz=0

* Tue Jun  3 2008 Jiri Moskovcak <jmoskovc@redhat.com> 1.11.23.1
- updated to new version 1.11.23
- fixed build on x86_64
- rewritten sanity.sh patch to match current version
- Resolves: #449424

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.11.22-13
- Autorebuild for GCC 4.3

* Mon Sep 17 2007 Jiri Moskovcak <jmoskovc@redhat.com> - 1.11.22-12
- rewriten previous patch when trying to diff  removed files
- Resolves: #277501, #242049

* Mon Jul 30 2007 Jiri Moskovcak <jmoskovc@redhat.com> - 1.11.22-11
- fix diff on removed file when "-r BASE" tag is used
- Resolves: #242049

* Fri Jun 15 2007 Stepan Kasal <skasal@redhat.com> - 1.11.22-10
- make sccs2rcs non-executable, so that find-requires does not add
  dependency on /bin/csh when /bin/csh is available
- add CSH=/bin/csh to configure, so that sccs2rcs #! line is not
  corrupted  when /bin/csh is not available
- replace the deprecated %%makeinstall (see Packaging Guidelines)

* Mon Feb 19 2007 Jindrich Novy <jnovy@redhat.com> - 1.11.22-9
- fix permissions of cvs.sh, add cvs.csh to /etc/profile.d (#225672)

* Fri Jan  5 2007 Jindrich Novy <jnovy@redhat.com> - 1.11.22-8
- fix post/preun scriptlets so that they won't fail with docs disabled

* Fri Dec  1 2006 Jindrich Novy <jnovy@redhat.com> - 1.11.22-7
- remove/replace obsolete rpm tags, fix rpmlint errors

* Sat Oct 28 2006 Jindrich Novy <jnovy@redhat.com> - 1.11.22-6
- respect explicit port specification in CVS_PROXY (#212418)

* Wed Oct 25 2006 Jindrich Novy <jnovy@redhat.com> - 1.11.22-5
- spec cleanup
- use dist, SOURCE0 now points to correct upstream URL

* Thu Jul 28 2006 Martin Stransky <stransky@redhat.com> - 1.11.22-4
- added ipv6 patch (#199404)

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 1.11.22-3.1
- rebuild

* Wed Jun 28 2006 Maros Barabas <mbarabas@redhat.com> - 1.11.22-3
- fix for #196848 - double free coruption

* Thu Jun 22 2006 Martin Stransky <stransky@redhat.com> - 1.11.22-2
- added LFS support (#196259)

* Mon Jun 12 2006 Martin Stransky <stransky@redhat.com> - 1.11.22-1
- new upstream

* Tue May 9  2006 Martin Stransky <stransky@redhat.com> - 1.11.21-4
- fix for #189858 - /etc/profile.d/cvs.sh overwrite personal settings
- fix for #190009 - rcs2log uses obsolete sort option

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 1.11.21-3.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 1.11.21-3.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Wed Dec 21 2005 Martin Stransky <stransky@redhat.com> 1.11.21-3
- fix for #150031 - cvs diff -kk -u fails

* Wed Dec 14 2005 Martin Stransky <stransky@redhat.com> 1.11.21-2
- fix for cvs diff with two -r switches (#18161)
- pam patch (#48937)
- CVS_RSH is set to ssh (#58699)

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Thu Nov 10 2005 Martin Stransky <stransky@redhat.com> 1.11.21-1
- new upstream

* Thu Aug 23 2005 Martin Stransky <stransky@redhat.com> 1.11.19-10
- fix for #166366 - CVS temporary file issue

* Thu Jul 21 2005 Martin Stransky <stransky@redhat.com> 1.11.19-9
- add vim-minimal to Requires (#163030)

* Mon Apr 18 2005 Martin Stransky <stransky@redhat.com> 1.11.19-8
- add security fix CAN-2005-0753 (Derek Price)

* Thu Mar 17 2005 Martin Stransky <stransky@redhat.com> 1.11.19-7
- fix NULL pointer comparsion (#63365)

* Mon Mar 14 2005 Martin Stransky <stransky@redhat.com> 1.11.19-6
- add '/' to invalid RCS tag characters (#56162)

* Wed Mar 9  2005 Martin Stransky <stransky@redhat.com> 1.11.19-5
- fix newline issue in log (#64182)

* Mon Mar 7  2005 Martin Stransky <stransky@redhat.com> 1.11.19-4
- remove check of HTTP_PROXY variable (#150434)

* Thu Mar 3  2005 Martin Stransky <stransky@redhat.com> 1.11.19-3
- add xinetd config file (#136929)
- add proxy-support patch (#144297)

* Mon Feb 28 2005 Martin Stransky <stransky@redhat.com> 1.11.19-2
- add opt flags

* Mon Feb 28 2005 Martin Stransky <stransky@redhat.com> 1.11.19-1
- update to 1.11.19

* Mon Feb 14 2005 Adrian Havill <havill@redhat.com>
- rebuilt

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu Jun 10 2004 Nalin Dahyabhai <nalin@redhat.com> 1.11.17-2
- rebuild

* Thu Jun 10 2004 Nalin Dahyabhai <nalin@redhat.com> 1.11.17-1
- update to 1.11.17, which includes those last few fixes

* Fri May 28 2004 Nalin Dahyabhai <nalin@redhat.com>
- add security fix for CAN-2004-0416,CAN-2004-0417,CAN-2004-0418 (Stefan Esser)

* Fri May 28 2004 Robert Scheck 1.11.16-0
- update to 1.11.16 (#124239)

* Tue May 18 2004 Nalin Dahyabhai <nalin@redhat.com> 1.11.15-6
- rebuild

* Thu May 13 2004 Nalin Dahyabhai <nalin@redhat.com> 1.11.15-5
- use revised version of Stefan Esser's patch provided by Derek Robert Price

* Mon May  3 2004 Nalin Dahyabhai <nalin@redhat.com> 1.11.15-4
- rebuild

* Mon May  3 2004 Nalin Dahyabhai <nalin@redhat.com> 1.11.15-3
- add patch from Stefan Esser to close CAN-2004-0396

* Wed Apr 21 2004 Nalin Dahyabhai <nalin@redhat.com> 1.11.15-2
- rebuild

* Wed Apr 21 2004 Nalin Dahyabhai <nalin@redhat.com> 1.11.15-1
- update to 1.11.15, fixing CAN-2004-0180 (#120969)

* Tue Mar 23 2004 Nalin Dahyabhai <nalin@redhat.com> 1.11.14-1
- update to 1.11.14

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Jan  7 2004 Nalin Dahyabhai <nalin@redhat.com> 1.11.11-1
- turn kserver, which people shouldn't use any more, back on

* Tue Dec 30 2003 Nalin Dahyabhai <nalin@redhat.com>
- update to 1.11.11

* Thu Dec 18 2003 Nalin Dahyabhai <nalin@redhat.com> 1.11.10-1
- update to 1.11.10

* Mon Jul 21 2003 Nalin Dahyabhai <nalin@redhat.com> 1.11.5-3
- rebuild

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Apr 30 2003 Nalin Dahyabhai <nalin@redhat.com> 1.11.5-1
- update to 1.11.5
- disable kerberos 4 support

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Tue Jan 21 2003 Nalin Dahyabhai <nalin@redhat.com> 1.11.2-9
- rebuild

* Thu Jan 16 2003 Nalin Dahyabhai <nalin@redhat.com> 1.11.2-8
- incorporate fix for double-free in server (CAN-2003-0015)

* Tue Nov 26 2002 Nalin Dahyabhai <nalin@redhat.com> 1.11.2-7
- don't error out in %%install if the info dir file we remove from the build
  root isn't there (depends on the version of texinfo installed, reported by
  Arnd Bergmann)

* Fri Oct  4 2002 Nalin Dahyabhai <nalin@redhat.com> 1.11.2-6
- fixup LDFLAGS to find multilib Kerberos for linking

* Thu Sep 24 2002 Nalin Dahyabhai <nalin@redhat.com>
- incorporate patch to add 't' as a loginfo format specifier, from NetBSD

* Thu Jul 18 2002 Tim Waugh <twaugh@redhat.com 1.11.2-5
- Fix mktemp patch (bug #66669)
- Incorporate patch to fix verifymsg behaviour on empty logs (bug #66022)

* Fri Jun 21 2002 Tim Powers <timp@redhat.com> 1.11.2-4
- automated rebuild

* Tue Jun  4 2002 Nalin Dahyabhai <nalin@redhat.com> 1.11.2-3
- incorporate patch to fix incorrect socket descriptor usage (#65225)
- incorporate patches to not choke on empty commit messages and to always
  send them (#66017)
- incorporate patch to not infinitely recurse on assertion failures (#66019)

* Sun May 26 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu May  9 2002 Nalin Dahyabhai <nalin@redhat.com> 1.11.2-1
- update to 1.11.2

* Mon Feb 18 2002 Nalin Dahyabhai <nalin@redhat.com> 1.11.1p1-7
- build with an external zlib
- don't run automake in the %%build phase

* Tue Jan 15 2002 Nalin Dahyabhai <nalin@redhat.com> 1.11.1p1-6
- merge patch to handle timestamping of symlinks in the repository properly,
  from dwmw2 (#23333)

* Wed Jan 09 2002 Tim Powers <timp@redhat.com> 1.11.1p1-5
- automated rebuild

* Tue Nov 13 2001 Nalin Dahyabhai <nalin@redhat.com> 1.11.1p1-4
- remove explicit dependency on krb5-libs

* Tue Jul 31 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.11.1p1-3
- Fix up initial cvs login (#47457)
- Bring back the leading newline at the beginning of commit messages
  "a" is one key less than "O". ;)
- Fix build in the current build system

* Mon Jun 25 2001 Bill Nottingham <notting@redhat.com>
- don't own /usr/share/info/dir

* Fri Jun 22 2001 Nalin Dahyabhai <nalin@redhat.com>
- fix the files list

* Mon Jun 18 2001 Nalin Dahyabhai <nalin@redhat.com>
- update to 1.11.1p1
- drop no-longer-necessary patches
- use bundled zlib, because it's apparently not the same as the system zlib
- run the test suite in the build phase
- drop explicit Requires: on perl (RPM will catch the interpreter req)

* Mon Jan 29 2001 Nalin Dahyabhai <nalin@redhat.com>
- fix cvs-1.11-security.patch, which had CR-LF line terminators (#25090)
- check for and ignore ENOENT errors when attempting to remove symlinks (#25173)

* Mon Jan 08 2001 Preston Brown <pbrown@redhat.com>
- patch from Olaf Kirch <okir@lst.de> to do tmp files safely.

* Tue Oct 10 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- 1.11

* Wed Jul 12 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Mon Jul 10 2000 Nalin Dahyabhai <nalin@redhat.com>
- always zero errno before calling readdir (#10374)

* Tue Jun 27 2000 Nalin Dahyabhai <nalin@redhat.com>
- rebuild in new build environment (release 6)

* Mon Jun  5 2000 Nalin Dahyabhai <nalin@redhat.com>
- rebuild in new build environment (release 5)
- FHS tweaks
- actually gzip the info pages

* Wed May 10 2000 Nalin Dahyabhai <nalin@redhat.com>
- reverse sense of conditional kerberos dependency
- add kerberos IV patch from Ken Raeburn
- switch to using the system's zlib instead of built-in
- default to unstripped binaries

* Tue Apr  4 2000 Bill Nottingham <notting@redhat.com>
- eliminate explicit krb5-configs dependency

* Mon Mar 20 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- 1.10.8

* Wed Mar  1 2000 Nalin Dahyabhai <nalin@redhat.com>
- make kerberos support conditional at build-time

* Wed Mar  1 2000 Bill Nottingham <notting@redhat.com>
- integrate kerberos support into main tree

* Mon Feb 14 2000 Nalin Dahyabhai <nalin@redhat.com>
- build with gssapi auth (--with-gssapi, --with-encryption)
- apply patch to update libs to krb5 1.1.1

* Fri Feb 04 2000 Cristian Gafton <gafton@redhat.com>
- fix the damn info pages too while we're at it.
- fix description
- man pages are compressed
- make sure %%post and %%preun work okay

* Sun Jan 9 2000  Jim Kingdon <http://bugzilla.redhat.com/bugzilla>
- update to 1.10.7.

* Wed Jul 14 1999 Jim Kingdon <http://developer.redhat.com>
- add the patch to make 1.10.6 usable
  (http://www.cyclic.com/cvs/dev-known.html).

* Tue Jun  1 1999 Jeff Johnson <jbj@redhat.com>
- update to 1.10.6.

* Sun Mar 21 1999 Cristian Gafton <gafton@redhat.com> 
- auto rebuild in the new build environment (release 2)

* Mon Feb 22 1999 Jeff Johnson <jbj@redhat.com>
- updated text in spec file.

* Mon Feb 22 1999 Jeff Johnson <jbj@redhat.com>
- update to 1.10.5.

* Tue Feb  2 1999 Jeff Johnson <jbj@redhat.com>
- update to 1.10.4.

* Tue Oct 20 1998 Jeff Johnson <jbj@redhat.com>
- update to 1.10.3.

* Mon Sep 28 1998 Jeff Johnson <jbj@redhat.com>
- update to 1.10.2.

* Wed Sep 23 1998 Jeff Johnson <jbj@redhat.com>
- remove trailing characters from rcs2log mktemp args

* Thu Sep 10 1998 Jeff Johnson <jbj@redhat.com>
- update to 1.10.1

* Mon Aug 31 1998 Jeff Johnson <jbj@redhat.com>
- fix race conditions in cvsbug/rcs2log

* Sun Aug 16 1998 Jeff Johnson <jbj@redhat.com>
- update to 1.10.

* Wed Aug 12 1998 Jeff Johnson <jbj@redhat.com>
- update to 1.9.30.

* Mon Jun 08 1998 Prospector System <bugs@redhat.com>
- translations modified for de, fr

* Mon Jun  8 1998 Jeff Johnson <jbj@redhat.com>
- build root
- update to 1.9.28

* Mon Apr 27 1998 Prospector System <bugs@redhat.com>
- translations modified for de, fr, tr

* Wed Oct 29 1997 Otto Hammersmith <otto@redhat.com>
- added install-info stuff
- added changelog section
