#!/usr/bin/env bash
set -eu
MODE="${1:-order}"
PKG="${2:-bash}"
D="${TMPDIR:-/tmp}/depgraph-apt"

mkdir -p "$D/lists/partial" "$D/cache/archives/partial" "$D/sources.d" "$D/prefs.d"
echo "deb [trusted=yes arch=amd64] http://archive.ubuntu.com/ubuntu noble main" \
    > "$D/sources.list"
: > "$D/status"
cat > "$D/apt.conf" <<CONF
Dir::Etc::sourcelist "$D/sources.list";
Dir::Etc::sourceparts "$D/sources.d";
Dir::Etc::preferencesparts "$D/prefs.d";
Dir::State::Lists "$D/lists";
Dir::State::status "$D/status";
Dir::Cache "$D/cache";
Debug::NoLocking "1";
APT::Architecture "amd64";
APT::Architectures { "amd64"; };
Acquire::Languages "none";
CONF
export APT_CONFIG="$D/apt.conf"
apt-get update -qq >/dev/null 2>&1 || true

case "$MODE" in
    order)
        apt-get install -s --no-install-recommends "$PKG" \
            | awk '/^Inst /{print ++n". "$2}'
        ;;
    depends)
        apt-cache depends --recurse --no-recommends --no-suggests \
            --no-conflicts --no-breaks --no-replaces --no-enhances "$PKG"
        ;;
    dotty)
        apt-cache dotty "$PKG"
        ;;
    *)
        echo "usage: $0 order|depends|dotty PACKAGE" >&2
        exit 2
        ;;
esac
