#!python3
"""
by Ed Mitchell, and Carson Miller
Windows local forensic collector (single combined text report).
Requires: Python 3.x (only stdlib). Run as Administrator.
Outputs: report-YYYYMMDD-HHMMSS.txt and artifacts/ folder for temporary copies.
"""

import os
import sys
import subprocess
import hashlib
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
import tempfile

OUTDIR = Path.cwd() / f"forensic_collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
REPORT = OUTDIR / "report.txt"
ARTIFACTS = OUTDIR / "artifacts"

# Ensure dirs
OUTDIR.mkdir(parents=True, exist_ok=True)
ARTIFACTS.mkdir(parents=True, exist_ok=True)

def run(cmd, shell=False, capture=True):
    try:
        if isinstance(cmd, list):
            proc = subprocess.run(cmd, capture_output=capture, text=True, shell=shell)
        else:
            proc = subprocess.run(cmd, capture_output=capture, text=True, shell=True)
        return proc.stdout if proc.stdout is not None else ""
    except Exception as e:
        return f"ERROR running {cmd}: {e}\n"

def safe_hash(path):
    try:
        with open(path, "rb") as f:
            h = hashlib.sha256()
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        return f"ERROR_HASH: {e}"

def write_section(title, content):
    with open(REPORT, "a", encoding="utf-8", errors="replace") as f:
        f.write("#" * 80 + "\n")
        f.write(f"{title}\n")
        f.write("#" * 80 + "\n")
        f.write(content + "\n\n")

def gather_system_info():
    parts = []
    parts.append("=== systeminfo ===")
    parts.append(run("systeminfo"))
    parts.append("\n=== wmic bios ===")
    parts.append(run('wmic bios get Manufacturer,Name,SMBIOSBIOSVersion,SerialNumber,ReleaseDate /format:list'))
    parts.append("\n=== wmic baseboard ===")
    parts.append(run('wmic baseboard get Manufacturer,Product,SerialNumber,Version /format:list'))
    parts.append("\n=== CPU (wmic cpu) ===")
    parts.append(run('wmic cpu get Name,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed /format:list'))
    parts.append("\n=== Memory (wmic computersystem) ===")
    parts.append(run('wmic computersystem get TotalPhysicalMemory,Model /format:list'))
    return "\n".join(parts)

def gather_processes():
    out = []
    out.append("Getting process list (wmic). For each process, will try to compute SHA256 of executable if path present.\n")
    wmic = run('wmic process get ProcessId,ExecutablePath,ParentProcessId,CommandLine /format:csv')
    out.append(wmic)
    # parse process lines to compute hashes
    for line in wmic.splitlines():
        if "," not in line:
            continue
        # CSV form: Node,CommandLine,ExecutablePath,ParentProcessId,ProcessId
        cols = line.split(",")
        if len(cols) < 5:
            continue
        node, cmdline, exe, ppid, pid = cols[0], cols[1], cols[2], cols[3], cols[4]
        exe = exe.strip()
        if exe and os.path.isfile(exe):
            h = safe_hash(exe)
            out.append(f"PID {pid} EXEC {exe} SHA256: {h}")
    return "\n".join(out)

def gather_drivers_services():
    out = []
    out.append("=== driverquery /v ===")
    out.append(run("driverquery /v"))
    out.append("\n=== wmic service ===")
    out.append(run('wmic service get Name,DisplayName,State,StartMode,PathName /format:csv'))
    return "\n".join(out)

def gather_users_logons():
    out = []
    out.append("=== local users (net user) ===")
    out.append(run("net user"))
    out.append("\n=== wmic useraccount ===")
    out.append(run('wmic useraccount get Name,SID,Disabled,Lockout /format:csv'))
    out.append("\n=== Recent Security log events (4624 logon, 4634 logoff) via PowerShell (last 200) ===")
    ps = r"Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4624,4634} -MaxEvents 200 | Select TimeCreated,Id,@{n='Account';e={$_.Properties[5].Value}} | Format-Table -AutoSize"
    out.append(run(['powershell', '-NoProfile', '-Command', ps]))
    return "\n".join(out)

