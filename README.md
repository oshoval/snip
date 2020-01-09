+This script will install the latest accepted snip release. \
Snip purpose is to allow a quick method to integrate between markdown snippets and cli.

## Snippets for sanity check

```
# snip main first
echo first
```

```
# snip main hello
echo "hello world"
```

## Some useful snippets

```
# snip main bye
echo bye
```

## Start using Snip tool
general format:
```
./snip.py [<url>|<local-file>|<shortcut>] <cmd> <options>
```

### Commands supported:
ls: show snippets on screen with their enumeration

1,2,...: executes the enumerated snip #

### Options supported:
[--dry / -d]: only prints to screen without executing it.

[-m / --modify]: opens vi editor, after closing saved text is executed

### Using url (in raw format)

```
./snip.py https://gitlab.cee.redhat.com/redsamurai/snippets/raw/master/modi.md ls
```

### Using local file

```
./snip.py <full-path>/modi.md ls
```

### Using shortcuts defined in inventory.ini

```
./snip.py main ls
```