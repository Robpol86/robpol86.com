#!/bin/bash

# Tar up and encrypt specified files before encoding them to QR codes.
#
# https://github.com/Robpol86/robpol86.com/blob/master/docs/_static/airgap.sh
#
# Using large QR codes to hop the air gap and transmit files out of this host
# with no network connectivity.
# Generate and print a temporary password used to encrypt the file contents.
# Save as (chmod +x): /usr/local/bin/airgap
#
# Reconstruct data on OS X with the following:
# 1. Read QR codes from this host's screen using phone app.
# 2. Have phone save text data to Dropbox or local storage and transfer to PC.
# 3. Save files as 1.txt, 2.txt, etc.
# 4. cat [1-3].txt |base64 -D |openssl enc -aes-256-cfb -d |tar -xzv

set -e  # Exit script if a command fails.
set -u  # Treat unset variables as errors and exit immediately.
set -o pipefail  # Exit script if pipes fail instead of just the last program.

# Handle no arguments specified.
if [[ $# -eq 0 ]]; then
    echo "Must specify relative path to files to encode."
    exit 1
fi

# Handle bad arguments.
declare -A visited
for file in "$@"; do
    if [ ${visited[$file]+true} ]; then
        echo "ERROR: file $file specified more than once."
        exit 2
    elif [ ! -e "$file" ]; then
        echo "ERROR: file $file does not exist."
        exit 2
    elif [ ! -f "$file" ]; then
        echo "ERROR: file $file is not a file."
        exit 2
    elif [ ! -r "$file" ]; then
        echo "ERROR: file $file is not readable."
        exit 2
    fi
    visited[$file]=1
done

# Generate random password 10 to 15 characters in length.
export PASSWORD=$(openssl rand -base64 25 |cut -c -$((10+RANDOM%6)))

# Remove any previously created QR codes.
rm -vf /tmp/qr*.png

# Encode.
echo -e "\x1b[1mCompressing, encrypting, and encoding $# file(s)...\x1b[0m"
tar -czv $@ |
    openssl enc -aes-256-cfb -salt -pass env:PASSWORD |
    base64 -w0 |
    qrencode -o /tmp/qr.png -Sv40
echo -e "\x1b[1mDone\x1b[0m"

# Print.
ls -l /tmp/qr*.png
echo -en "\x1b[1mPassword:\x1b[0m "
echo "$PASSWORD"
