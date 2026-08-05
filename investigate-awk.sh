#!/bin/sh

echo "VGhpcyBpcyB0aGUgc3RyaW5nLg==" |awk '
  function y64_decode(encoded) {
    gsub(/\./, "+", encoded)
    gsub(/_/, "/", encoded)
    gsub(/-/, "=", encoded)
    # https://dnshane.wordpress.com/2017/03/10/decoding-base64-in-awk/
    # https://github.com/shane-kerr/AWK-base64decode
    # Initialize base64 decoder.
    for (i=0; i<26; i++) { BASE64[sprintf("%c", i+65)] = i; BASE64[sprintf("%c", i+97)] = i+26 }
    for (i=0; i<10; i++) BASE64[sprintf("%c", i+48)] = i+52
    BASE64["+"] = 62; BASE64["/"] = 63; BASE64["="] = -1
    result[1]=""
    n = 1
    # Decode base64.
    while (length(encoded) >= 4) {
      g0 = BASE64[substr(encoded, 1, 1)]
      g1 = BASE64[substr(encoded, 2, 1)]
      g2 = BASE64[substr(encoded, 3, 1)]
      g3 = BASE64[substr(encoded, 4, 1)]
      if (g0 == "") {
        printf("Unrecognized character %c in Base 64 encoded string\n", g0) >> "/dev/stderr"
        exit 1
      }
      if (g1 == "") {
        printf("Unrecognized character %c in Base 64 encoded string\n", g1) >> "/dev/stderr"
        exit 1
      }
      if (g2 == "") {
        printf("Unrecognized character %c in Base 64 encoded string\n", g2) >> "/dev/stderr"
        exit 1
      }
      if (g3 == "") {
        printf("Unrecognized character %c in Base 64 encoded string\n", g3) >> "/dev/stderr"
        exit 1
      }
      result[n++] = (g0 * 4) + int(g1 / 16)
      if (g2 != -1) {
        result[n++] = ((g1 * 16) % 256) + int(g2 / 4)
        if (g3 != -1) result[n++] = ((g2 * 64) % 256) + g3
      }
      encoded = substr(encoded, 5)
    }
    # Concat result array.
    decoded = ""
    for (i=1; i in result; i++) {
      decoded = decoded sprintf("%c", result[i])
      delete result[i]
    }
    return decoded
  }
  {
    print(y64_decode($0))
  }
'
