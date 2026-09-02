```python
#!/usr/bin/env python3

"""
PyOS 2.0
========

A completely fake operating system written in Python.

Features:
    - Virtual filesystem
    - Persistent virtual disk
    - Multiple users
    - File permissions
    - chmod / chown
    - Fake package manager
    - Fake processes
    - ps / kill / top
    - Fake networking
    - ping / ifconfig
    - CPU / RAM simulation
    - Environment variables
    - Pipes
    - > and >> redirection
    - Command history
    - Tab completion
    - Built-in text editor
    - Built-in Python interpreter
    - neofetch
    - reboot / shutdown

The only real file PyOS touches is:
    pyos_disk.json

Everything else exists inside the simulation.
"""

import os
import sys
import json
import shlex
import time
import random
import platform
from datetime import datetime


DISK_FILE = "pyos_disk.json"


# ============================================================
# FILESYSTEM OBJECTS
# ============================================================

class File:
    def __init__(
        self,
        name,
        content="",
        owner="user",
        group="users",
        permissions="rw-r--r--",
    ):
        self.name = name
        self.content = content
        self.owner = owner
        self.group = group
        self.permissions = permissions

    def to_dict(self):
        return {
            "type": "file",
            "name": self.name,
            "content": self.content,
            "owner": self.owner,
            "group": self.group,
            "permissions": self.permissions,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["name"],
            data.get("content", ""),
            data.get("owner", "user"),
            data.get("group", "users"),
            data.get("permissions", "rw-r--r--"),
        )


class Directory:
    def __init__(
        self,
        name,
        parent=None,
        owner="root",
        group="root",
        permissions="rwxr-xr-x",
    ):
        self.name = name
        self.parent = parent
        self.children = {}
        self.owner = owner
        self.group = group
        self.permissions = permissions

    def add(self, item):
        self.children[item.name] = item

    def get(self, name):
        return self.children.get(name)

    def remove(self, name):
        if name in self.children:
            del self.children[name]

    def to_dict(self):
        return {
            "type": "directory",
            "name": self.name,
            "owner": self.owner,
            "group": self.group,
            "permissions": self.permissions,
            "children": [
                child.to_dict()
                for child in self.children.values()
            ],
        }

    @classmethod
    def from_dict(cls, data, parent=None):
        directory = cls(
            data["name"],
            parent,
            data.get("owner", "root"),
            data.get("group", "root"),
            data.get("permissions", "rwxr-xr-x"),
        )

        for child in data.get("children", []):
            if child["type"] == "file":
                item = File.from_dict(child)
            else:
                item = Directory.from_dict(child, directory)

            directory.add(item)

        return directory


# ============================================================
# PROCESS
# ============================================================

class Process:
    def __init__(self, pid, name, user, cpu=None, memory=None):
        self.pid = pid
        self.name = name
        self.user = user
        self.cpu = cpu if cpu is not None else random.uniform(0.1, 8.0)
        self.memory = memory if memory is not None else random.randint(2, 250)
        self.started = datetime.now()

    def update(self):
        self.cpu = max(0.0, self.cpu + random.uniform(-1.5, 1.5))
        self.cpu = min(self.cpu, 99.0)


# ============================================================
# USER
# ============================================================

class User:
    def __init__(self, username, password="", admin=False):
        self.username = username
        self.password = password
        self.admin = admin


# ============================================================
# PYOS
# ============================================================

class PyOS:

    def __init__(self):
        self.hostname = "pyos"
        self.version = "2.0"

        self.running = True
        self.next_pid = 100

        self.users = {
            "root": User("root", "toor", True),
            "user": User("user", "", False),
        }

        self.current_user = "user"

        self.environment = {
            "PATH": "/usr/bin:/bin",
            "HOME": "/home/user",
            "SHELL": "/bin/pysh",
            "USER": "user",
            "HOSTNAME": "pyos",
            "TERM": "pyterm",
        }

        self.history = []

        self.processes = []

        self.installed_packages = [
            "python",
            "pysh",
            "coreutils",
        ]

        self.total_ram = 4096
        self.used_ram = 0

        self.network_interfaces = {
            "lo": {
                "address": "127.0.0.1",
                "status": "UP",
            },
            "eth0": {
                "address": "192.168.1.42",
                "status": "UP",
            },
        }

        self.root = None
        self.current = None

        self.create_or_load_disk()

        self.spawn_process("init", "root", memory=25)
        self.spawn_process("pysh", self.current_user, memory=35)

    # ========================================================
    # DISK
    # ========================================================

    def create_or_load_disk(self):

        if os.path.exists(DISK_FILE):
            try:
                with open(DISK_FILE, "r", encoding="utf-8") as file:
                    data = json.load(file)

                self.root = Directory.from_dict(data)
                self.current = self.resolve("/home/user")

                if self.current is None:
                    raise ValueError("Invalid disk")

                return

            except Exception:
                print("⚠ Disk image corrupted.")
                print("Creating a new virtual disk...")

        self.create_filesystem()

    def save_disk(self):

        with open(DISK_FILE, "w", encoding="utf-8") as file:
            json.dump(
                self.root.to_dict(),
                file,
                indent=2,
            )

    def create_filesystem(self):

        self.root = Directory(
            "/",
            None,
            "root",
            "root",
            "rwxr-xr-x",
        )

        home = Directory(
            "home",
            self.root,
            "root",
            "root",
        )

        user_home = Directory(
            "user",
            home,
            "user",
            "users",
            "rwx------",
        )

        root_home = Directory(
            "root",
            home,
            "root",
            "root",
            "rwx------",
        )

        etc = Directory("etc", self.root)
        usr = Directory("usr", self.root)
        bin_dir = Directory("bin", usr)
        tmp = Directory("tmp", self.root)
        var = Directory("var", self.root)
        log = Directory("log", var)
        dev = Directory("dev", self.root)

        self.root.add(home)
        self.root.add(etc)
        self.root.add(usr)
        self.root.add(tmp)
        self.root.add(var)
        self.root.add(dev)

        home.add(user_home)
        home.add(root_home)

        usr.add(bin_dir)
        var.add(log)

        user_home.add(
            File(
                "welcome.txt",
                "Welcome to PyOS 2.0!\n"
                "\n"
                "This entire filesystem is fake.\n"
                "Your computer is safe. Probably.\n",
                "user",
                "users",
                "rw-r--r--",
            )
        )

        user_home.add(
            Directory(
                "Documents",
                user_home,
                "user",
                "users",
                "rwx------",
            )
        )

        user_home.add(
            Directory(
                "Downloads",
                user_home,
                "user",
                "users",
                "rwx------",
            )
        )

        etc.add(
            File(
                "os-release",
                'NAME="PyOS"\n'
                'VERSION="2.0"\n'
                'ID=pyos\n'
                'PRETTY_NAME="PyOS 2.0"\n',
                "root",
                "root",
                "rw-r--r--",
            )
        )

        etc.add(
            File(
                "hostname",
                "pyos\n",
                "root",
                "root",
            )
        )

        etc.add(
            File(
                "motd",
                "Welcome to PyOS.\n"
                "Please enjoy your completely imaginary operating system.\n",
                "root",
                "root",
            )
        )

        self.current = user_home

        self.save_disk()

    # ========================================================
    # PATHS
    # ========================================================

    def path_parts(self, path):

        if path.startswith("/"):
            parts = path.split("/")[1:]
        else:
            parts = path.split("/")

        return [
            part
            for part in parts
            if part not in ("", ".")
        ]

    def resolve(self, path):

        if not path:
            return self.current

        if path == "~":
            path = "/home/user"

        if path.startswith("~"):
            path = "/home/user" + path[1:]

        if path.startswith("/"):
            node = self.root
        else:
            node = self.current

        for part in self.path_parts(path):

            if part == "..":

                if node.parent is not None:
                    node = node.parent

                continue

            if not isinstance(node, Directory):
                return None

            node = node.get(part)

            if node is None:
                return None

        return node

    def get_path(self, node):

        if node == self.root:
            return "/"

        parts = []

        while node != self.root:
            parts.append(node.name)
            node = node.parent

        return "/" + "/".join(reversed(parts))

    # ========================================================
    # PERMISSIONS
    # ========================================================

    def is_admin(self):
        return self.users[self.current_user].admin

    def permission_index(self, node):

        if self.current_user == node.owner:
            return 0

        if node.group == "users":
            return 1

        return 2

    def can_read(self, node):

        if self.is_admin():
            return True

        index = self.permission_index(node)
        return node.permissions[index * 3] == "r"

    def can_write(self, node):

        if self.is_admin():
            return True

        index = self.permission_index(node)
        return node.permissions[index * 3 + 1] == "w"

    def can_execute(self, node):

        if self.is_admin():
            return True

        index = self.permission_index(node)
        return node.permissions[index * 3 + 2] == "x"

    # ========================================================
    # PROCESS MANAGEMENT
    # ========================================================

    def spawn_process(
        self,
        name,
        user,
        cpu=None,
        memory=None,
    ):

        process = Process(
            self.next_pid,
            name,
            user,
            cpu,
            memory,
        )

        self.next_pid += 1
        self.processes.append(process)

        self.used_ram += process.memory

        return process

    def find_process(self, pid):

        for process in self.processes:
            if process.pid == pid:
                return process

        return None

    def kill_process(self, pid):

        process = self.find_process(pid)

        if process is None:
            return False

        if (
            process.user != self.current_user
            and not self.is_admin()
        ):
            print("kill: permission denied")
            return False

        self.used_ram -= process.memory
        self.processes.remove(process)

        return True

    # ========================================================
    # BOOT
    # ========================================================

    def boot(self):

        print()
        print("╔══════════════════════════════════════╗")
        print("║              PyOS 2.0               ║")
        print("╚══════════════════════════════════════╝")
        print()

        messages = [
            "Loading PyOS kernel...",
            "Initializing virtual CPU...",
            "Initializing virtual memory...",
            "Mounting virtual filesystem...",
            "Starting networking...",
            "Starting userspace...",
            "Launching pysh...",
        ]

        for message in messages:
            time.sleep(0.08)
            print(f"[  OK  ] {message}")

        print()
        print("Welcome to PyOS.")
        print("Type 'help' for a list of commands.")
        print()

        self.read_motd()

    def read_motd(self):

        motd = self.resolve("/etc/motd")

        if motd and self.can_read(motd):
            print(motd.content)

    # ========================================================
    # PROMPT
    # ========================================================

    def prompt(self):

        path = self.get_path(self.current)

        if path == "/home/user":
            path = "~"

        symbol = "#" if self.is_admin() else "$"

        return (
            f"{self.current_user}"
            f"@{self.hostname}:"
            f"{path}{symbol} "
        )

    # ========================================================
    # MAIN LOOP
    # ========================================================

    def run(self):

        self.boot()

        while self.running:

            try:
                command = input(self.prompt())

                if not command.strip():
                    continue

                self.history.append(command)

                self.execute(command)

            except KeyboardInterrupt:
                print(
                    "\nUse 'exit' or 'shutdown' "
                    "to leave PyOS."
                )

            except EOFError:
                print()
                self.shutdown([])

    # ========================================================
    # COMMAND EXECUTION
    # ========================================================

    def execute(self, command_line, capture=False):

        command_line = command_line.strip()

        if not command_line:
            return ""

        # ----------------------------------------------------
        # Redirection
        # ----------------------------------------------------

        redirect_file = None
        append = False

        if ">>" in command_line:
            command_line, redirect_file = command_line.split(
                ">>",
                1,
            )
            append = True

        elif ">" in command_line:
            command_line, redirect_file = command_line.split(
                ">",
                1,
            )

        redirect_file = (
            redirect_file.strip()
            if redirect_file
            else None
        )

        # ----------------------------------------------------
        # Pipes
        # ----------------------------------------------------

        if "|" in command_line:

            commands = [
                part.strip()
                for part in command_line.split("|")
            ]

            output = ""

            for part in commands:
                output = self.execute(
                    part,
                    capture=True,
                )

                if output is None:
                    output = ""

                # Give the next command the previous
                # command's output through an environment variable.
                self.environment["PIPE_INPUT"] = output

            if redirect_file:
                self.write_redirect(
                    redirect_file,
                    output,
                    append,
                )
                return ""

            print(output, end="")
            return output

        try:
            args = shlex.split(command_line)
        except ValueError as error:
            print(f"parse error: {error}")
            return ""

        if not args:
            return ""

        command = args[0]
        arguments = args[1:]

        commands = {
            "help": self.help,
            "ls": self.ls,
            "pwd": self.pwd,
            "cd": self.cd,
            "mkdir": self.mkdir,
            "touch": self.touch,
            "cat": self.cat,
            "write": self.write,
            "rm": self.rm,
            "tree": self.tree,
            "clear": self.clear,
            "echo": self.echo,
            "whoami": self.whoami,
            "uname": self.uname,
            "date": self.date,
            "neofetch": self.neofetch,
            "history": self.history_cmd,
            "env": self.env,
            "export": self.export,
            "ps": self.ps,
            "top": self.top,
            "kill": self.kill,
            "chmod": self.chmod,
            "chown": self.chown,
            "id": self.id_cmd,
            "adduser": self.adduser,
            "su": self.su,
            "sudo": self.sudo,
            "apt": self.apt,
            "pkg": self.apt,
            "ping": self.ping,
            "ifconfig": self.ifconfig,
            "ip": self.ifconfig,
            "nano": self.nano,
            "python": self.python_shell,
            "py": self.python_shell,
            "reboot": self.reboot,
            "shutdown": self.shutdown,
            "exit": self.shutdown,
            "logout": self.logout,
        }

        function = commands.get(command)

        if function is None:

            if command in self.environment.get(
                "ALIASES",
                {}
            ):
                command = self.environment["ALIASES"][command]

            else:
                print(
                    f"pysh: command not found: {command}"
                )
                return ""

        result = function(arguments)

        if result is None:
            result = ""

        if redirect_file:
            self.write_redirect(
                redirect_file,
                str(result),
                append,
            )
            return str(result)

        if capture:
            return str(result)

        if result:
            print(result, end="")

        return str(result)
```python
    # ========================================================
    # REDIRECTION
    # ========================================================

    def write_redirect(
        self,
        filename,
        content,
        append=False,
    ):
        """Write command output into a virtual file."""

        target = self.resolve(filename)

        # Existing file
        if target is not None:

            if isinstance(target, Directory):
                print("redirect: target is a directory")
                return

            if not self.can_write(target):
                print("redirect: permission denied")
                return

            if append:
                target.content += content
            else:
                target.content = content

            self.save_disk()
            return

        # New file
        name = os.path.basename(filename)

        if "/" in filename:
            parent_path = os.path.dirname(filename)
            parent = self.resolve(parent_path)
        else:
            parent = self.current

        if parent is None:
            print("redirect: directory not found")
            return

        if not isinstance(parent, Directory):
            print("redirect: parent is not a directory")
            return

        if not self.can_write(parent):
            print("redirect: permission denied")
            return

        parent.add(
            File(
                name,
                content,
                self.current_user,
                "users",
                "rw-------",
            )
        )

        self.save_disk()

    # ========================================================
    # HELP
    # ========================================================

    def help(self, args):

        text = """
PyOS commands
=============

Filesystem:
    ls                  List files
    pwd                 Show current directory
    cd <dir>            Change directory
    mkdir <dir>         Create directory
    touch <file>        Create file
    cat <file>          Read file
    write <file> <txt>  Write file
    rm <file>           Delete file
    tree                Show filesystem tree
    nano <file>         Edit a file

Users:
    whoami              Current user
    id                  User information
    adduser <name>      Create user
    su <name>            Switch user
    sudo <command>      Run command as root

Permissions:
    chmod <perm> <file>
    chown <user> <file>

Processes:
    ps                  List processes
    top                 Process monitor
    kill <pid>          Kill process

Packages:
    apt update
    apt install <pkg>
    apt remove <pkg>
    apt list

Networking:
    ping <host>
    ifconfig

Shell:
    echo <text>
    env
    export NAME=value
    history
    clear

System:
    uname
    date
    neofetch
    python
    reboot
    shutdown
    exit

Shell features:
    command1 | command2
    command > file
    command >> file
"""

        return text

    # ========================================================
    # BASIC FILE COMMANDS
    # ========================================================

    def ls(self, args):

        target = self.current

        if args:
            target = self.resolve(args[0])

        if target is None:
            return "ls: no such file or directory\n"

        if isinstance(target, File):

            if not self.can_read(target):
                return "ls: permission denied\n"

            return target.name + "\n"

        lines = []

        for name, item in sorted(
            target.children.items()
        ):

            suffix = "/" if isinstance(
                item,
                Directory,
            ) else ""

            lines.append(name + suffix)

        return "\n".join(lines) + (
            "\n" if lines else ""
        )

    def pwd(self, args):
        return self.get_path(self.current) + "\n"

    def cd(self, args):

        if not args:
            target = self.resolve("/home/user")
        else:
            target = self.resolve(args[0])

        if target is None:
            return "cd: no such directory\n"

        if isinstance(target, File):
            return "cd: not a directory\n"

        if not self.can_execute(target):
            return "cd: permission denied\n"

        self.current = target

        return ""

    def mkdir(self, args):

        if not args:
            return "mkdir: missing operand\n"

        if not self.can_write(self.current):
            return "mkdir: permission denied\n"

        for name in args:

            if "/" in name:
                return (
                    "mkdir: only simple names "
                    "are supported\n"
                )

            if self.current.get(name):
                return (
                    f"mkdir: '{name}' already exists\n"
                )

            self.current.add(
                Directory(
                    name,
                    self.current,
                    self.current_user,
                    "users",
                    "rwx------",
                )
            )

        self.save_disk()

        return ""

    def touch(self, args):

        if not args:
            return "touch: missing operand\n"

        if not self.can_write(self.current):
            return "touch: permission denied\n"

        for name in args:

            if "/" in name:
                return (
                    "touch: only simple names "
                    "are supported\n"
                )

            if not self.current.get(name):

                self.current.add(
                    File(
                        name,
                        "",
                        self.current_user,
                        "users",
                        "rw-------",
                    )
                )

        self.save_disk()

        return ""

    def cat(self, args):

        if not args:
            return "cat: missing operand\n"

        target = self.resolve(args[0])

        if target is None:
            return (
                f"cat: {args[0]}: not found\n"
            )

        if isinstance(target, Directory):
            return (
                f"cat: {args[0]}: is a directory\n"
            )

        if not self.can_read(target):
            return "cat: permission denied\n"

        return target.content

    def write(self, args):

        if len(args) < 2:
            return (
                "write: usage: write <file> <text>\n"
            )

        filename = args[0]
        content = " ".join(args[1:])

        target = self.resolve(filename)

        if target:

            if isinstance(target, Directory):
                return "write: is a directory\n"

            if not self.can_write(target):
                return "write: permission denied\n"

            target.content = content

        else:

            if not self.can_write(self.current):
                return "write: permission denied\n"

            self.current.add(
                File(
                    filename,
                    content,
                    self.current_user,
                    "users",
                    "rw-------",
                )
            )

        self.save_disk()

        return ""

    def rm(self, args):

        if not args:
            return "rm: missing operand\n"

        if not self.can_write(self.current):
            return "rm: permission denied\n"

        for name in args:

            if self.current.get(name) is None:
                print(
                    f"rm: cannot remove '{name}': "
                    "no such file"
                )
                continue

            self.current.remove(name)

        self.save_disk()

        return ""

    # ========================================================
    # TREE
    # ========================================================

    def tree(self, args):

        print(".")
        self.print_tree(self.current, "")

        return ""

    def print_tree(self, directory, prefix):

        items = sorted(
            directory.children.items()
        )

        for index, (name, item) in enumerate(items):

            last = index == len(items) - 1

            branch = (
                "└── "
                if last
                else "├── "
            )

            if isinstance(item, Directory):

                print(
                    prefix +
                    branch +
                    name +
                    "/"
                )

                extension = (
                    "    "
                    if last
                    else "│   "
                )

                self.print_tree(
                    item,
                    prefix + extension,
                )

            else:

                print(
                    prefix +
                    branch +
                    name
                )

    # ========================================================
    # SHELL COMMANDS
    # ========================================================

    def clear(self, args):

        os.system(
            "cls"
            if os.name == "nt"
            else "clear"
        )

        return ""

    def echo(self, args):

        if not args and "PIPE_INPUT" in self.environment:
            return self.environment["PIPE_INPUT"]

        text = " ".join(args)

        # Environment variables
        for key, value in self.environment.items():

            if isinstance(value, str):
                text = text.replace(
                    "$" + key,
                    value,
                )

        return text + "\n"

    def whoami(self, args):
        return self.current_user + "\n"

    def uname(self, args):

        return (
            "PyOS pyos-kernel 2.0 "
            "Python-Virtual-Kernel x86_64\n"
        )

    def date(self, args):

        return datetime.now().strftime(
            "%A, %d %B %Y %H:%M:%S\n"
        )

    # ========================================================
    # ENVIRONMENT
    # ========================================================

    def env(self, args):

        lines = []

        for key, value in self.environment.items():

            if isinstance(value, str):
                lines.append(
                    f"{key}={value}"
                )

        return "\n".join(lines) + "\n"

    def export(self, args):

        if not args:
            return self.env([])

        for assignment in args:

            if "=" not in assignment:
                continue

            key, value = assignment.split(
                "=",
                1,
            )

            self.environment[key] = value

        return ""

    # ========================================================
    # HISTORY
    # ========================================================

    def history_cmd(self, args):

        lines = []

        for number, command in enumerate(
            self.history,
            1,
        ):
            lines.append(
                f"{number:4}  {command}"
            )

        return "\n".join(lines) + (
            "\n" if lines else ""
        )

    # ========================================================
    # PROCESSES
    # ========================================================

    def ps(self, args):

        lines = [
            "PID    USER       CPU%     RAM(MB)    COMMAND",
            "-----  ---------  -------  ---------  --------",
        ]

        for process in self.processes:

            process.update()

            lines.append(
                f"{process.pid:<6}"
                f"{process.user:<10}"
                f"{process.cpu:>6.1f}%   "
                f"{process.memory:>7}      "
                f"{process.name}"
            )

        return "\n".join(lines) + "\n"

    def top(self, args):

        print("\nPyOS Process Monitor")
        print("Press Ctrl+C to stop.")
        print()

        try:

            while True:

                os.system(
                    "cls"
                    if os.name == "nt"
                    else "clear"
                )

                print("PyOS TOP")
                print(
                    f"RAM: "
                    f"{self.used_ram}/"
                    f"{self.total_ram} MB"
                )

                print()

                print(
                    "PID    USER       CPU%     RAM     COMMAND"
                )

                for process in self.processes:

                    process.update()

                    print(
                        f"{process.pid:<6}"
                        f"{process.user:<10}"
                        f"{process.cpu:>6.1f}%   "
                        f"{process.memory:>5} MB  "
                        f"{process.name}"
                    )

                time.sleep(1)

        except KeyboardInterrupt:
            print()

        return ""

    def kill(self, args):

        if not args:
            return "kill: missing PID\n"

        try:
            pid = int(args[0])

        except ValueError:
            return "kill: invalid PID\n"

        if self.kill_process(pid):
            return (
                f"Process {pid} terminated.\n"
            )

        return (
            f"kill: process {pid} not found\n"
        )

    # ========================================================
    # PERMISSIONS
    # ========================================================

    def chmod(self, args):

        if len(args) != 2:
            return (
                "chmod: usage: chmod <permissions> <file>\n"
            )

        permissions = args[0]
        filename = args[1]

        target = self.resolve(filename)

        if target is None:
            return "chmod: file not found\n"

        if (
            not self.is_admin()
            and target.owner != self.current_user
        ):
            return "chmod: permission denied\n"

        if (
            len(permissions) == 9
            and all(
                c in "rwx-"
                for c in permissions
            )
        ):
            target.permissions = permissions
            self.save_disk()

            return ""

        return "chmod: invalid permissions\n"

    def chown(self, args):

        if len(args) != 2:
            return (
                "chown: usage: chown <user> <file>\n"
            )

        if not self.is_admin():
            return "chown: permission denied\n"

        username = args[0]
        filename = args[1]

        if username not in self.users:
            return "chown: user does not exist\n"

        target = self.resolve(filename)

        if target is None:
            return "chown: file not found\n"

        target.owner = username

        self.save_disk()

        return ""

    # ========================================================
    # USERS
    # ========================================================

    def id_cmd(self, args):

        user = self.users[self.current_user]

        groups = (
            "root"
            if user.admin
            else "users"
        )

        return (
            f"uid={self.current_user} "
            f"gid={groups} "
            f"groups={groups}\n"
        )

    def adduser(self, args):

        if not self.is_admin():
            return "adduser: permission denied\n"

        if not args:
            return "adduser: missing username\n"

        username = args[0]

        if username in self.users:
            return "adduser: user already exists\n"

        self.users[username] = User(
            username,
            "",
            False,
        )

        home = self.resolve("/home")

        home.add(
            Directory(
                username,
                home,
                username,
                "users",
                "rwx------",
            )
        )

        self.save_disk()

        return (
            f"User '{username}' created.\n"
        )

    def su(self, args):

        if not args:
            return "su: missing username\n"

        username = args[0]

        if username not in self.users:
            return "su: user does not exist\n"

        self.current_user = username

        self.environment["USER"] = username
        self.environment["HOME"] = (
            "/home/"
            + username
        )

        home = self.resolve(
            self.environment["HOME"]
        )

        if home:
            self.current = home

        return ""

    def sudo(self, args):

        if not args:
            return "sudo: missing command\n"

        if not self.is_admin():

            print(
                "[sudo] password for "
                + self.current_user
                + ":"
            )

            password = input()

            user = self.users[self.current_user]

            if password != user.password:
                return "sudo: incorrect password\n"

        old_user = self.current_user

        self.current_user = "root"

        result = self.execute(
            " ".join(args)
        )

        self.current_user = old_user

        return result
      # ========================================================
    # PACKAGE MANAGER
    # ========================================================

    def package_manager(self, args):

        if not args:
            print("Usage:")
            print("  apt install <package>")
            print("  apt remove <package>")
            print("  apt list")
            print("  apt search <name>")
            return

        action = args[0]

        if action == "list":

            print("Installed packages:")

            for package in self.installed_packages:
                print(f"  {package}")

            return

        if action == "search":

            if len(args) < 2:
                print("Usage: apt search <name>")
                return

            query = args[1].lower()

            available = [
                "python",
                "pysh",
                "coreutils",
                "nano",
                "vim",
                "git",
                "curl",
                "wget",
                "htop",
                "neofetch",
                "gcc",
                "make",
                "python-pip",
            ]

            results = [
                package
                for package in available
                if query in package.lower()
            ]

            if not results:
                print("No packages found.")
                return

            for package in results:
                status = (
                    "[installed]"
                    if package in self.installed_packages
                    else ""
                )

                print(f"  {package} {status}")

            return

        if action == "install":

            if len(args) < 2:
                print("Usage: apt install <package>")
                return

            package = args[1]

            if package in self.installed_packages:
                print(f"{package} is already installed.")
                return

            available = [
                "python",
                "pysh",
                "coreutils",
                "nano",
                "vim",
                "git",
                "curl",
                "wget",
                "htop",
                "neofetch",
                "gcc",
                "make",
                "python-pip",
            ]

            if package not in available:
                print(f"E: Unable to locate package {package}")
                return

            print(f"Reading package lists... Done")
            print(f"Building dependency tree... Done")
            print(f"Installing {package}...")

            time.sleep(0.5)

            self.installed_packages.append(package)

            print(f"Successfully installed {package}.")

            return

        if action == "remove":

            if len(args) < 2:
                print("Usage: apt remove <package>")
                return

            package = args[1]

            if package not in self.installed_packages:
                print(f"Package '{package}' is not installed.")
                return

            protected = {
                "python",
                "pysh",
                "coreutils",
            }

            if package in protected:
                print(
                    f"Cannot remove essential package '{package}'."
                )
                return

            self.installed_packages.remove(package)

            print(f"Removed {package}.")

            return

        print(f"apt: unknown action '{action}'")

    # ========================================================
    # PROCESS MANAGEMENT
    # ========================================================

    def ps(self):

        print(
            f"{'PID':<6}"
            f"{'USER':<12}"
            f"{'CPU%':<8}"
            f"{'MEM':<8}"
            f"{'COMMAND'}"
        )

        print("-" * 55)

        for process in self.processes:

            process.update()

            print(
                f"{process.pid:<6}"
                f"{process.user:<12}"
                f"{process.cpu:<8.1f}"
                f"{process.memory:<8} "
                f"{process.name}"
            )

    def top(self):

        print("PyOS process monitor")
        print("Press Ctrl+C to exit.")

        try:

            while True:

                os.system("clear")

                print("PyOS TOP")
                print("=" * 60)

                print(
                    f"RAM: "
                    f"{self.used_memory()} MB / "
                    f"{self.total_ram} MB"
                )

                print()

                self.ps()

                time.sleep(1)

        except KeyboardInterrupt:

            print("\nExited top.")

    def used_memory(self):

        return sum(
            process.memory
            for process in self.processes
        )

    def kill(self, args):

        if not args:
            print("Usage: kill <pid>")
            return

        try:
            pid = int(args[0])

        except ValueError:

            print("kill: invalid PID")
            return

        process = self.find_process(pid)

        if process is None:

            print(
                f"kill: process {pid} not found"
            )

            return

        if process.name == "init":

            print("kill: cannot kill init")

            return

        self.processes.remove(process)

        print(
            f"Process {pid} ({process.name}) terminated."
        )

    # ========================================================
    # NETWORKING
    # ========================================================

    def ping(self, args):

        if not args:

            print("Usage: ping <host>")

            return

        host = args[0]

        known_hosts = {
            "localhost": "127.0.0.1",
            "google.com": "142.250.72.14",
            "example.com": "93.184.216.34",
            "pyos.local": "10.0.0.1",
        }

        ip = known_hosts.get(host)

        if ip is None:

            print(
                f"ping: unknown host {host}"
            )

            return

        print(
            f"PING {host} ({ip})"
        )

        for i in range(4):

            latency = random.uniform(
                5,
                80
            )

            print(
                f"64 bytes from {ip}: "
                f"icmp_seq={i + 1} "
                f"time={latency:.1f} ms"
            )

            time.sleep(0.5)

        print()

        print(
            "--- ping statistics ---"
        )

        print(
            "4 packets transmitted, "
            "4 received, 0% packet loss"
        )

    def ifconfig(self):

        print("lo:")

        print(
            "    inet 127.0.0.1 "
            "netmask 255.0.0.0"
        )

        print(
            "    status: UP"
        )

        print()

        print("eth0:")

        print(
            "    inet 10.0.0.42 "
            "netmask 255.255.255.0"
        )

        print(
            "    broadcast 10.0.0.255"
        )

        print(
            "    status: UP"
        )

        print(
            "    RX packets: 1337"
        )

        print(
            "    TX packets: 9001"
        )

    # ========================================================
    # ENVIRONMENT
    # ========================================================

    def env(self):

        for key, value in sorted(
            self.environment.items()
        ):

            print(
                f"{key}={value}"
            )

    def export(self, args):

        if not args:

            print(
                "Usage: export NAME=value"
            )

            return

        expression = args[0]

        if "=" not in expression:

            print(
                "export: invalid assignment"
            )

            return

        name, value = expression.split(
            "=",
            1
        )

        if not name:

            print(
                "export: invalid variable name"
            )

            return

        self.environment[name] = value

        print(
            f"{name}={value}"
        )

    # ========================================================
    # USERS
    # ========================================================

    def id_command(self):

        user = self.users[
            self.current_user
        ]

        uid = (
            0
            if user.admin
            else list(
                self.users.keys()
            ).index(
                user.username
            ) + 1000
        )

        print(
            f"uid={uid}({user.username})"
        )

        if user.admin:

            print(
                "gid=0(root)"
            )

        else:

            print(
                f"gid={uid}({user.username})"
            )

    def add_user(self, args):

        if not self.is_admin():

            print(
                "adduser: permission denied"
            )

            return

        if not args:

            print(
                "Usage: adduser <username>"
            )

            return

        username = args[0]

        if username in self.users:

            print(
                f"User '{username}' already exists."
            )

            return

        password = input(
            "New password: "
        )

        self.users[username] = User(
            username,
            password,
            admin=False
        )

        home = Directory(
            username,
            self.root.get("home"),
            owner=username,
            group=username
        )

        self.root.get("home").add(home)

        print(
            f"User '{username}' created."
        )

    def su(self, args):

        if not args:

            print(
                "Usage: su <username>"
            )

            return

        username = args[0]

        if username not in self.users:

            print(
                f"su: user '{username}' does not exist"
            )

            return

        target = self.users[
            username
        ]

        if target.password:

            password = input(
                "Password: "
            )

            if password != target.password:

                print(
                    "su: authentication failure"
                )

                return

        self.current_user = username

        self.environment[
            "USER"
        ] = username

        self.environment[
            "HOME"
        ] = f"/home/{username}"

        print(
            f"Switched to user {username}."
        )

    def sudo(self, command):

        if not self.is_admin():

            print(
                f"{self.current_user} "
                "is not in the sudoers file."
            )

            return

        old_user = self.current_user

        self.current_user = "root"

        try:

            self.execute(
                command
            )

        finally:

            self.current_user = old_user

    # ========================================================
    # EDITOR
    # ========================================================

    def nano(self, args):

        if not args:

            print(
                "Usage: nano <filename>"
            )

            return

        filename = self.resolve(
            args[0]
        )

        parent_path = os.path.dirname(
            filename
        )

        basename = os.path.basename(
            filename
        )

        parent = self.resolve(
            parent_path
        )

        if not isinstance(
            parent,
            Directory
        ):

            print(
                "nano: invalid parent directory"
            )

            return

        existing = parent.get(
            basename
        )

        if isinstance(
            existing,
            File
        ):

            content = existing.content

        else:

            content = ""

        print(
            "GNU nano (PyOS edition)"
        )

        print(
            "Enter text. Type "
            ":wq on a new line to save and exit."
        )

        print()

        if content:

            print(content)

            print()

        lines = []

        while True:

            line = input()

            if line == ":wq":

                break

            lines.append(line)

        new_content = "\n".join(
            lines
        )

        if isinstance(
            existing,
            File
        ):

            existing.content = new_content

        else:

            parent.add(
                File(
                    basename,
                    new_content,
                    owner=self.current_user,
                    group=self.current_user
                )
            )

        self.save_disk()

        print(
            f"Saved {filename}"
        )

    # ========================================================
    # PYTHON SHELL
    # ========================================================

    def python_shell(self):

        print(
            "PyOS Python shell"
        )

        print(
            "Type exit() to leave."
        )

        allowed_builtins = {
            "abs": abs,
            "all": all,
            "any": any,
            "bool": bool,
            "dict": dict,
            "float": float,
            "int": int,
            "len": len,
            "list": list,
            "max": max,
            "min": min,
            "print": print,
            "range": range,
            "str": str,
            "sum": sum,
            "tuple": tuple,
        }

        namespace = {
            "__builtins__": allowed_builtins
        }

        while True:

            try:

                code = input(
                    ">>> "
                )

            except EOFError:

                break

            if code.strip() == "exit()":

                break

            try:

                try:

                    result = eval(
                        code,
                        namespace
                    )

                    if result is not None:

                        print(result)

                except SyntaxError:

                    exec(
                        code,
                        namespace
                    )

            except Exception as error:

                print(
                    f"{type(error).__name__}: "
                    f"{error}"
                )

    # ========================================================
    # REDIRECTION
    # ========================================================

    def write_redirect(
        self,
        filename,
        content,
        append=False
    ):

        """Write command output into a virtual file."""

        path = self.resolve(
            filename
        )

        parent_path = os.path.dirname(
            path
        )

        basename = os.path.basename(
            path
        )

        parent = self.resolve(
            parent_path
        )

        if not isinstance(
            parent,
            Directory
        ):

            print(
                f"redirection: "
                f"{parent_path}: "
                f"No such directory"
            )

            return

        existing = parent.get(
            basename
        )

        if isinstance(
            existing,
            File
        ):

            if not self.can_write(
                existing
            ):

                print(
                    "redirection: "
                    "Permission denied"
                )

                return

            if append:

                existing.content += content

            else:

                existing.content = content

        else:

            parent.add(
                File(
                    basename,
                    content,
                    owner=self.current_user,
                    group=self.current_user
                )
            )

        self.save_disk()

    # ========================================================
    # HELP
    # ========================================================

    def help(self):

        print(
            """
PyOS commands
=============

Filesystem
----------
ls
pwd
cd <directory>
mkdir <directory>
touch <file>
cat <file>
write <file> <text>
rm <file>
tree

Users
-----
whoami
id
adduser <username>
su <username>
sudo <command>

Permissions
-----------
chmod <mode> <file>
chown <user> <file>

Packages
--------
apt list
apt search <name>
apt install <package>
apt remove <package>

Processes
---------
ps
top
kill <pid>

Networking
----------
ping <host>
ifconfig

Environment
-----------
env
export NAME=value

Shell
-----
echo <text>
history
clear
nano <file>
python
neofetch

System
------
uname
date
reboot
shutdown
help

Redirection
-----------
command > file
command >> file

Pipes
-----
command1 | command2

Examples
--------
echo hello
echo hello > hello.txt
cat hello.txt
ls | cat
mkdir test
cd test
touch file.txt
write file.txt "Hello PyOS!"
cat file.txt

Package example
---------------
apt search python
apt install git
apt list

Process example
---------------
ps
kill 1002
"""
        )

    # ========================================================
    # NEOFETCH
    # ========================================================

    def neofetch(self):

        print(
            "        _____       "
        )

        print(
            "       / ___ \\     "
        )

        print(
            "      | |   | |     "
        )

        print(
            "      | |___| |     "
        )

        print(
            "       \\_____/      "
        )

        print()

        print(
            f"OS: PyOS {self.version}"
        )

        print(
            f"Host: {self.hostname}"
        )

        print(
            f"Kernel: PyOS-Kernel 1.0"
        )

        print(
            f"Shell: pysh"
        )

        print(
            f"User: {self.current_user}"
        )

        print(
            f"RAM: {self.total_ram} MB"
        )

        print(
            f"Processes: {len(self.processes)}"
        )

        print(
            f"Packages: {len(self.installed_packages)}"
        )

        print(
            "Terminal: PyTerminal"
        )

    # ========================================================
    # SYSTEM COMMANDS
    # ========================================================

    def uname(self, args):

        if args and args[0] == "-a":

            print(
                f"PyOS {self.hostname} "
                "1.0.0-pyos "
                "#1 SMP "
                "PyOS-Kernel x86_64"
            )

        else:

            print("PyOS")

    def date(self):

        print(
            datetime.now().strftime(
                "%a %b %d %H:%M:%S %Y"
            )
        )

    def reboot(self):

        print(
            "Broadcast message from root:"
        )

        print(
            "The system is going down for reboot!"
        )

        time.sleep(1)

        self.boot()

    def shutdown(self):

        print(
            "Broadcast message from root:"
        )

        print(
            "The system is going down for shutdown!"
        )

        time.sleep(1)

        self.running = False
      # ========================================================
    # COMMAND EXECUTION
    # ========================================================

    def execute(
        self,
        command,
        capture=False
    ):

        command = command.strip()

        if not command:
            return ""

        # ----------------------------------------------------
        # SUDO
        # ----------------------------------------------------

        if command.startswith("sudo "):

            self.sudo(
                command[5:]
            )

            return ""

        # ----------------------------------------------------
        # REDIRECTION
        # ----------------------------------------------------

        redirect_match = re.search(
            r"(>>|>)\s*(\S+)\s*$",
            command
        )

        if redirect_match:

            operator = redirect_match.group(1)

            filename = redirect_match.group(2)

            actual_command = command[
                :redirect_match.start()
            ].strip()

            output = self.execute(
                actual_command,
                capture=True
            )

            self.write_redirect(
                filename,
                output,
                append=(operator == ">>")
            )

            return ""

        # ----------------------------------------------------
        # PIPE
        # ----------------------------------------------------

        if "|" in command:

            parts = [
                part.strip()
                for part in command.split("|")
            ]

            pipe_data = ""

            for part in parts:

                self.environment[
                    "PIPE_INPUT"
                ] = pipe_data

                pipe_data = self.execute(
                    part,
                    capture=True
                )

            self.environment.pop(
                "PIPE_INPUT",
                None
            )

            if capture:

                return pipe_data

            print(pipe_data)

            return ""

        # ----------------------------------------------------
        # PARSE COMMAND
        # ----------------------------------------------------

        try:

            args = shlex.split(
                command
            )

        except ValueError as error:

            print(
                f"Parse error: {error}"
            )

            return ""

        if not args:

            return ""

        cmd = args[0]

        args = args[1:]

        # ----------------------------------------------------
        # CAPTURE OUTPUT
        # ----------------------------------------------------

        output_buffer = io.StringIO()

        old_stdout = sys.stdout

        if capture:

            sys.stdout = output_buffer

        try:

            # =================================================
            # FILESYSTEM
            # =================================================

            if cmd == "ls":

                self.ls(args)

            elif cmd == "pwd":

                print(
                    self.current_path
                )

            elif cmd == "cd":

                self.cd(args)

            elif cmd == "mkdir":

                self.mkdir(args)

            elif cmd == "touch":

                self.touch(args)

            elif cmd == "cat":

                self.cat(args)

            elif cmd == "write":

                self.write(args)

            elif cmd == "rm":

                self.rm(args)

            elif cmd == "tree":

                self.tree()

            # =================================================
            # USERS
            # =================================================

            elif cmd == "whoami":

                print(
                    self.current_user
                )

            elif cmd == "id":

                self.id_command()

            elif cmd == "adduser":

                self.add_user(args)

            elif cmd == "su":

                self.su(args)

            elif cmd == "sudo":

                if not args:

                    print(
                        "sudo: missing command"
                    )

                else:

                    self.sudo(
                        " ".join(args)
                    )

            # =================================================
            # PERMISSIONS
            # =================================================

            elif cmd == "chmod":

                self.chmod(args)

            elif cmd == "chown":

                self.chown(args)

            # =================================================
            # PACKAGE MANAGER
            # =================================================

            elif cmd in (
                "apt",
                "pkg"
            ):

                self.package_manager(
                    args
                )

            # =================================================
            # PROCESSES
            # =================================================

            elif cmd == "ps":

                self.ps()

            elif cmd == "top":

                self.top()

            elif cmd == "kill":

                self.kill(args)

            # =================================================
            # NETWORKING
            # =================================================

            elif cmd == "ping":

                self.ping(args)

            elif cmd in (
                "ifconfig",
                "ip"
            ):

                self.ifconfig()

            # =================================================
            # ENVIRONMENT
            # =================================================

            elif cmd == "env":

                self.env()

            elif cmd == "export":

                self.export(args)

            # =================================================
            # SHELL COMMANDS
            # =================================================

            elif cmd == "echo":

                text = " ".join(args)

                if (
                    not text
                    and "PIPE_INPUT"
                    in self.environment
                ):

                    text = self.environment[
                        "PIPE_INPUT"
                    ]

                print(
                    text
                )

            elif cmd == "history":

                for index, item in enumerate(
                    self.history,
                    start=1
                ):

                    print(
                        f"{index:4}  {item}"
                    )

            elif cmd == "clear":

                os.system("clear")

            elif cmd == "nano":

                self.nano(args)

            elif cmd == "python":

                self.python_shell()

            # =================================================
            # SYSTEM INFORMATION
            # =================================================

            elif cmd == "neofetch":

                self.neofetch()

            elif cmd == "uname":

                self.uname(args)

            elif cmd == "date":

                self.date()

            # =================================================
            # POWER MANAGEMENT
            # =================================================

            elif cmd == "reboot":

                self.reboot()

            elif cmd in (
                "shutdown",
                "poweroff"
            ):

                self.shutdown()

            # =================================================
            # HELP
            # =================================================

            elif cmd == "help":

                self.help()

            # =================================================
            # EXIT
            # =================================================

            elif cmd == "exit":

                self.running = False

            # =================================================
            # UNKNOWN COMMAND
            # =================================================

            else:

                print(
                    f"{cmd}: command not found"
                )

        finally:

            sys.stdout = old_stdout

        return output_buffer.getvalue()

    # ========================================================
    # SHELL LOOP
    # ========================================================

    def run(self):

        self.boot()

        while self.running:

            try:

                prompt = (
                    f"{self.current_user}"
                    f"@{self.hostname}:"
                    f"{self.current_path}"
                    f"$ "
                )

                command = input(
                    prompt
                )

                command = command.strip()

                if not command:

                    continue

                # ------------------------------------------------
                # Add command to history
                # ------------------------------------------------

                self.history.append(
                    command
                )

                # ------------------------------------------------
                # Execute command
                # ------------------------------------------------

                self.execute(
                    command
                )

            except KeyboardInterrupt:

                print()

            except EOFError:

                print()

                break

            except Exception as error:

                print(
                    f"PyOS error: {error}"
                )

        print(
            "PyOS halted."
        )


# ============================================================
# MAIN
# ============================================================

def main():

    try:

        PyOS().run()

    except KeyboardInterrupt:

        print()

        print(
            "PyOS terminated."
        )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
