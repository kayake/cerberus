import argparse

class Attack:
    name = "attack"
    aliases = ["run", "brute", "bruteforce", "start", "r"]
    def __init__(self, this):
        self.cache = this
        self.parser = argparse.ArgumentParser(prog="attack", usage='attack -u https://exampe.com/ --data="user=admin&pass=^PASS^" --random-agent --tor')
        g1 = self.parser.add_argument_group(title="Target", description="Need to be provided to start the bruteforce attack.")
        g1.add_argument("--url", "-u", type=str, help="The target to attack.")
        g2 = self.parser.add_argument_group(title="Wordlists", description="At least, 2 of these options need to be provided (e.g: attack -l admin -P /usr/share/dict/brazilian).")
        g2.add_argument("--passwords", "-P", type=str, help="Passwords list.")
        g2.add_argument("--logins", "-L", type=str, help="Usernames list.")
        g2.add_argument("--login", "-l", type=str, help="Username account.")
        g2.add_argument("--password", "-P", type=str, help="Password account.")

        g3 = self.parser.add_argument_group(title="Request", description="'Data' options is required to start any attack. All this options are used to customize the request, like adding you own header.")
        g3.add_argument("--data", "-D", type=str, help="The file of the data (in .txt) or raw to send.")
        g3.add_argument("--headers", "-H", type=str, help="The headers file to use.")
        g3.add_argument("--random-agent", action="store_true", help="Choose, randomily, an user agent.", required=False)
        g3.add_argument("--tor")

    def execute(self, arguments):
        if not "--" in arguments:
            return self.parser.print_help()

