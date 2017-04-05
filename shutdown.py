#!/usr/bin/env python3

text = 'rebooting'
num = len(text)

resp = []
resp.append('*' * (num + 6))
resp.append('== %s ==' % text.upper())
resp.append('*' * (num + 6))

print('\n'.join(resp))
exit()
