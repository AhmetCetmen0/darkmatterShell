import hashlib
import random
import time
import sys


# Orijinal karakter seti
BASE_ALPHABET = [
    "a", "b", "c", "ç", "d", "e", "f", "g", "ğ", "h", "ı", "i", "j", "k", "l", "m", "n", "o", "ö", "p", "q", "r", "s", "ş", "t", "u", "ü", "v", "w", "x", "y", "z",
    "A", "B", "C", "Ç", "D", "E", "F", "G", "Ğ", "H", "I", "İ", "J", "K", "L", "M", "N", "O", "Ö", "P", "Q", "R", "S", "Ş", "T", "U", "Ü", "V", "W", "X", "Y", "Z",
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    " ", ".", ",", "!", "?", "@", "*", "#", "$", "%", "&", "(", ")", "-", "_", "=", "+", "{", "}", "[", "]", "|", "\\", "/", ":", ";", "'", "\"", "<", ">", "~", "^", "`"
]

def get_shuffled_alphabet(password):
    # Password'tan SHA256 hash al
    sha = hashlib.sha256()
    sha.update(password.encode('utf-8'))
    hash_value = sha.digest()

    # Hash'ın ilk 4 byte'ını uint seed'e çevir
    seed = int.from_bytes(hash_value[:4], 'big')

    # Fisher-Yates shuffle
    alphabet = BASE_ALPHABET[:]
    rng = random.Random(seed)
    n = len(alphabet)

    while n > 1:
        k = rng.randint(0, n - 1)
        # swap alphabet[k] ve alphabet[n-1]
        alphabet[n-1], alphabet[k] = alphabet[k], alphabet[n-1]
        n -= 1

    return alphabet

def encrypt(data, password):
    shuffled_alphabet = get_shuffled_alphabet(password)

    # Veriyi sayılara dönüştür
    data_int = []
    for char in data:
        try:
            index = shuffled_alphabet.index(char)
            data_int.append(index)
        except ValueError:
            print(f"Error: '{char}' character not found in the alphabet.")
            return

    # Zaman bilgisi
    current_time = time.gmtime()
    sec = current_time.tm_sec
    min = current_time.tm_min
    hour = current_time.tm_hour
    year = current_time.tm_year
    crypting_param = (sec * min * year + hour)

    # Şifreleme parametreleriyle işlemi yap
    for i in range(len(data_int)):
        data_int[i] = (data_int[i] + 1) * crypting_param

    # Veriyi böl
    segments = [str(num) for num in data_int]
    time_data = [str(sec), str(min), str(hour), str(year)]

    # Veriyi şifreli hale getir
    if len(segments) < 9:
        segments.extend(time_data)
    else:
        segments.insert(8, time_data[3])
        segments.insert(6, time_data[1])
        segments.insert(3, time_data[0])
        segments.insert(1, time_data[2])

    final_encrypted = ",".join(segments)
    print(f"Encrypted Data: \n{final_encrypted}")
    with open("output.txt", "w") as f:
        f.write(final_encrypted)

def decrypt(data, password):
    shuffled_alphabet = get_shuffled_alphabet(password)

    segments = data.split(",")
    if len(segments) < 11:
        sec = int(segments[-4])
        min = int(segments[-3])
        hour = int(segments[-2])
        year = int(segments[-1])
        segments = segments[:-4]
    else:
        sec = int(segments[4])
        min = int(segments[8])
        hour = int(segments[1])
        year = int(segments[11])

        segments = [segment for i, segment in enumerate(segments) if i not in [4, 8, 11, 1]]

    crypting_param = (sec * min * year + hour)

    # Şifreyi çöz
    original_data = []
    for segment in segments:
        encrypted_value = int(segment)
        original_index = (encrypted_value // crypting_param) - 1

        if encrypted_value % crypting_param != 0:
            print(f"Warning: The value {encrypted_value} wasn't perfectly divisible.")

        if 0 <= original_index < len(shuffled_alphabet):
            original_data.append(shuffled_alphabet[original_index])
        else:
            print(f"Error: Invalid index {original_index}.")

    decrypted_text = ''.join(original_data)
    print(f"Decrypted Data: \n{decrypted_text}")
    with open("decrypted_output.txt", "w") as f:
        f.write(decrypted_text)

def show_help():
    print("Usage:")
    print("  -e <data> <password>    Encrypt the given data with the provided password.")
    print("  -d <data> <password>    Decrypt the given data with the provided password.")
    print("  -h                      Show this help message.")

if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] == "-h":
        show_help()
    elif len(sys.argv) != 4:
        print("Error: Incorrect number of arguments.")
        show_help()
    else:
        operation = sys.argv[1]
        data = sys.argv[2]
        password = sys.argv[3]

        if operation == "-e":
            encrypt(data, password)
        elif operation == "-d":
            decrypt(data, password)
        else:
            print("Error: Invalid operation. Use -e for encrypt or -d for decrypt.")
