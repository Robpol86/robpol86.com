#!/bin/sh

# https://github.com/Robpol86/robpol86.com/blob/main/docs/posts/2026/_static/btrfs-snapshot.sh
# Save as (chmod +x): /sbin/btrfs-snapshot

# Usage: btrfs-snapshot <command> [OPTIONS] [<args>]
#
# These are the available commands:
#   take        Create a read-only btrfs snapshot of the subvolume.
#   list        List all snapshots in the subvolume made with this tool.
#   restore     Clone a snapshot as read-write and make it the default subvolume.
#   delete      TODO
#   clean       TODO
#   revert      TODO
#
# Each command has its own -h. For example, see 'btrfs-snapshot take -h' for
# more information on creating snapshots.

# Usage: btrfs-snapshot take [OPTIONS] <snapshot-name>
#
# Take named btrfs snapshots with comments.
#
# Comments are Y64 encoded to make them path friendly. Snapshot names and comments
# are encoded into the snapshot directory path. An example:
#   .bsnaps/snapshots/snapshot-name/0U2luZ2xlIGxpbmUgY29tbWVudC4-
# If the snapshot is taken when the btrfs subvolume is mounted it is considered
# a "running" snapshot, and this is recorded as a 1 in the snapshot directory
# path (e.g. .bsnaps/snapshots/snapshot-name/1).
#
# Options:
#   -c comment  Snapshot description. If comment is '-' then comment will be
#               read from stdin.
#   -h          Display this help and exit.
#   -s dir      Mounted subvolume directory.
#               Default: @SUBVOLUME_DIR
#   -v          Enable verbose/debug output and don't remove temporary files.

# Usage: btrfs-snapshot list [OPTIONS]
#
# List all snapshots created by this tool in the btrfs subvolume as a table.
#
# Options:
#   -h          Display this help and exit.
#   -s dir      Mounted subvolume directory.
#               Default: @SUBVOLUME_DIR
#   -v          Enable verbose/debug output and don't remove temporary files.

# Usage: btrfs-snapshot restore [OPTIONS] <snapshot-name|snapshot-id>
#
# Restore a btrfs snapshot by its name or ID.
#
# Restore a snapshot by setting it as the default btrfs subvolume. The selected
# snapshot will be cloned as read-write, so the original remains unmodified. If
# you restore a snapshot while the system is running changes will take effect on
# the next reboot.
#
# Options:
#   -f          Do not ask the user to confirm.
#   -h          Display this help and exit.
#   -n          Treat argument as snapshot's name instead of either name or ID.
#   -s dir      Mounted subvolume directory.
#               Default: @SUBVOLUME_DIR
#   -v          Enable verbose/debug output and don't remove temporary files.

# Usage: btrfs-snapshot delete [OPTIONS] <snapshot-name|snapshot-id>
#
# TODO
#
# TODO long
#
# Options:
#   -h          Display this help and exit.
#   -s dir      Mounted subvolume directory.
#               Default: @SUBVOLUME_DIR
#   -v          Enable verbose/debug output and don't remove temporary files.

# Usage: btrfs-snapshot clean [OPTIONS] <snapshot-name|snapshot-id>
#
# TODO
#
# TODO long
#
# Options:
#   -h          Display this help and exit.
#   -s dir      Mounted subvolume directory.
#               Default: @SUBVOLUME_DIR
#   -v          Enable verbose/debug output and don't remove temporary files.

# Usage: btrfs-snapshot revert [OPTIONS]
#
# TODO
#
# TODO long
#
# Options:
#   -h          Display this help and exit.
#   -s dir      Mounted subvolume directory.
#               Default: @SUBVOLUME_DIR
#   -v          Enable verbose/debug output and don't remove temporary files.

set -o errexit  # Exit script if a command fails.
set -o nounset  # Treat unset variables as errors and exit immediately.

SUBCOMMAND=
COMMENT=
FORCE=
ID_IS_NAME=
VERBOSE=

