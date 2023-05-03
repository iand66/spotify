import os

def cleanup():
    for root, dir, files  in os.walk('.', topdown=True):
        for file in files:
            if not file.isascii():
                os.rename(os.path.join(root, file), os.path.join(root, file).encode('ascii',errors='ignore'))


if __name__ == "__main__":
    cleanup()