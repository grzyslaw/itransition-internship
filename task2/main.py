import glob
import hashlib

def hash_files():
    files = glob.glob('./files/*')
    hashes = []
    for file in files:
        with open(file,'rb') as f:
            bin = f.read()
            digest = hashlib.sha3_256(bin).hexdigest()
            hashes.append(digest)
    return hashes

def get_sort_key(hash):
    product = 1
    for ch in hash:
        value = int(ch,16)
        product *= (value + 1)
    return product

def sort_and_join_hashes(hashes):
    hashes = sorted(hashes, key=get_sort_key)
    joined_hashes = "".join(hashes) + 'choruzy.g@gmail.com'
    result = hashlib.sha3_256(joined_hashes.encode('utf-8')).hexdigest()
    print(result)
    
hashes = hash_files()
sort_and_join_hashes(hashes)
    

