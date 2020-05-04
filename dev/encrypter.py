import argparse
import sys
import pickle


s = ''
s += ' .,;:-!?\"\''
s += 'abcdefghijklmnopqrstuvwxyz'
s += 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
s += 'abcdefghijklmnopqrstuvwxyz'.upper()
s += 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'.upper()


def endecode(args):
    if (args.key is None) or (args.key == ''):
        print('\nНеправильный ключ')
        exit()

    if args.chiper not in ['caesar', 'vigenere', 'vernam']:
        print("\nТакого шифра не предусмотрено", end='')
        print("(используйте caesar, vigenere, vernam)")
        exit()

    # входная строка
    if (args.input_file is None or args.input_file == ""):
        try:
            input_text = sys.stdin.read()
        except KeyboardInterrupt:
            print('\nОстановка пользователем')
            exit()
    else:
        input_text = ''
        try:
            with open(args.input_file) as f:
                for line in f:
                    input_text += line
        except FileNotFoundError:
            print('\nНет такого файла')
            exit()

    k = 2 * int(args.encrypt_type == 'encode') - 1
    # если шифруем сдвигаем
    # вперед (k == +1), если дешифруем сдвигаем назад (k == -1)

    # выходная строка
    output_text = ''

    c = -1
    # шифрация/дешифрация
    for letter in input_text:

        char = letter

        if not (letter in s):
            output_text += char
            continue

        if (args.chiper == 'caesar'):
            try:
                char = s[(s.index(letter) + k * int(args.key)) % len(s)]
            except ValueError:
                print('\nКлюч в шифре Цезаря должен быть числом')
                exit()
        elif (args.chiper == 'vigenere'):
            c = (c + 1) % len(args.key)
            try:
                char = s[(s.index(letter) + k * s.index(args.key[c])) % len(s)]
            except ValueError:
                print("\nКодирование таким ключом не", end='')
                print("предусмотрено программой,", end='')
                print("используйте символы:\n\'" + s)
                exit()
        elif (args.chiper == 'vernam'):
            c = (c + 1) % len(args.key)
            try:
                char = s[s.index(letter) ^ s.index(args.key[c])]
            except ValueError:
                print("\nКодирование таким ключом не", end='')
                print("предусмотрено программой,", end='')
                print("используйте символы:\n" + s)
                exit()

        output_text += char

    # вывод
    if (args.output_file is None or args.output_file == ""):
        sys.stdout.write(output_text)
    else:
        with open(args.output_file, 'w') as f:
            f.write(output_text)
    exit()


def train(args):
    if (args.model_file == '') or (args.model_file is None):
        print('Не задано имя файла модели')
        exit()

    #  входная строка
    if (args.text_file is None or args.text_file == ""):
        try:
            input_text = sys.stdin.read()
        except KeyboardInterrupt:
            print('\nОстановка пользователем')
            exit()
    else:
        input_text = ''
        try:
            with open(args.text_file) as f:
                for line in f:
                    input_text += line
        except FileNotFoundError:
            print('\nНет такого файла')
            exit()

    #  словарь модели
    model_dict = {}  # type: dict

    #  частоты букв, которых мы не умеем (де)кодировать не повлияют на
    #  нахождение "правильного" текста, поэтому в словарь добавляем
    # только те, что знаем
    for letter in s:
        model_dict.setdefault(letter, 0)

    count = 0
    for letter in input_text:
        if (letter in s):
            count = count + 1
            model_dict[letter] = model_dict[letter] + 1

    if (count != 0):
        for key in model_dict.keys():
            model_dict[key] = float(model_dict[key] / count)

    with open(args.model_file + '.pickle', 'wb') as output_file:
        pickle.dump(model_dict, output_file)
    exit()