SUBVOLUME_DIR=/  # @MODULE-SETUP-REPLACE@
TMP_DIR="${TMP_DIR:-/tmp}"
read -r UUID < "${KERNEL_UUID_FILE:-/proc/sys/kernel/random/uuid}"

# Check dependencies.
#   bash --rpm-requires ./btrfs-snapshot.sh  |sort -u |awk -F '[()]' '/^executable/{printf("%s ", $2)} END{print ""}'
#   Above command works in the Fedora Docker image.
(for cmd in awk base64 btrfs cat findmnt grep mkdir mount rm rmdir sed stat umount; do
  if ! command -v "$cmd" > /dev/null; then
    echo "ERROR: Missing command '$cmd'" >&2
    exit 1
  fi
done)

# Function that runs awk without polluting 'set -x' stderr.
# Deduplicates shared awk functions too.
# Awk program is read from input on fd3.
awk_shared() {
  awk_program_file="$TMP_DIR/bsnaps-awk_shared.$UUID.txt"
  # Write shared awk functions into file.
  cat > "$awk_program_file" <<-'EOF'
    # Trim whitespace from both ends of a string.
    function trim(str) {
      sub(/^[ \t\n]+/, "", str)
      sub(/[ \t\n]+$/, "", str)
      return str
    }
    # Filter out valid characters and return the invalid characters for snapshot names.
    function invalid_name_characters(name) {
      gsub(/[a-zA-Z0-9_ .:-]/, "", name)
      return name
    }
    # Verify if current line is a relevant snapshot line and export parsed values as global variables if so.
    function is_line_snapshot(category, id,       arr) {
      if ($1 !~ /^[0-9]+$/) return 0  # False if first column is non-numeric.
      if (id != "" && id != $1) return 0  # False if ID is specified and does not match this line.
      if ($5 !~ /^[0-9 :-]+$/) return 0  # False if otime column is invalid.
      if ($6 !~ /^[0-9a-z-]{36}$/) return 0  # False if uuid column is invalid.
      if (!match($7, /\.bsnaps\/([^/]+)\/([^/]+)\/([01])([0-9a-zA-Z._-]*)$/, arr)) return 0  # False if path is not bsnaps.
      if (category != "" && category != arr[1]) return 0  # False if category is wrong.
      # Set global variables.
      SNAPSHOT_ID = $1
      SNAPSHOT_DATE = $5
      SNAPSHOT_UUID = $6
      SNAPSHOT_NAME = arr[2]
      if (invalid_name_characters(SNAPSHOT_NAME) != "") return 0
      SNAPSHOT_RUNNING = arr[3]
      SNAPSHOT_COMMENT_ENCODED = arr[4]
      # Return true.
      return 1
    }
    # Y64 decode function.
    function y64_decode(encoded,          cmd, line, decoded, ret) {
      if (!encoded) return encoded
      # Convert Y64 to base64.
      gsub(/\./, "+", encoded)
      gsub(/_/, "/", encoded)
      gsub(/-/, "=", encoded)
      # Launch base64 decoder.
      cmd = "base64 -d"
      print encoded |& cmd
      close(cmd, "to")  # Send EOF to base64 stdin.
      # Read base64 output.
      while ((cmd |& getline line) > 0) {
        decoded = (decoded == "" ? line : decoded "\n" line)
      }
      ret = close(cmd)
      if (ret != 0) {
        printf("WARNING: Failed to decode base64 string '%s'.\n", encoded) >> "/dev/stderr"
        return encoded  # Note: returns base64 string on failed decode, not original Y64 string.
      }
      # Check for salt.
      if (substr(decoded, 1, 4) != "salt") {
        printf("WARNING: Unsalted base64 string '%s'.\n", encoded) >> "/dev/stderr"
        return encoded
      }
      return trim(substr(decoded, 5))
    }
EOF
  # Write caller's awk program into file via fd3.
  cat >> "$awk_program_file" <&3
  # Run awk.
  ret=0
  awk -f "$awk_program_file" "$@" || ret=1
  if [ ${VERBOSE:-false} = false ]; then rm -f "$awk_program_file"; fi
  return $ret
}

