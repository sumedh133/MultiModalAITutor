import hashlib

def get_file_hash(file):
    return hashlib.md5(file.getvalue()).hexdigest()