def hack(args):
    #  индекс совпадения строки
    def findI(string, alph):
        freq = {}  # type: dict
        for letter in alph:
            freq.setdefault(letter, 0)

        for letter in string:
            if letter in alph:
                freq[letter] = freq[letter] + 1

        summ = 0
        for letter in alph:
            summ = summ + freq[letter]*(freq[letter] - 1)
        summ = float(summ / (len(string) * (len(string) - 1)))
        return summ

    #  взаимный индекс совпадения строк
    def MI(string1, string2, alph):
        freq1 = {}  # type: dict
        freq2 = {}  # type: dict
        for letter in alph:
            freq1.setdefault(letter, 0)
            freq2.setdefault(letter, 0)

        for letter in string1:
            if letter in alph:
                freq1[letter] = freq1[letter] + 1

        for letter in string2:
            if letter in alph:
                freq2[letter] = freq2[letter] + 1

        summ = 0
        for letter in alph:
            summ = summ + freq1[letter]*freq2[letter]
        summ = float(summ / (len(string1)*len(string2)))
        return summ

    #  входная строка
    if (args.input_file is None or args.input_file == ""):
        try:
            input_text = sys.stdin.read()
        except KeyboardInterrupt:
            print('\nОстановка пользователем')
            exit()
    else:
        input_text = ''
        try:
            with open(args.input_file) as f:
                for line in f:
                    input_text += line
        except FileNotFoundError:
            print('\nНет такого файла')
            exit()

    if input_text == '':
        exit()

    mit = ''
    key_len = 0
    for letter in input_text:
        if letter in s:
            mit = mit + letter

    for t in range(1, len(mit) - 1):
        sl = []
        for j in range(0, t):
            line = ''
            for i in range(j, len(mit), t):
                line += mit[i]
            sl.append(line)

        meanI = float(0)
        for line in sl:
            meanI = meanI + findI(line, s)

        meanI = float(meanI / t)
        if meanI > 0.05:
            key_len = t
            break

    sl = []
    for j in range(0, key_len):
        line = ''
        for i in range(j, len(mit), key_len):
            line += mit[i]
        sl.append(line)

    for i in range(1, len(sl)):
        mmi = 0
        msd = 0
        for sd in range(len(s)):
            sd_s = ''
            for letter in sl[i]:
                sd_s += s[(s.index(letter) - sd) % len(s)]

            if MI(sl[0], sd_s, s) > mmi:
                mmi = MI(sl[0], sd_s, s)
                msd = sd

        sd_s = ''
        for letter in sl[i]:
            sd_s += s[(s.index(letter) - msd) % len(s)]
        sl[i] = sd_s

    mit = ''
    for i in range(max(map(len, sl))):
        for j in range(len(sl)):
            if i >= len(sl[j]):
                continue
            mit += sl[j][i]

    input_textv = ''
    count = 0
    for letter in input_text:
        if letter not in s:
            input_textv += letter
        else:
            input_textv += mit[count]
            count = count + 1

    #  выходная строка
    output_text = ''

    #  словарь с текущими значениями частот
    current_freq = {}  # type: dict

    #  словарь "правильных" частот
    with open(args.model_file + '.pickle', 'rb') as input_file:
        model_dict = pickle.load(input_file)

    for key in model_dict:
        model_dict[key] = float(model_dict[key])

    for letter in s:
        current_freq.setdefault(letter, 0)

    count = 0
    for letter in input_text:
        if letter in s:
            count = count + 1
            current_freq[letter] = current_freq[letter] + 1

    if (count != 0):
        for key in current_freq.keys():
            current_freq[key] = float(current_freq[key] / count)

    current_freqv = {}  # type: dict
    for letter in s:
        current_freqv.setdefault(letter, 0)

    count = 0
    for letter in input_textv:
        if letter in s:
            count = count + 1
            current_freqv[letter] = current_freqv[letter] + 1

    if (count != 0):
        for key in current_freqv.keys():
            current_freqv[key] = float(current_freqv[key] / count)

    m = float(len(s) + 1)
    key = 0
    b = True
    for j in range(len(s)):

        summ = float(0)
        summv = float(0)
        for k in current_freq.keys():
            summ = summ + abs(current_freq[k] - model_dict[k])
            summv = summv + abs(current_freqv[k] - model_dict[k])

        if summ < m:
            key = j
            b = True
            m = summ

        if summv < m:
            key = j
            b = False
            m = summv

        i = 0
        for k in current_freq.keys():
            if (i == 0):
                value = current_freq[k]
                valuev = current_freqv[k]
            i = i + 1
            current_freq[k] = current_freq[s[(s.index(str(k)) + 1) % len(s)]]
            current_freqv[k] = current_freqv[s[(s.index(str(k)) + 1) % len(s)]]
            if (i == len(current_freq)):
                current_freq[k] = value
                current_freqv[k] = valuev

    for i in range(len(input_text)):

        if b:
            letter = input_text[i]
        else:
            letter = input_textv[i]

        char = letter

        if letter in s:
            char = s[(s.index(letter) - key) % len(s)]

        output_text += char

    #  вывод
    if (args.output_file is None or args.output_file == ""):
        sys.stdout.write(output_text)
    else:
        with open(args.output_file, 'w') as f:
            f.write(output_text)


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='encrypt_type')

# encode
encode_parser = subparsers.add_parser('encode')
encode_parser.add_argument('--chiper', type=str)
encode_parser.add_argument('--key', type=str)
encode_parser.add_argument('--input-file', type=str)
encode_parser.add_argument('--output-file', type=str)
encode_parser.set_defaults(func=endecode)

# decode
decode_parser = subparsers.add_parser('decode')
decode_parser.add_argument('--chiper', type=str)
decode_parser.add_argument('--key', type=str)
decode_parser.add_argument('--input-file', type=str)
decode_parser.add_argument('--output-file', type=str)
decode_parser.set_defaults(func=endecode)

# train
train_parser = subparsers.add_parser('train')
train_parser.add_argument('--text-file', type=str)
train_parser.add_argument('--model-file', type=str)
train_parser.set_defaults(func=train)

# hack
hack_parser = subparsers.add_parser('hack')
hack_parser.add_argument('--input-file', type=str)
hack_parser.add_argument('--output-file', type=str)
hack_parser.add_argument('--model-file', type=str)
hack_parser.set_defaults(func=hack)

if __name__ == '__main__':
    args = parser.parse_args()
    if args.encrypt_type not in ['encode', 'decode', 'train', 'hack']:
        print("\nНеизвестная команда")
        print("Используте [<encode>, <decode>, <train>, <hack>]")
        exit()
    args.func(args)