# Handle top level help (no args == -h).
if [ $# -eq 0 ] || [ "$1" = "-h" ]; then
  awk '
    /^# Usage:/ {doit=1}
    !/^#/ && doit==1 {exit}
    doit==1 {print substr($0, 3)}
  ' "$0"
  exit 0
fi

# Handle "--help" special case.
if [ "$1" = "--help" ]; then
  echo "unknown option: '--help'" >&2
  echo "See 'btrfs-snapshot -h'." >&2
  exit 1
fi

# Read subcommand and handle aliases.
case "$1" in
  create) SUBCOMMAND="take" ;;
  ls) SUBCOMMAND="list" ;;
  undo) SUBCOMMAND="revert" ;;
  take|list|restore|delete|clean|revert) SUBCOMMAND="$1" ;;
  *) echo "unknown subcommand: '$1'" >&2
     echo "See 'btrfs-snapshot -h'." >&2
     exit 1 ;;
esac
shift

# Parse command line arguments.
case "$SUBCOMMAND" in
  take) GETOPTS=":c:hs:v" ;;
  restore) GETOPTS=":fhns:v" ;;
  *) GETOPTS=":hs:v" ;;
esac
while getopts "$GETOPTS" OPT; do
  case "$SUBCOMMAND-$OPT" in
    *-\?)   echo "unknown flag: '$OPTARG'" >&2
            exit 1 ;;
    *-:)    echo "flag needs an argument: '$OPTARG'" >&2
            exit 1 ;;
    *-h)    awk -v SUBCOMMAND="$SUBCOMMAND" -v SUBVOLUME_DIR="$SUBVOLUME_DIR" '
              /@SUBVOLUME_DIR/ {gsub(/@SUBVOLUME_DIR/, SUBVOLUME_DIR)}
              /^# Usage:/ && $4==SUBCOMMAND {doit=1}
              !/^#/ && doit==1 {exit}
              doit==1 {print substr($0, 3)}
            ' "$0"
            exit 0 ;;
    *-s)    SUBVOLUME_DIR="$OPTARG" ;;
    *-v)    VERBOSE=true ;;
    take-c) COMMENT="$OPTARG" ;;
    restore-f) FORCE=true ;;
    restore-n) ID_IS_NAME=true ;;
    *)      echo "BUG" >&2
            exit 1 ;;
  esac
done
shift "$((OPTIND-1))"

# Enable verbose/debug.
if [ ${VERBOSE:-false} = true ]; then
  set -o xtrace  # Print commands before executing them.
fi

# Check if SUBVOLUME_DIR is a btrfs fs and subvolume.
if ! stat -f --format=%T "$SUBVOLUME_DIR" |grep -q '^btrfs$'; then
  echo "ERROR: Path '$SUBVOLUME_DIR' is not a btrfs filesystem." >&2
  exit 1
fi
if ! stat --format=%i "$SUBVOLUME_DIR" |grep -q '^256$'; then
  echo "ERROR: Path '$SUBVOLUME_DIR' is not a btrfs subvolume." >&2
  exit 1
fi

################################################################################
# Subcommand list.
################################################################################

