# ServerDesk

**ServerDesk** is a lightweight, framebuffer-based touchscreen menu for Linux servers – purpose-built for direct control and monitoring without the need for a graphical desktop environment.

Designed for environments with direct physical access, **ServerDesk** provides quick access to essential system commands such as process monitoring, log inspection, shutdown/reboot actions, and more – all through a clean, responsive overlay interface operated via touch input.

![Overlay](./assets/menu.png)

## Key Features

- **Framebuffer rendering** – no X11, Wayland or window manager required
- **Touchscreen-friendly UI** – designed for small screens (e.g., 1024×600)
- **Command-driven logic** – easily extensible via a simple JSON configuration
- **Secure and local** – no remote access, no internet exposure
- **Failsafe execution** – subprocesses run in isolated sessions, auto-recovery supported
- **Modular structure** – clean separation of scripts, assets and logic

**ServerDesk** is ideal for embedded or dedicated maintenance terminals, homelab servers, or rack-mounted systems with integrated display hardware.

## Requirements

### Hardware

- Linux-capable device with framebuffer support (e.g. `/dev/fb0`)
- Touchscreen input device (e.g. `/dev/input/eventX`)

### Software

- Any Linux distribution with:
  - Python 3.10+
  - Systemd
  - Framebuffer device enabled (no X11 or Wayland needed)
  - Write access to `/dev/fb0` and `/dev/input/eventX`
- Some packages to run **ServerDesk** commands:
  - `htop`, `iftop` and `iotop`: monitoring tools
  - `lm-sensors`: hardware monitoring
- Python packages: `evdev` and `Pillow`

You can install them via:

```bash
sudo apt install \
  htop iftop iotop lm-sensors \
  python3 python3-evdev python3-pillow
```

## Installation

### Step 1 — Create User

It is recommended to run **ServerDesk** under a dedicated system user. This enhances separation and allows fine-tuned sudo permissions. Name this user whatever you want, but bear in mind to change all the commands listed below to match your choice.

Here, the username `watchdog` will be used:

```bash
# Create the user account
sudo useradd -r -m -d /home/watchdog -s /usr/sbin/nologin watchdog

# Grant the user necessary rights (framebuffer and tty)
sudo usermod -aG video,tty watchdog

# You may check those with
groups watchdog
```

To allow **ServerDesk** to run commands without password prompts, edit the sudoers file:

```bash
sudo nano /etc/sudoers.d/serverdesk
```

And add the list of commands needet to run **ServerDesk**:

```bash
watchdog ALL=(ALL) NOPASSWD: \
  /usr/bin/apt, \
  /usr/bin/apt-get, \
  /usr/bin/chvt, \
  /usr/bin/df, \
  /usr/bin/dmesg, \
  /usr/bin/dpkg, \
  /usr/bin/htop, \
  /usr/bin/journalctl, \
  /usr/bin/systemctl, \
  /usr/bin/w, \
  /usr/sbin/iftop, \
  /usr/sbin/iotop, \
  /usr/sbin/mdadm
```

### Step 2 — Cloning Repository

Clone the **ServerDesk** repository to the appropriate location:

```bash
git clone https://github.com/komed3/serverdesk /home/watchdog/serverdesk
sudo chown -R watchdog:watchdog /home/watchdog/serverdesk
```

**Tip:** You can clone this repository with any user, but ownership must be transferred to your designated service user afterward, so the service can run the program without disruptions.
