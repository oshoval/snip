# Snip

```
# snip snip test
dnf config-manager \
    --add-repo \
    https://download.docker.com/linux/fedora/docker-ce.repo
dnf install -y docker-ce docker-ce-cli containerd.io
sudo groupadd docker
sudo usermod -aG docker $(whoami)
sudo service docker start
```

```
# snip snip hello
echo hello world
```
