# Cerberus

A bruteforce HTTP(s) tool, similar to [Hydra](https://salsa.debian.org/pkg-security-team/hydra)

> [!IMPORTANT]
> This project was inspired by [Hydra](https://salsa.debian.org/pkg-security-team/hydra), this project is not a COPY

## 1 How it works?

Unlike [Hydra](https://salsa.debian.org/pkg-security-team/hydra), Cerberus uses only threads to perform HTTP(s) requests, which makes it slower.

### 1.1 Setting up proxies

You have 2 options to set up a proxy: using a shell, or configuring it in a file (config.yaml)

#### 1.1.1 Using shell

```zsh
cerberus > config --set proxy.address 127.0.0.1:8080
cerberus > config --set proxy.protocol http
```

In the file it should look like this:

```yaml
proxy:
    address: 127.0.0.1:8080
    protocol: http
```

In addition, you can create a proxy list and set up it, like this:

```zsh
cerberus > config --set proxies your/proxies_list
```

> [!IMPORTANT]
> The proxy list must follow a structure. ([Proxies List Stucture](#113-proxies-list-structure))

### 1.1.2 Edit .yaml file

As mentioned before, you can edit .yaml file, witch is the easiest way, like this:

```yaml
proxies: my/proxy/list
proxy:
    address: 127.0.0.1
    protocol: http
```

> [!NOTE]
> As previously mentioned, you need to follow a structure to set up proxies list

### 1.1.3 Proxies List Structure

The proxy list structure must be:

```txt
host:port protocol
user:password@host:port protocol
```

## 1.2 Setting up Tor

You can use Tor, but, you need to follow this basics steps:

### 1.2.1 Set up Control Port and Password

#### 1.2.1.1 On Linux

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

#### 1.2.1.2 On Windows


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

### 1.2.2 Configure Tor in .yaml File

```yaml
tor:
    protocol: socks5
    port: 9050
    control_port: 9051
    password: my_hashed_password # if there ins't password, leave it null
```

Now we can use Tor. Use option `--tor` (in attack command).

## 2 Commands

### 2.1 Start an Attack

```txt
cerberus > attack -u https://example.com/ -D user=^USER^&pass=^PASS^ -R 401 -T 6 --tor --random-agent -l admin -P password/list.txt
```

> [!TIP]
> If you are using Tor, use few threads.

You can change option `--tor` to `--proxy` or `--proxies`

### 2.2 Plugins

You can add plugins, that helps you to do another activity or attack. If you want, to add, or create one, create a **SINGLE** file and put it in the folder `lib/plugins/`.
You need to follow a structure like this:

```py
# lib/plugins/test/hellow.world.py

class MyClass:
    description = "My First Plugin!"
    """ A generic Class Name """
    def __init__(self, this):
        self.this = this # You can get many Shell properties with "this" argument

    def run(self, arguments):
        print("Hello world!")
        """ Getting arguments """
        for argument in arguments:
            print(argument)
```

After that, you can execute the plugin

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

### 2.3 Help

```zsh
~$ python3 crbs.py

cerberus > ?

help - It helps you
attack - Start the bruteforce attack
plugin - Use any plugins in /lib/plugins/
config - Configure your configuration file

cerberus > 
```
