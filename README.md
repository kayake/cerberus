# Cerberus

Cerberus provides customizable plugin functionality, proxy support (including standard proxies and Tor), and the ability to perform attacks using multiple wordlists. It features a user-friendly interface and a flexible response-check mechanism that accepts `Status Code`, `JSON Data`, `Status Text`, and `Full Response Text` as valid responses.

---

## Table of Contents

- [Disclaimer](#disclaimer)
- [Contributing](#contributing)
- [Installation](#installation)
  - [Installtion from The Development Branch](#installing-from-the-development-branch)
- [Usage](#usage)
- [Configuration](#configuration)
  - [Setting Up Proxies and Tor](#setting-up-proxies-and-tor)
    - [Example Configuration File](#example-configuration-file)
    - [Setting up Control Port and Password](#setting-up-control-port-and-password)
      - [Setting Up on Linux](#on-linux)
      - [Setting Up on Windows](#on-windows)
- [Starting an Attack](#starting-an-attack)
  - [Starting The Attack](#starting-the-attack)
    - [Example Configuration File](#example-configuration-file-1)
  - [How to Use Multiple Wordlists Attack](#how-to-use-multiple-wordlists-attack)
- [Setting Up Plugins](#setting-up-plugins)
  - [Example Plugin](#example-plugin)
  - [Running Plugin](#running-the-plugin)
- [Help](#help)

---

## Disclaimer

For important legal and usage information, please refer to the [Disclaimer](/DISCLAIMER.md) document.

---

## Contributing

If you wish to contribute to the project, kindly review the [Contributing Guidelines](/CONTRIBUTING.md) before proceeding.

---

## Installation

To install Cerberus, run the following command:

```bash
git clone https://github.com/kayake/cerberus.git && cd cerberus && pip install -r requirements.txt
```

> [!NOTE]
> We recommend using `git clone https://github.com/kayake/cerberus.git && cd cerberus && poetry install`.

<sub>
🅘 If your PIP version is 23.x.x, please review the documentation on <a href="https://github.com/kayake/cerberus/issues/2">Python package installation failure (PIP: >= 23.0.0)</a>.
</sub>

### Installing from the Development Branch
To install Cerberus from the development branch, run the following command:

```bash
git clone https://github.com/kayake/cerberus.git --branch dev --single-branch && cd cerberus && pip install -r requirements.txt
```

> [!WARNING]
> The development branch is intended for testing purposes only.

---

## Usage

To view available commands and options, run:

```bash
python3 crbs.py --help
```

> [!IMPORTANT]
> For version compatibility details, please consult the [Security Policy](/SECURITY.md) document.

---

## Configuration

To enhance anonymity, proxy servers or Tor should be configured. Cerberus simplifies this configuration process, thereby improving overall anonymity.

### Setting Up Proxies and Tor

There are two methods for proxy configuration: via the command-line interface or through a configuration file (`configs/attack.yaml`).

#### Example Configuration File

```yaml
connection:
        proxy: http://username:password@127.0.0.1:9273
        proxies: /path/to/proxies.txt
        tor:
                control_port: 9051
                address: socks5://127.0.0.1:9050
                password: my_enc_password
```

> [!IMPORTANT]  
> Tor must be set up. See [Setting Up Tor](#setting-up-control-port-and-password) for more information.

#### Setting Up Control Port and Password

##### On Linux

```bash
tor --hash-password "<your_plain_text_password>"
sudo nano /etc/tor/torrc
```

> [!NOTE]
> The password is optional.

```plaintext
ControlPort 9051  # Control port (you can choose another port if needed)
HashedControlPassword <hashed_password>  # Encrypted password (Optional)
# CookieAuthentication 1  # Optional (cookie-based authentication)
```

##### On Windows

```bash
cd "C:\Users\<YourUser>\Desktop\Tor Browser\Browser\TorBrowser\Tor"
tor.exe --hash-password "<your_plain_text_password>"
```

> [!NOTE]  
> This step is optional.

If you installed the Tor Browser, the `torrc` file is usually located at:

```plaintext
C:\Users\<YourUser>\Desktop\Tor Browser\Browser\TorBrowser\Data\Tor\torrc
```

Open it with a text editor (e.g., Notepad++).

```plaintext
ControlPort 9051
HashedControlPassword <hashed_password>
```

Now you can use Tor. Use the `--tor` option in the attack command.

---

## Starting an Attack

First, configure the [Attack Configuration File](/configs/attack.yaml).

### Example Configuration File

```yaml
body:
    url: https://example.com/login/
    method: POST
    headers: asdf
    data: username=^USER^&password=^PASS^

connection:
    timeout: 50
    verify_ssl: true
    limit_connections: 100
    proxy: http://username:password@127.0.0.1:9273
    proxies: /path/to/proxies.txt
    tor:
        control_port: 9051
        address: socks5://127.0.0.1:9050
        password: my_enc_password

response:
    success: ~
    fail: 401

credentials:
    usernames: admin
    passwords: /usr/share/dict/brazilian
```

> [!CAUTION]  
> Do not exceed 100 `limit_connections`. Typically, hardware supports up to 100 simultaneous connections. If you are confident in your hardware's capabilities, you may increase this limit or set it to `0` to remove `AioHTTP` restrictions (**at your own risk**).

### Starting the Attack

Run the following command:

```bash
cerberus --verbose 3 attack
```

> [!TIP] 
> Use the `--verbose` option to view response statuses and requests sent.

The `--tor` option may be replaced with `--proxy` or `--proxies`.

### How to Use Multiple Wordlists Attack

To start a *Multiple Wordlists Attack*, transform the wordlist(s) into an array:

```yaml
credentials:
    usernames: [example.1.txt, example.2.txt]
    passwords: [/usr/share/dict/brazilian, /usr/share/dict/american-english]
```

> [!WARNING]  
> Pay attention to the `[]`. Cerberus will not read arguments like this: `example.2.txt, example.1.txt`. It will consider them as a single wordlist.

> [!CAUTION]
> This feature demands high CPU usage, so **DO NOT** use more than two **wordlists** (Cerberus will warn you if this happens).

---

## Setting Up Plugins

To extend functionality, plugins may be added. Create a single file and place it within the `lib/plugins` directory. The file must adhere to the following structure:

#### Example Plugin

```python
# lib/plugins/test/hello.world.py

class MyClass:
        description = "My First Plugin!"
        """ A generic Class Name """
        def run(self, arguments):
                print("Hello world!")
                """ Getting arguments """
                for argument in arguments:
                        print(argument)
```

#### Running the Plugin

```bash
cerberus --verbose 3 plugin --list
==================================================
test/hello.world.py - My First Plugin!
==================================================
cerberus --verbose 3 plugin --use test/hello.world.py -args="--foo foo"
  
```

---

## Help

```bash
usage: cerberus [-h] [--version] [--update] [--verbose LEVEL] {attack,plugin} ...

options:
  -h, --help            show this help message and exit

Commands:
  {attack,plugin}
    attack              Start an attack (Consider executing python3 crbs.py attack -h for attack options)
    plugin              Use a plugin in 'lib/plugins/'

Version options:
  --version             Show the version

Update options:
  --update, -u          Update Cerberus

Others:
  --verbose LEVEL, -v LEVEL
                        Set debug level

cerberus --verbose 3 attack -h
```
