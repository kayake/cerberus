# Cerberus

> [!WARNING]
> THIS PROJECT IS IN BETA. IF THERE ARE ANY BUGS OR PROBLEMS, PLEASE REPORT THEM TO [Issue](https://github.com/kayake/cerberus/issues)


A bruteforce HTTP(s) tool
> [!IMPORTANT]
> This project was inspired by [Hydra](https://salsa.debian.org/pkg-security-team/hydra), this project is not a COPY

## Usage

```bash
python3 crbs.py
```

> [!WARNING]
> For version compatibility details, please consult the [Security Policy](/SECURITY.md) document.

### Setting up proxies

Two methods exist for proxy configuration: command-line interface or a configuration file (config.yaml)

#### Using shell

```zsh
cerberus > config --set proxy.address 127.0.0.1:8080
cerberus > config --set proxy.protocol http
```

The file should be formatted as follows:

```yaml
proxy:
    address: 127.0.0.1:8080
    protocol: http
```

Furthermore, you can generate and configure a proxy list as follows:

```zsh
cerberus > config --set proxies your/proxies_list
```

> [!IMPORTANT]
> The proxy list must follow a structure. [Proxies List Stucture](#proxies-list-structure)

### Edit .yaml file

As previously discussed, modifying the .yaml file offers the simplest approach, as follows:

```yaml
proxies: my/proxy/list
proxy:
    address: 127.0.0.1
    protocol: http
```

> [!NOTE]
> As previously discussed, adherence to a defined structure for proxy list configuration is required.

### Proxies List Structure

The proxy list must adhere to the following structure:

```txt
host:port protocol
user:password@host:port protocol
```

## Setting up Tor

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

### Configure Tor in .yaml File

```yaml
tor:
    protocol: socks5
    port: 9050
    control_port: 9051
    password: my_hashed_password # if there ins't password, leave it null
```

Now we can use Tor. Use option `--tor` (in attack command).

## Commands

### Start an Attack

```txt
cerberus > attack -u https://example.com/ -D user=^USER^&pass=^PASS^ -R 401 -T 6 --tor --random-agent -l admin -P password/list.txt
```

> [!TIP]
> When using Tor, limit the number of threads.

The `--tor` option may be replaced with `--proxy` or `--proxies`.

### Plugins

To extend functionality, plugins may be added.  Should you require a new plugin, please create a single file and place it within the `lib/plugins/` directory. The file must adhere to the following structure:

```py
# lib/plugins/test/hello.world.py

class MyClass:
    description = "My First Plugin!"
    """ A generic Class Name """
    def __init__(self, this):
        self.this = this # lib/core/shell/handler.py properties

    def run(self, arguments):
        print("Hello world!")
        """ Getting arguments """
        for argument in arguments:
            print(argument)
```

Subsequently, execute the plugin.

```zsh
cerberus > plugin list
==================================================
test/hello.world.py - My First Plugin!
==================================================
cerberus > plugin use test/hello.world.py
cerberus test(test/hello.world.py) > a ay au
Hello world!
a
ay
au
cerberus test(test/hello.world.py) > 
```

### Help

```zsh
cerberus > ?

help - It helps you
attack - Start the bruteforce attack
plugin - Use any plugins in /lib/plugins/
config - Configure your configuration file

cerberus > 
```
