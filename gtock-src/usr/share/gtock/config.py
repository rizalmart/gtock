# config.py - build time configuration
# Copyright (C) 2004, 2005  Philip Van Hoof <me at pvanhoof dot be>
# Copyright (C) 2004 - 2009 Gaute Hope <eg at gaute dot vetsj dot com>
# Copyright (C) 2004, 2005  Kristof Vansant <de_lupus at pandora dot be>
#
# Ported to PyObject and Python3 by rizalmart
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import os
import shlex
import shutil
import subprocess
import sys

#################

gtk_version="3.0"

app_version = "3.1.0"

dconf_path= "org.gtk.gtock"

#################

# Resolve resources relative to this module instead of assuming /usr. This
# supports /usr, /usr/local, custom prefixes and DESTDIR-based package builds.
gs_dir = os.path.dirname(os.path.realpath(__file__))
image_dir = os.path.join(gs_dir, "pixmaps")
glade_dir = os.path.join(gs_dir, "assets")
xwrapper_path = os.path.join(gs_dir, "xwrapper.py")
xwrapper_exec = "{} {}".format(shlex.quote(sys.executable), shlex.quote(xwrapper_path))
locale_dir = os.environ.get(
    "GTOCK_LOCALEDIR",
    os.path.join(os.path.dirname(gs_dir), "locale")
)
crontabbin = None
anacronbin = None
cron_backend = None
atbin = shutil.which("at") or "/usr/bin/at"
atqbin = shutil.which("atq") or "/usr/bin/atq"
atrmbin = shutil.which("atrm") or "/usr/bin/atrm"
batchbin = shutil.which("batch") or "/usr/bin/batch"
subin = shutil.which("su") or "/bin/su"
prefix = os.path.dirname(os.path.dirname(gs_dir))




def getDconfPath():
	return dconf_path

def getGtkVersion():
	return gtk_version

def getConfigDir():
	return os.environ['HOME'] + "/.config/gtock"

def getPrefix():
	return prefix

def getSubin ():
	return subin

def getAtbin ():
	return atbin

def getAtrmbin ():
	return atrmbin

def getAtqbin ():
	return atqbin

def getBatchbin ():
	return batchbin

def getCrontabbin ():
    """Return the selected crontab executable (legacy API)."""
    command = getCrontabCommand()
    return command[0] if command else None


def _package_owner(path):
    """Best-effort package identification; never required for operation."""
    if not path:
        return None
    path = os.path.realpath(path)
    checks = (
        (["dpkg-query", "-S", path], ("cronie", "cron", "fcron", "dcron", "busybox")),
        (["rpm", "-qf", path], ("cronie", "cron", "fcron", "dcron", "busybox")),
        (["apk", "info", "--who-owns", path], ("cronie", "cron", "fcron", "dcron", "busybox")),
    )
    for command, names in checks:
        if not shutil.which(command[0]):
            continue
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=3)
            value = (result.stdout + result.stderr).lower()
            import re
            for name in names:
                # Match package-name tokens, not substrings: otherwise
                # "dcron" and "fcron" would incorrectly match "cron".
                if re.search(r"(?:^|[^a-z0-9])" + re.escape(name) +
                             r"(?:[-.:]|$)", value):
                    if name == "cron":
                        return "cronie"
                    return name
        except (OSError, subprocess.SubprocessError):
            pass
    return None


def _is_busybox_binary(path):
    if not path:
        return False
    if os.path.basename(os.path.realpath(path)) == "busybox":
        return True
    try:
        result = subprocess.run([path, "--help"], capture_output=True,
                                text=True, timeout=3)
        return "BusyBox v" in (result.stdout + result.stderr)
    except (OSError, subprocess.SubprocessError):
        return False


def _busybox_has(applet):
    busybox = shutil.which("busybox")
    if not busybox:
        return False
    try:
        result = subprocess.run([busybox, "--list"], capture_output=True,
                                text=True, timeout=3)
        return result.returncode == 0 and applet in result.stdout.split()
    except (OSError, subprocess.SubprocessError):
        return False


_CRON_BACKEND_PRIORITY = ("cronie", "fcron", "dcron", "busybox")


