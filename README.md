# Cerberus

Cerberus offers customizable plugin functionality, proxy support, encompassing both standard proxies and Tor and Mutiple Wordlists Attack. Its user-friendly interface, and it features a flexible response check mechanism accepting `Status Code`, `JSON Data`, `Status Text`, and `Full Response Text` as valid responses.

> [!NOTE]
> Significantly, the process verifies the presence of a designated key within the JSON response.

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
    - [Setting Up Proxies and Tor](#setting-up-proxies-and-tor)
        - [Setting Up on Linux](#on-linux)
        - [Setting Up on Windows](#on-windows)
    - [Start an Attack](#starting-an-attack)
        - [How to use Mutiple Wordlists Attack](#how-to-use-mutiple-wordlist-attack)
    - [Setting up Plugins](#setting-up-plugins)
- [Help](#help)
- [Disclaimer](/DISCLAIMER.md)
- [Contribuiting](/CONTRIBUTING.md)

## Installation

```bash
git clone https://github.com/kayake/cerberus.git && cd cerberus && pip install -r requirements.txt
```

> [!NOTE]
> We recommend using `git clone https://github.com/kayake/cerberus.git && cd cerberus && poetry install`.

<sub>
🅘 If your PIP version is 23.x.x, please review the documentation <a href="https://github.com/kayake/cerberus/issues/2"> Python package installation failure (PIP: >= 23.0.0)</a>.</sub>

## Usage

```bash
python3 crbs.py --help
```

> [!WARNING]
> For version compatibility details, please consult the [Security Policy](/SECURITY.md) document.

## Configuration

To enhance anonymity, proxy servers or Tor should be configured. Cerberus simplifies this configuration process, thereby improving overall anonymity.

### Setting up Proxies and Tor

Two methods exist for proxy configuration: command-line interface or a configuration file (configs/attack.yaml)

The file should be formatted as follows:

```yaml
connection:
    proxy: http://username:password@127.0.0.1:9273
    proxies: /path/to/proxies.txt
    tor:
        control_port: 9051
        address: socks5://127.0.0.1:9050
        password: my_enc_passwordconnection:
        proxy: 
```

> [!IMPORTANT]
> The tor must be set up, see [Setting up tor](#setting-up-tor) for more informations 

To utilize Tor, adhere to these fundamental steps:

### Set up Control Port and Password

#### On Linux

```zsh
~$ tor --hash-password "<your_plain_text_password>"
~$ sudo nano /etc/tor/torrc
```

> [!IMPORTANT]
> The password is optional

```.torrc
ControlPort 9051  # Control port (you can choose another port if needed)
HashedControlPassword <hashed_password>  # Encrypted password (Optional)
# CookieAuthentication 1  # Optional (cookie-based authentication)
```

#### On Windows


```zsh
C:\> cd "C:\Users\<YourUser>\Desktop\Tor Browser\Browser\TorBrowser\Tor"
C:\> tor.exe --hash-password "<your_plain_text_password>"
```

> [!NOTE]
> This step is optional

If you installed the Tor Browser, the torrc file is usually located at:

```txt
C:\Users\<YourUser>\Desktop\Tor Browser\Browser\TorBrowser\Data\Tor\torrc
```

Open it with a text editor (e.g., Notepad++)

```.torrc
ControlPort 9051
HashedControlPassword <hashed_password>
```

Now we can use Tor. Use option `--tor` (in attack command).

## Starting an Attack

First of all, you must configure [Config Attack File](/configs/attack.yaml)

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
> Do not exceed 100 `limit_connections`. Typically, hardware supports up to 100 simultaneous connections. If you are confident in your hardware's capabilities, you may increase this limit or set it to `0` to remove `AioHTTP` restrictions (**At your own risk**).

After that, you can start the attack by typing:

```zsh
~ $ cerberus --verbose 3 attack
```

> [!TIP]
> Use option `--verbose` so that you can see response status and requests sent

The `--tor` option may be replaced with `--proxy` or `--proxies`.

### How to use Mutiple Wordlist Attack

To start a *Mutiple Wordlist Attack* you must transform the wordlist(s) to an array:

```yaml
# ...
credentials:
  usernames: [example.1.txt, example.2.txt]
  passwords: [/usr/share/dict/brazilian, /usr/share/dict/american-english]
```

> [!WARNING]
> Pay attention to the `[]`, Cerberus won't read arguments like this: `example.2.txt, example.1.txt`, it will consider as a single Wordlist.

> [!CAUTION]
> This feature demands high CPU usage, so **DO NOT** use more than 2 **Wordlists** (Cerberus will warn you when that happens).

## Setting up Plugins

To extend functionality, plugins may be added.  Should you require a new plugin, please create a single file and place it within the `lib/plugins` directory. The file must adhere to the following structure:

```py
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

Subsequently, execute the plugin.

```zsh
cerberus --verbose 3 plugin --list
==================================================
test/hello.world.py - My First Plugin!
==================================================
cerberus --verbose 3 plugin --use test/hello.world.py
cerberus test(test/hello.world.py) > a ay au
Hello world!
a
ay
au
cerberus test(test/hello.world.py) >  
```

## Help

```zsh
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

cerberus --no-cache --verbose 3 --attack
```