def gather_browser_artifacts():
    out = []
    # Chrome/Edge (Chromium) history paths
    local = os.environ.get("LOCALAPPDATA", r"C:\Users\Default\AppData\Local")
    userprof = os.environ.get("USERPROFILE", r"C:\Users\Default")
    chrome_hist = Path(local) / r"Google\Chrome\User Data\Default\History"
    edge_hist = Path(local) / r"Microsoft\Edge\User Data\Default\History"
    firefox_profile_base = Path(userprof) / r"AppData\Roaming\Mozilla\Firefox\Profiles"

    def try_sqlite_copy_and_query(src_path, label):
        if not src_path.exists():
            return f"{label}: not found ({src_path})"
        try:
            cp = ARTIFACTS / f"{label}_History_copy"
            shutil.copy2(str(src_path), str(cp))
            # attempt to query last 25 urls if it's chrome-like sqlite
            con = sqlite3.connect(str(cp))
            cur = con.cursor()
            results = []
            # Chrome/Edge schema: urls table
            try:
                cur.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 25")
                for r in cur.fetchall():
                    results.append(f"{r[0]} | {r[1]} | {r[2]}")
            except Exception:
                results.append("Could not query 'urls' table (schema mismatch).")
            con.close()
            return f"{label}: copied to {cp}\nSample recent visits:\n" + "\n".join(results)
        except Exception as e:
            return f"{label}: ERROR copying or reading file: {e}"

    out.append(try_sqlite_copy_and_query(chrome_hist, "Chrome"))
    out.append(try_sqlite_copy_and_query(edge_hist, "Edge"))
    # Firefox: find profile folder and places.sqlite
    if firefox_profile_base.exists():
        for p in firefox_profile_base.iterdir():
            if p.is_dir():
                ff_places = p / "places.sqlite"
                out.append(try_sqlite_copy_and_query(ff_places, f"Firefox_{p.name}"))
    else:
        out.append(f"Firefox profiles folder not found: {firefox_profile_base}")
    out.append("\nNote: saved logins/cookies may be locked or encrypted; this script attempts to copy sqlite dbs for safe read.")
    return "\n".join(out)

def gather_network():
    out = []
    out.append("=== netstat -ano ===")
    out.append(run("netstat -ano"))
    out.append("\n=== route print ===")
    out.append(run("route print"))
    out.append("\n=== arp -a ===")
    out.append(run("arp -a"))
    out.append("\n=== ipconfig /displaydns ===")
    out.append(run("ipconfig /displaydns"))
    return "\n".join(out)

def gather_listening_ports():
    # netstat -abn needs admin; -b shows executable
    out = []
    out.append("=== netstat -abn (may require Admin) ===")
    out.append(run("netstat -abn"))
    return "\n".join(out)

def main():
    header = f"Windows Forensic Collection Report\nGenerated: {datetime.now().isoformat()}\nHost: {os.environ.get('COMPUTERNAME','Unknown')}\nUser: {os.environ.get('USERNAME','Unknown')}\n"
    with open(REPORT, "w", encoding="utf-8", errors="replace") as f:
        f.write(header + "\n")

    try:
        write_section("SYSTEM INFORMATION", gather_system_info())
        write_section("RUNNING PROCESSES & HASHES", gather_processes())
        write_section("DRIVERS AND SERVICES", gather_drivers_services())
        write_section("USER ACCOUNTS AND LOGON/LOGOFF", gather_users_logons())
        write_section("BROWSER ARTIFACTS (sample recent history if readable)", gather_browser_artifacts())
        write_section("NETWORK (connections, routing, ARP, DNS cache)", gather_network())
        write_section("LISTENING PORTS", gather_listening_ports())
        # final note
        write_section("NOTES", "Artifacts folder: {}\nRun as Admin for full detail. Some files (browser, system) may be locked; they were copied where possible.".format(ARTIFACTS))
        print(f"Collection complete. Report: {REPORT}\nArtifacts folder: {ARTIFACTS}")
    except Exception as e:
        print("ERROR during collection:", e)
        sys.exit(2)

if __name__ == "__main__":
    main()

