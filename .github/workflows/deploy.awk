function error(msg) {
  print(msg) > "/dev/stderr"
  exit 1
}

function setOutput(name, value) {
  printf("Set Output: %s=%s\n", name, value)
  printf("::set-output name=%s::%s\n", name, value)
}