if [ "$SUBCOMMAND" = "list" ]; then
  # Get list of snapshots.
  snapshot_list_file="$TMP_DIR/bsnaps-snapshot_list.$UUID.txt"
  if ! btrfs subvolume list -rsut "$SUBVOLUME_DIR" > "$snapshot_list_file"; then
    echo "ERROR: Failed to get list of snapshots." >&2
    echo "Are you running this as root or with sudo?" >&2
    if [ ${VERBOSE:-false} = false ]; then rm -f "$snapshot_list_file"; fi
    exit 1
  fi

  if ! awk_shared -v FS='\t+' "$snapshot_list_file" "$snapshot_list_file" 3<<'EOF'
    BEGIN {
      padding_id = 3
      padding_date = 20
      padding_running = 1
      padding_name = 15
      padding_name_max = 30
    }

    # Skip irrelevant snapshots.
    !is_line_snapshot("snapshots") { next }

    # Exit 1 if no relevant snapshots found.
    {snapshots_found++}
    ENDFILE{
      if (!snapshots_found) {
        print "No snapshots found." >> "/dev/stderr"
        exit 1
      }
    }

    # First pass.
    NR==FNR {
      # Dynamic name column.
      name_width = length(SNAPSHOT_NAME)
      if (name_width > padding_name_max) padding_name = padding_name_max
      else if (name_width > padding_name) padding_name = name_width
      next
    }

    # Print header.
    BEGINFILE {
      if (NR!=FNR) {
        printf("%-"padding_id"s  %-"padding_date-7"s %-"padding_running+7"s %-"padding_name"s  %s\n",
               "ID", "Date", "Running?", "Name", "Comment")
        hr = sprintf("%*s", 79, "-")
        gsub(/ /, "-", hr)
        print(hr)
      }
    }

    # Second pass.
    NR!=FNR {
      # Extract fields.
      running = SNAPSHOT_RUNNING ? "*" : ""
      comment = y64_decode(SNAPSHOT_COMMENT_ENCODED)
      # TODO refactor comment printing, like restore does it.

      # Print row.
      if (!comment) {
        # No comment.
        printf("%-"padding_id"s  %-"padding_date"s %-"padding_running"s %s\n",
               SNAPSHOT_ID, SNAPSHOT_DATE, running, SNAPSHOT_NAME)
      } else if (comment !~ /\n/) {
        # Single-line comment.
        printf("%-"padding_id"s  %-"padding_date"s %-"padding_running"s %-"padding_name"s  %s\n",
               SNAPSHOT_ID, SNAPSHOT_DATE, running, SNAPSHOT_NAME, comment)
      } else {
        # Multi-line comment.
        split(comment, arr, "\n")
        printf("%-"padding_id"s  %-"padding_date"s %-"padding_running"s %-"padding_name"s  %s\n",
               SNAPSHOT_ID, SNAPSHOT_DATE, running, SNAPSHOT_NAME, arr[1])
        for (i=2; i<=length(arr); i++) {
          printf("%*s", padding_id+padding_date+padding_running+padding_name+6, "")
          print arr[i]
        }
      }
    }
EOF
  then
    if [ ${VERBOSE:-false} = false ]; then rm -f "$snapshot_list_file"; fi
    exit 1
  fi
  if [ ${VERBOSE:-false} = false ]; then rm -f "$snapshot_list_file"; fi

  exit 0
fi

################################################################################
# Subcommand take.
################################################################################

