import re
import subprocess
import hashlib

# Get the output of the lxc-ls command
lxc_ls_output = subprocess.check_output(['lxc-ls', '-f'], text=True)

# Regex patterns and their corresponding color codes
patterns_and_colors = {
    # Colorize headers (yellow)
    r'\b(NAME|STATE|AUTOSTART|GROUPS|IPV4|IPV6|UNPRIVILEGED)\b': "\033[38;2;255;255;0m",  # Yellow

    # Colorize the STATE column for STOPPED and RUNNING
    r'\bSTOPPED\b': "\033[38;2;255;0;0m",  # Red
    r'\bRUNNING\b': "\033[38;2;0;255;0m",  # Green
}

# Define specific color for each IP block (CIDR ranges)
ip_color_mapping = {
    '10.': "\033[38;2;255;153;153m",  # Red for 10.0.0.0/8
    '172.1[6-9].': "\033[38;2;100;255;190m",  # Green for 172.16.0.0/12 to 172.19.x.x
    '172.2[0-9].': "\033[38;2;230;255;170m",  # Green for 172.20.x.x to 172.29.x.x
    '172.3[0-1].': "\033[38;2;0;255;0m",  # Green for 172.30.x.x to 172.31.x.x
    '192.168.': "\033[38;2;0;0;255m",  # Blue for 192.168.0.0/16
}

# Function to generate a color for container names
def generate_color(name):
    # Hash the name to generate a unique color
    hash_object = hashlib.md5(name.encode())
    hash_hex = hash_object.hexdigest()
    # Use different parts of the hash to generate RGB values
    r = (int(hash_hex[1:5], 16) % 128 + 128)
    g = (int(hash_hex[1:4], 16) % 128 + 128)
    b = (int(hash_hex[4:9], 16) % 128 + 128)
    return f"\033[38;2;{r};{g};{b}m"

# Function to apply color to IP addresses based on the CIDR block prefix
def colorize_ip(match):
    ip = match.group(0)
    for prefix, color_code in ip_color_mapping.items():
        if re.match(f"^{prefix}", ip):  # Match any IP starting with the prefix
            return f"{color_code}{ip}\033[0m"
    return ip  # If no match, return as is

# Function to apply color to 'false' in the UNPRIVILEGED column
def colorize_false_unprivileged(match):
    return f"\033[38;2;220;105;140m{match.group(0)}\033[0m"  # Light green for false

# Function to apply color to '0' in the AUTOSTART column
def colorize_zero_autostart(match):
    return f"\033[38;2;155;220;155m{match.group(0)}\033[0m"  # Light blue for 0 in AUTOSTART

# Apply each regex pattern and color code to the output
highlighted_output = lxc_ls_output

# Apply colorization for headers, state, etc.
for pattern, color_code in patterns_and_colors.items():
    highlighted_output = re.sub(pattern, lambda match: f"{color_code}{match.group(0)}\033[0m", highlighted_output, flags=re.M)

# Apply colorization to IP addresses
highlighted_output = re.sub(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b', colorize_ip, highlighted_output)

# Colorize the names under the NAME column
highlighted_output = re.sub(r'^\s*(\w[\w-]+)', lambda match: f"{generate_color(match.group(1))}{match.group(1)}\033[0m", highlighted_output, flags=re.M)

# Colorize 'false' in the UNPRIVILEGED column specifically
highlighted_output = re.sub(r'(?<=\s)false(?=\s|$)', colorize_false_unprivileged, highlighted_output)

# Colorize '0' in the AUTOSTART column specifically
highlighted_output = re.sub(r'(?<=\s)0(?=\s|$)', colorize_zero_autostart, highlighted_output)

# Print the highlighted output to the terminal
print(highlighted_output)