def _backend_from_executable(path, process_name=None):
    """Classify a cron executable using its real binary and package owner."""
    if not path:
        return None
    real_path = os.path.realpath(path)
    basename = os.path.basename(real_path).lower()
    process_name = (process_name or "").lower()

    if basename == "fcron" or basename == "fcrontab" or process_name == "fcron":
        return "fcron"
    if _is_busybox_binary(path):
        return "busybox"

    owner = _package_owner(real_path)
    if owner in _CRON_BACKEND_PRIORITY:
        return owner

    # The Debian/Ubuntu cron package is the Vixie/Cronie-compatible daemon.
    if basename in ("cron", "crond") and owner == "cronie":
        return "cronie"
    return None


def _running_cron_backends():
    """Return implementations whose daemon processes are currently running."""
    found = set()
    proc = "/proc"
    try:
        entries = os.scandir(proc)
    except OSError:
        return found

    with entries:
        for entry in entries:
            if not entry.name.isdigit():
                continue
            base = os.path.join(proc, entry.name)
            try:
                with open(os.path.join(base, "comm"), encoding="utf-8") as stream:
                    comm = stream.read().strip().lower()
                if comm not in ("cron", "crond", "fcron"):
                    continue
                executable = os.path.realpath(os.path.join(base, "exe"))
                backend = _backend_from_executable(executable, comm)
                if backend:
                    found.add(backend)
            except (OSError, PermissionError):
                continue
    return found


def _installed_cron_backends():
    """Return cron implementations discoverable from installed executables."""
    found = set()

    fcrontab = shutil.which("fcrontab")
    fcron_daemon = shutil.which("fcron")
    if fcrontab or fcron_daemon:
        found.add("fcron")

    # Inspect conventional daemon names and the generic crontab command.
    for name in ("cron", "crond", "crontab"):
        path = shutil.which(name)
        if not path:
            continue
        backend = _backend_from_executable(path, name)
        if backend:
            found.add(backend)

    busybox = shutil.which("busybox")
    if busybox and _busybox_has("crond") and _busybox_has("crontab"):
        found.add("busybox")

    # If a generic crontab exists but no package/daemon evidence identifies
    # its implementation, retain compatibility with traditional cron.
    if shutil.which("crontab") and not found:
        found.add("cronie")
    return found


def getCronBackend():
    """Choose a backend: explicit override, running daemon, then installed.

    Automatic selection follows the requested priority: Cronie, fcron,
    dcron, then BusyBox cron. A running implementation takes precedence over
    an implementation that is merely installed.
    """
    global cron_backend
    override = os.environ.get("GTOCK_CRON_BACKEND", "").strip().lower()
    if override:
        if override in ("cronie", "dcron", "busybox", "fcron", "cronie-compatible"):
            cron_backend = override
            return cron_backend
        # Ignore an invalid override and continue with automatic detection.

    # Detection is performed once per application process. An explicit
    # environment override above always takes precedence over the cached value.
    if cron_backend:
        return cron_backend

    # Apply one deterministic priority order to everything discovered.
    # Running daemons and installed executables both count as evidence.
    detected = _running_cron_backends() | _installed_cron_backends()
    for backend in _CRON_BACKEND_PRIORITY:
        if backend in detected:
            cron_backend = backend
            return cron_backend

    cron_backend = None
    return None

def getCrontabCommand():
    """Return argv prefix for crontab operations (safe for subprocess)."""
    backend = getCronBackend()
    if backend == "fcron":
        executable = shutil.which("fcrontab")
        return [executable] if executable else None
    executable = shutil.which("crontab")
    if executable:
        return [executable]
    if backend == "busybox":
        busybox = shutil.which("busybox")
        return [busybox, "crontab"] if busybox else None
    return None


def getCronDaemon():
    """Return the detected daemon executable, if present."""
    for name in ("crond", "cron", "fcron"):
        path = shutil.which(name)
        if path:
            return path
    busybox = shutil.which("busybox")
    if busybox and _busybox_has("crond"):
        return [busybox, "crond"]
    return None


def getAnacronbin():
    return shutil.which("anacron")


def anacronInstalled():
    if getAnacronbin() is not None:
      return True
    else:
      return False

def getVersion ():
	return app_version

def getImagedir ():
	return image_dir

def getGladedir ():
	return glade_dir

def GETTEXT_PACKAGE():
	return "gtock"

def GNOMELOCALEDIR():
	return locale_dir
	
def atInstalled():
	return os.path.exists(atbin)
	
def cronTabInstalled():
	return getCrontabCommand() is not None