if [ "$SUBCOMMAND" = "take" ]; then
  # Parse subcommand arguments.
  if [ $# != 1 ]; then
    echo "'btrfs-snapshot take' requires exactly 1 argument." >&2
    echo "See 'btrfs-snapshot take -h'." >&2
    exit 1
  fi
  snapshot_name="$1"
  shift

  # Check if snapshot name has invalid characters.
  if [ -z "$snapshot_name" ]; then
    echo "ERROR: Snapshot name is empty." >&2
    exit 1
  fi
  awk_shared -v snapshot_name="$snapshot_name" /dev/null 3<<'EOF'
      END {
        chars = invalid_name_characters(snapshot_name)
        if (chars == "") exit 0
        s = length(chars) == 1 ? "" : "s"
        printf("ERROR: Invalid snapshot name character%s '%s'.\n", s, chars) >> "/dev/stderr"
        exit 1
      }
EOF

  # Encode comment.
  y64_encode() {
    { printf salt; cat; } |base64 -w0 |sed -e 's/+/./g' -e 's|/|_|g' -e 's/=/-/g'
  }
  if [ "${COMMENT:-}" = "-" ]; then
    if [ -t 0 ]; then
      echo "Press Ctrl+D to finish" >&2
    fi
    comment_b64="$(y64_encode)"
  elif [ -n "${COMMENT:-}" ]; then
    comment_b64="$(printf "%s" "$COMMENT" |y64_encode)"
  else
    comment_b64=
  fi
  # TODO if name+comment > limit: fail. (reproduce with just a long comment)

  # Determine snapshot path.
  snapshot_path_mkdir="${SUBVOLUME_DIR%/}/.bsnaps/snapshots/$snapshot_name"
  if findmnt -O ro "$SUBVOLUME_DIR" > /dev/null; then
    is_readonly=true
    snapshot_path="$snapshot_path_mkdir/0$comment_b64"
  else
    is_readonly=
    snapshot_path="$snapshot_path_mkdir/1$comment_b64"
  fi

  # Fail if snapshot already exists.
  if [ -e "$snapshot_path" ]; then
    echo "ERROR: Snapshot '$snapshot_path' already exists." >&2
    echo "Run 'btrfs-snapshot list' to list existing snapshots." >&2
    exit 1
  fi

  # Remount subvolume as readwrite if it is mounted as readonly.
  if [ ${is_readonly:-false} = true ]; then
    if ! mount -oremount,rw "$SUBVOLUME_DIR"; then
      echo "ERROR: Failed to remount '$SUBVOLUME_DIR' as read-write." >&2
      echo "Are you running this as root or with sudo?" >&2
      exit 1
    fi
    echo "Remounted '$SUBVOLUME_DIR' as read-write"
  fi

  # Create snapshots parent directories.
  if ! mkdir -p "$snapshot_path_mkdir"; then
    echo "ERROR: Failed to create directory '$snapshot_path_mkdir'." >&2
    echo "Are you running this as root or with sudo?" >&2
    exit 1
  fi

  # Create snapshot
  btrfs subvolume snapshot -r "$SUBVOLUME_DIR" "$snapshot_path"

  # Remount subvolume as readonly if it was originally in that state.
  if [ ${is_readonly:-false} = true ]; then
    mount -oremount,ro "$SUBVOLUME_DIR"
    echo "Remounted '$SUBVOLUME_DIR' as read-only"
  fi

  exit 0
fi

################################################################################
# Subcommand restore.
################################################################################

if [ "$SUBCOMMAND" = "restore" ]; then
  # Parse subcommand arguments.
  if [ $# != 1 ]; then
    echo "'btrfs-snapshot $SUBCOMMAND' requires exactly 1 argument." >&2
    echo "See 'btrfs-snapshot $SUBCOMMAND -h'." >&2
    exit 1
  fi

  # Get list of snapshots.
  snapshot_list_file="$TMP_DIR/bsnaps-snapshot_list.$UUID.txt"
  if ! btrfs subvolume list -rsut "$SUBVOLUME_DIR" > "$snapshot_list_file"; then
    echo "ERROR: Failed to get list of snapshots." >&2
    echo "Are you running this as root or with sudo?" >&2
    if [ ${VERBOSE:-false} = false ]; then rm -f "$snapshot_list_file"; fi
    exit 1
  fi

  # Parse btrfs list command output.
  subvolume_device="$(findmnt -nvo SOURCE "$SUBVOLUME_DIR")"
  IFS="$(printf '\t')" read -r snapshot_id snapshot_date snapshot_uuid snapshot_name snapshot_running snapshot_has_comment <<EOREAD
$(awk_shared -v FS='\t+' -v ID="$1" -v ID_IS_NAME="$ID_IS_NAME" "$snapshot_list_file" 3<<'EOF'
      function record_result() {
        result = sprintf("%d\t%s\t%s\t%s\t%s\t%s\n",
          SNAPSHOT_ID, SNAPSHOT_DATE, SNAPSHOT_UUID, SNAPSHOT_NAME,
          SNAPSHOT_RUNNING ? "Yes" : "No",
          SNAPSHOT_COMMENT_ENCODED ? "true" : "")
      }
      !is_line_snapshot("snapshots") { next }
      !ID_IS_NAME && ID==SNAPSHOT_ID { record_result(); exit }  # ID: first wins.
      ID==SNAPSHOT_NAME { record_result() }  # Name: last wins.
      END { if (result) printf(result) }  # Print if either matched.
EOF
    )
EOREAD
  if [ -z "$snapshot_id" ]; then
    echo "ERROR: Cannot find btrfs snapshot name or ID '$1'." >&2
    echo "Run 'btrfs-snapshot list' to list existing snapshots." >&2
    if [ ${VERBOSE:-false} = false ]; then rm -f "$snapshot_list_file"; fi
    exit 1
  fi

  # Prompt user before making changes
  echo "Restoring snapshot ID $snapshot_id:" >&2
  echo "-------------------------------------------------------------------------------" >&2
  echo "Subvolume:  $SUBVOLUME_DIR"
  echo "Device:     $subvolume_device"
  echo "Name:       $snapshot_name"
  echo "UUID:       $snapshot_uuid"
  echo "Date:       $snapshot_date"
  echo "Running:    $snapshot_running"
  if [ -n "$snapshot_has_comment" ]; then
    printf "Comment:    "
    awk_shared -v FS='\t+' -v ID="$snapshot_id" -v PREFIX="            " "$snapshot_list_file" 3<<'EOF'
      is_line_snapshot("snapshots", ID) {
        comment = y64_decode(SNAPSHOT_COMMENT_ENCODED)
        split(comment, lines, "\n")
        for (idx in lines) print(idx == 1 ? lines[idx] : PREFIX lines[idx])
        exit
      }
EOF
  else
    echo "Comment:"
  fi
  echo "-------------------------------------------------------------------------------" >&2
  if [ ${VERBOSE:-false} = false ]; then rm -f "$snapshot_list_file"; fi
  if [ ${FORCE:-false} = false ]; then
    echo "Press enter to continue..." >&2
    read -r _
  fi

  # Mount the snapshot as read-only.
  dir_restore_from="$TMP_DIR/.bsnaps/$snapshot_name-ro"
  if [ -e "$dir_restore_from" ]; then dir_restore_from="$dir_restore_from-$UUID"; fi
  mkdir -p "$dir_restore_from"
  mount -o "subvolid=$snapshot_id,ro" "$subvolume_device" "$dir_restore_from"
  echo "Mounted snapshot '$snapshot_name' as read-only"

  # Restored snapshots will live in subvolid=5 to prevent PATH_MAX issues with nested snapshots.
  dir_subvolid5="$TMP_DIR/.bsnaps/subvolid5"
  if [ -e "$dir_subvolid5" ]; then dir_subvolid5="$dir_subvolid5-$UUID"; fi
  mkdir -p "$dir_subvolid5"
  mount -o "subvolid=5,rw" "$subvolume_device" "$dir_subvolid5"
  echo "Mounted btrfs subvolid=5 as read-write"

  # Clone the snapshot as read-write and set-default it.
  dir_restore_to="$dir_subvolid5/.bsnaps/restored/$snapshot_name"
  mkdir -p "$dir_subvolid5/.bsnaps/restored"
  if [ -e "$dir_restore_to" ]; then dir_restore_to="$dir_restore_to-$UUID"; fi
  btrfs subvolume snapshot "$dir_restore_from" "$dir_restore_to"
  btrfs subvolume set-default "$dir_restore_to"  # TODO what about distros that hard-code volid in fstab?
  umount "$dir_subvolid5"
  echo "Unmounted read-write btrfs subvolid=5"
  umount "$dir_restore_from"
  echo "Unmounted read-only '$snapshot_name'"
  rmdir --ignore-fail-on-non-empty "$dir_restore_from" "$dir_subvolid5"

  # Remount $SUBVOLUME_DIR using the now-restored set-default subvolume.
  if findmnt -O ro "$SUBVOLUME_DIR" > /dev/null; then
    umount "$SUBVOLUME_DIR"
    mount -oro "$subvolume_device" "$SUBVOLUME_DIR"
    echo "Remounted '$SUBVOLUME_DIR' using snapshot '$snapshot_name' as read-only"
    echo "Changes are now in effect"
  else
    echo "Reboot for changes to take effect"
  fi

  exit 0
fi

################################################################################
# Subcommand delete.
################################################################################

if [ "$SUBCOMMAND" = "delete" ]; then
  echo "TODO"
  exit 0
fi

################################################################################
# Subcommand clean.
################################################################################

if [ "$SUBCOMMAND" = "clean" ]; then
  echo "TODO"
  exit 0
fi

################################################################################
# Subcommand revert.
################################################################################

if [ "$SUBCOMMAND" = "revert" ]; then
  echo "TODO"
  exit 0
fi

echo "BUG" >&2
exit 1

# TODO:
# - Prune old/irrelevant TODOs.
# - Write integration_tests with .img file in CI.
#   - See Claude conversation: Btrfs filesystem setup in GitHub Actions
#   - List create restore delete etc.
#   - Multiple docker images for diff supported distros. Ensures btrfs command consistency testing.
# - Consistent `sudo btrfs subvol list / -tsr` with/without reboot after restore in rd.break.
# - base64 security: filter out non a-z?
# - Tell user which snapshot they're running from with restore file.
#   - When restoring, create file that says "restored from ID". Then bss list reads that file and adds a note below said snap
#   - Maybe instead, bring back snapshot.nfo. Before taking snapshot write its name into that file.
# - umask at beginning of script so all tmp txt files are 600 owned by root.
# - test restore UUID collision fallbacks.
# TODO:
# - Consistent punctuation in echos.
# - Test non-root error messages for all subcommands.
# - Test with LC_ALL=C and other values.
# - @root and @home: can snapshots live in other subvols? Probably not.
# - Support non-root (arbitrary) subvolumes
# - Test with subvol_dir=.
# - Checks:
#   - if snapshots-dir has a leading / is it the same as subvolume?
#     - subv=/my/sub/vol/ume; snapshots-dir=/snap/shots == /my/sub/vol/ume/snap/shots
# - Replace grep/sed/etc with awk.
# - Integration tests for take+restore interaction (tests/integration_tests/test_snapshot_take_restore.py)
# - Optimize: drop Dracut dependencies for POSIX shell tricks
# - Test different locales, does btrfs and other command outputs change (e.g. btrfs subv l otime timestamp)
# - Reformat ubuntu and test all subcommands with no snapshots.
# - Go through usage/comments to ensure nothing is stale.
# - Dumb down awk to work with mawk/busybox awk.
# - Fix double slash when subvol is / in non-rd.break: "Create snapshot of '//.bsnaps/restored/ro-multiSnap'"
# - Bad comment: user specifyfies -c-, but then presses ctrl+d with no other text. Should count has no-comment.
#   - Same with -c ""
# TODO revert:
# - After restore, print 'Run "..." to revert.'
# - Every [restore] takes a read only snapshot into bsnaps/revert.
# - But how do i keep track of last revert? Ideal: revert, boot, revert, boot. Like cd ../.. keep going back without deleting
# - [restore] cli flag to not save revert snapshot.
# - [list] cli flag to include restore/revert snapshots. What happens if i restore a restore/revert?
#   - Maybe list restore/revert snapshots in [clean] instead?
# TODO delete:
# - Use more ominous @@@@@ hr.
# - Confirm subvolid is not mounted before delete.
# TODO clean:
# - Remove unmounted "restored" subvolumes.
