# anacron.py - Anacron table management for gTock
# Copyright (C) 2026 gTock contributors
# SPDX-License-Identifier: GPL-2.0-or-later

"""Safe, comment-preserving access to anacrontab files.

Anacron is deliberately kept separate from :mod:`crontab`: its records use
period/delay/job-id/command rather than the five-field cron expression.
The class provides a small API for a GTK editor or other frontend to use.
"""

import os
import re
import shutil
import subprocess
import tempfile


JOB_RE = re.compile(r"^\s*(\S+)\s+(\d+)\s+(\S+)\s+(.+?)\s*$")
VALID_PERIOD = re.compile(r"^(?:[1-9][0-9]*|@monthly)$")


class Anacron:
    def __init__(self, table="/etc/anacrontab", executable=None):
        self.table = table
        self.executable = executable or shutil.which("anacron")
        self.lines = []

    def get_type(self):
        return "anacron"

    def available(self):
        return bool(self.executable and os.path.isfile(self.table))

    @staticmethod
    def parse_job(line, linenumber=None):
        """Return a job dictionary, or None for comments/environment lines."""
        match = JOB_RE.match(line)
        if not match or line.lstrip().startswith("#"):
            return None
        period, delay, identifier, command = match.groups()
        if not VALID_PERIOD.match(period):
            return None
        return {
            "period": period,
            "delay": int(delay),
            "identifier": identifier,
            "command": command,
            "linenumber": linenumber,
            "raw": line,
        }

    def read(self):
        with open(self.table, "r", encoding="utf-8", errors="surrogateescape") as stream:
            self.lines = stream.readlines()
        jobs = []
        for index, line in enumerate(self.lines):
            job = self.parse_job(line, index)
            if job is not None:
                jobs.append(job)
        return jobs

    @staticmethod
    def _format_job(period, delay, identifier, command):
        period = str(period).strip()
        identifier = str(identifier).strip()
        command = str(command).strip()
        if not VALID_PERIOD.fullmatch(period):
            raise ValueError("Period must be a positive number of days or @monthly")
        if not str(delay).isdigit() or int(delay) < 0:
            raise ValueError("Delay must be a non-negative number of minutes")
        if not identifier or any(char.isspace() for char in identifier):
            raise ValueError("Job identifier must be a non-empty single word")
        if not command or "\n" in command or "\r" in command:
            raise ValueError("Command must be a non-empty single line")
        return f"{period}\t{int(delay)}\t{identifier}\t{command}\n"

    def validate(self, lines=None):
        """Validate a candidate table with the installed Anacron parser."""
        if not self.executable:
            raise RuntimeError("anacron executable was not found")
        candidate = list(self.lines if lines is None else lines)
        directory = os.path.dirname(os.path.abspath(self.table))
        fd, path = tempfile.mkstemp(prefix=".gtock-anacron-", dir=directory, text=True)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", errors="surrogateescape") as stream:
                stream.writelines(candidate)
            result = subprocess.run(
                [self.executable, "-T", "-t", path],
                capture_output=True, text=True, check=False,
            )
            if result.returncode != 0:
                raise ValueError((result.stderr or result.stdout or "Invalid anacrontab").strip())
            return True
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass

    def _install(self, lines):
        """Validate then atomically replace the table, retaining its metadata."""
        if not os.geteuid() == 0 and os.path.abspath(self.table).startswith("/etc/"):
            raise PermissionError("Root privileges are required to modify /etc/anacrontab")
        self.validate(lines)
        directory = os.path.dirname(os.path.abspath(self.table))
        old_stat = os.stat(self.table)
        fd, path = tempfile.mkstemp(prefix=".gtock-anacron-", dir=directory, text=True)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", errors="surrogateescape") as stream:
                stream.writelines(lines)
                stream.flush()
                os.fsync(stream.fileno())
            os.chmod(path, old_stat.st_mode & 0o7777)
            os.chown(path, old_stat.st_uid, old_stat.st_gid)
            os.replace(path, self.table)
            self.lines = list(lines)
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass

    def add(self, period, delay, identifier, command):
        lines = list(self.lines if self.lines else self._read_lines())
        if any((job := self.parse_job(line)) and job["identifier"] == str(identifier)
               for line in lines):
            raise ValueError("Anacron job identifier already exists")
        lines.append(self._format_job(period, delay, identifier, command))
        self._install(lines)
        return self.read()

    def update(self, linenumber, period, delay, identifier, command):
        lines = list(self.lines if self.lines else self._read_lines())
        if linenumber < 0 or linenumber >= len(lines):
            raise IndexError("Anacron line number is out of range")
        for index, line in enumerate(lines):
            job = self.parse_job(line)
            if job and job["identifier"] == str(identifier) and index != linenumber:
                raise ValueError("Anacron job identifier already exists")
        if self.parse_job(lines[linenumber]) is None:
            raise ValueError("Selected line is not an Anacron job")
        lines[linenumber] = self._format_job(period, delay, identifier, command)
        self._install(lines)
        return self.read()

    def delete(self, linenumber):
        lines = list(self.lines if self.lines else self._read_lines())
        if linenumber < 0 or linenumber >= len(lines) or self.parse_job(lines[linenumber]) is None:
            raise ValueError("Selected line is not an Anacron job")
        del lines[linenumber]
        self._install(lines)
        return self.read()

    def _read_lines(self):
        with open(self.table, "r", encoding="utf-8", errors="surrogateescape") as stream:
            return stream.readlines()
