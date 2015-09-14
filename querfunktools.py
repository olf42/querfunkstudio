#!/usr/bin/env python3

from hashlib import sha512

def encrypt_pw(pw):
    return sha512(pw.encode("utf-8")).hexdigest()

