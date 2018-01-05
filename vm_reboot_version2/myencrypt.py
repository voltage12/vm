def encrypt(key, s):
    try:
        b = bytearray(s)
        n = len(b)
        c = bytearray(n * 2)
        j = 0
        for i in range(0, n):
            b1 = b[i]
            b2 = b1 ^ key
            c1 = b2 % 16
            c2 = b2 // 16
            c1 = c1 + 65
            c2 = c2 + 65
            c[j] = c1
            c[j + 1] = c2
            j = j + 2
        return c
    except:
        return None

def decrypt(key, s):
    try:
        c = bytearray(s)
        n = len(c)
        if n % 2 != 0:
            return None
        n = n // 2
        b = bytearray(n)
        j = 0
        for i in range(0, n):
            c1 = c[j]
            c2 = c[j+1]
            j = j + 2
            c1 = c1 - 65
            c2 = c2 - 65
            b2 = c2 * 16 + c1
            b1 = b2 ^ key
            b[i] = b1
        return b
    except:
        return None


def generate_key(ipaddr_bytes, time_str_bytes):
    return (ipaddr_bytes[0] + ipaddr_bytes[-1] + time_str_bytes[0] + time_str_bytes[-1]) % 256
