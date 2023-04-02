function error(msg) {
  print(msg) > "/dev/stderr"
  exit 1
}

function setOutput(name, value) {
  printf("Set Output: %s=%s\n", name, value)
  printf("%s=%s\n", name, value) >> GITHUB_OUTPUT
}
