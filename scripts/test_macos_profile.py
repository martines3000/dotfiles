import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest


BAR = pathlib.Path(__file__).resolve().parents[1] / "profiles/macos/v2-paw/home/.config/sketchybar"


class NetworkWidgetTests(unittest.TestCase):
    def arguments(self, network, vpn=""):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            log = root / "calls.jsonl"
            mock = f"#!{sys.executable}\n" + '''import json, os, pathlib, sys
name = pathlib.Path(sys.argv[0]).name
if name == "scutil":
    print(os.environ["TEST_VPN"] if "--nc" in sys.argv else os.environ["TEST_NETWORK"])
elif name == "networksetup":
    print("Hardware Port: Wi-Fi\\nDevice: en7")
else:
    with open(os.environ["TEST_LOG"], "a") as stream:
        stream.write(json.dumps(sys.argv[1:]) + "\\n")
'''
            for name in ["scutil", "networksetup", "sketchybar"]:
                path = root / name
                path.write_text(mock)
                path.chmod(0o755)
            network = "IPv4 network interface information\n" + network + "\nIPv6 network interface information\n"
            env = dict(os.environ, PATH=str(root) + ":" + os.environ["PATH"], CONFIG_DIR=str(BAR), NAME="wifi", SENDER="wifi_change", TEST_NETWORK=network, TEST_VPN=vpn, TEST_LOG=str(log))
            subprocess.run(["bash", str(BAR / "plugins/wifi.sh")], env=env, check=True, capture_output=True, text=True)
            return [arg for line in log.read_text().splitlines() for arg in json.loads(line)]

    def labels(self, network):
        return [arg for arg in self.arguments(network) if arg.startswith("label=")]

    def test_connected_wifi_uses_discovered_interface(self):
        labels = self.labels("en7 : flags IPv4\n address : 203.0.113.20")
        self.assertIn("label=Wi-Fi 203.0.113.20", labels)

    def test_dual_stack_flags_do_not_end_ipv4_section(self):
        labels = self.labels("en7 : flags : 0x7 (IPv4,IPv6,DNS)\n address : 203.0.113.20")
        self.assertIn("label=Wi-Fi 203.0.113.20", labels)

    def test_other_interface_does_not_claim_wifi(self):
        labels = self.labels("en4 : flags IPv4\n address : 203.0.113.20")
        self.assertFalse(any("Wi-Fi" in label for label in labels))

    def test_tunnel_retains_existing_indicator(self):
        args = self.arguments("utun4 : flags IPv4")
        self.assertEqual(args[args.index("vpn") + 1], "drawing=on")

    def test_inactive_or_ipv6_only_tunnel_does_not_claim_vpn(self):
        self.assertIn("label=offline", self.labels("IPv6 network interface information\nutun4 : flags IPv6"))

    def test_connected_vpn_service_shows_separate_icon_without_ipv4_tunnel(self):
        args = self.arguments("en7 : flags : 0x7 (IPv4,IPv6,DNS)\n address : 203.0.113.20", '* (Connected) TEST VPN')
        self.assertIn("label=Wi-Fi 203.0.113.20", args)
        self.assertEqual(args[args.index("vpn") + 1], "drawing=on")

    def test_disconnected_vpn_and_idle_tunnels_remain_hidden(self):
        args = self.arguments("en7 : flags IPv4\n address : 203.0.113.20\nIPv6 network interface information\nNetwork interfaces: en7 utun4", '* (Disconnected) TEST VPN')
        self.assertEqual(args[args.index("vpn") + 1], "drawing=off")


if __name__ == "__main__":
    unittest.main()
