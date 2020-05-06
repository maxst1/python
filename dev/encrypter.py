import argparse
import sys
import pickle


alph = ''  # type: str
alph += ' .,;:-!?()'
alph += 'abcdefghijklmnopqrstuvwxyz'
alph += 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
alph += 'abcdefghijklmnopqrstuvwxyz'.upper()
alph += 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'.upper()


def find_freq(text: str, my_dict: dict) -> None:
    #  частоты букв, которых мы не умеем (де)кодировать не повлияют на
    #  нахождение "правильного" текста, поэтому в словарь добавляем
    # только те, что знаем
    count = 0  # type: int
    for letter in text:
        if letter in alph:
            my_dict[letter] = my_dict[letter] + 1
            count += 1
    if count != 0:
        for key in my_dict:
            my_dict[key] = float(my_dict[key] / count)


#  индекс совпадения строки
def findI(string: str) -> float:
    freq = set_dict()

    for letter in string:
        if letter in alph:
            freq[letter] = freq[letter] + 1

    summ = 0  # type: float
    for letter in alph:
        summ = summ + freq[letter]*(freq[letter] - 1)
    summ = float(summ / (len(string) * (len(string) - 1)))
    return summ


#  взаимный индекс совпадения строк
def MI(string1: str, string2: str) -> float:
    freq1 = set_dict()
    freq2 = set_dict()

    for letter in string1:
        if letter in alph:
            freq1[letter] = freq1[letter] + 1

    for letter in string2:
        if letter in alph:
            freq2[letter] = freq2[letter] + 1

    summ = 0  # type: float
    for letter in alph:
        summ = summ + freq1[letter]*freq2[letter]

    summ = float(summ / (len(string1)*len(string2)))
    return summ


def find_key_len(my_input_text: str) -> int:
    res = 0  # type: int
    for t in range(1, len(my_input_text) - 1):
        sl = []
        for j in range(0, t):
            line = ''
            for i in range(j, len(my_input_text), t):
                line += my_input_text[i]
            sl.append(line)

        meanI = float(0)
        for line in sl:
            meanI = meanI + findI(line)

        meanI = float(meanI / t)
        if meanI > 0.05:
            res = t
            break

    return res


def find_relative_displacement(my_input_text: str, key_len: int) -> list:
    sl = []
    for j in range(0, key_len):
        line = ''
        for i in range(j, len(my_input_text), key_len):
            line += my_input_text[i]
        sl.append(line)

    for i in range(1, len(sl)):
        max_mi = 0  # type: float
        max_sd = 0  # type: int
        for sd in range(len(alph)):
            sd_s = ''
            for letter in sl[i]:
                sd_s += alph[(alph.index(letter) - sd) % len(alph)]

            if MI(sl[0], sd_s) > max_mi:
                max_mi = MI(sl[0], sd_s)
                max_sd = sd

        sd_s = ''
        for letter in sl[i]:
            sd_s += alph[(alph.index(letter) - max_sd) % len(alph)]
        sl[i] = sd_s

    return sl


def find_txtv(input_text: str) -> str:
    # искомый текст без символов, которые мы не умеем кодировать
    my_input_text = ''
    for letter in input_text:
        if letter in alph:
            my_input_text += letter

    # находим длину ключа с помощью индекса совпадений
    key_len = find_key_len(my_input_text)

    # с помощью взаимного индекса совпадений находим относительные смещения
    # строк, и смещенные строки записываем в список sl
    sl = find_relative_displacement(my_input_text, key_len)

    # восстанавливаем текст по списку строк sl
    my_input_text = ''
    for i in range(max(map(len, sl))):
        for j in range(len(sl)):
            if i >= len(sl[j]):
                continue
            my_input_text += sl[j][i]

    # текст который не имеет относительных смещений по строкам
    # (т.е. зашифрован шифром Цезаря)
    input_textv = ''
    count = 0
    for letter in input_text:
        if letter not in alph:
            input_textv += letter
        else:
            input_textv += my_input_text[count]
            count += 1

    return input_textv


def find_summ(current_dict: dict, model_dict: dict) -> float:
    res = float(0)
    for key in current_dict:
        res += abs(current_dict[key] - model_dict[key])

    return res


def shift(cd: dict) -> None:
    # cd == current_dict
    i = 0
    for k in cd:
        if i == 0:
            value = cd[k]
        i = i + 1
        cd[k] = cd[alph[(alph.index(str(k)) + 1) % len(alph)]]
        if i == len(cd):
            cd[k] = value


def find_res_list(input_text: str, input_textv: str, model_dict: dict) -> list:
    result_key = 0
    b = True

    #  словари с текущими значениями частот
    current_freq = set_dict()
    current_freqv = set_dict()

    find_freq(input_text, current_freq)
    find_freq(input_textv, current_freqv)

    min_summ = float(len(alph) + 1)
    for key in range(len(alph)):

        #  находим различие для input_text
        summ = find_summ(current_freq, model_dict)

        #  находим различие для input_textv
        summv = find_summ(current_freqv, model_dict)

        if summ < min_summ:
            result_key = key
            b = True
            min_summ = summ

        if summv < min_summ:
            result_key = key
            b = False
            min_summ = summv

        #  вместо того, чтобы смещать сами input_text и input_textv на key
        #  мы можем просто циклически смещать значения частот в словарях их
        #  текущих частот (по сути это равносильно, так как сами значения
        #  частот не меняются при кодировании шифром Цезаря, меняется
        #  лишь то, какие символы соответствуют этим частотам)
        #  смещаем на единицу, так как нам надо, чтобы на ключе key было
        #  смещение key
        shift(current_freq)
        shift(current_freqv)

    res = []
    res.append(result_key)
    res.append(b)
    return res


def set_dict() -> dict:
    res = {}  # type: dict
    for letter in alph:
        res.setdefault(letter, 0)

    return res


def txt_out(output_text: str, output_file: str) -> None:
    if output_file is None or output_file == "":
        sys.stdout.write(output_text)
    else:
        with open(output_file, 'w') as f:
            f.write(output_text)


def txt_in(input_file: str) -> str:
    if input_file is None or input_file == "":
        try:
            input_text = sys.stdin.read()
        except KeyboardInterrupt:
            print('\nОстановка пользователем')
            exit()
    else:
        try:
            with open(input_file) as f:
                input_text = f.read()
        except FileNotFoundError:
            print('\nНет такого файла')
            exit()

    return input_text


def caesar(letter: str, key: int) -> str:
    return alph[(alph.index(letter) + key) % len(alph)]


def vernam(letter: str, key: int) -> str:
    return alph[alph.index(letter) ^ key]


def endecryption(input_text: str, args) -> str:

    # если шифруем сдвигаем
    # вперед (k == +1), если дешифруем сдвигаем назад (k == -1)
    k = 2 * int(args.encrypt_type == 'encode') - 1

    # шифрация/дешифрация
    c = -1  # type: int
    output_text = ''  # type: str
    for letter in input_text:

        char = letter

        if letter not in alph:
            output_text += char
            continue

        if args.cipher == 'caesar':
            try:
                char = caesar(letter, k * int(args.key))
            except ValueError:
                print('\nКлюч в шифре Цезаря должен быть числом')
                exit()
        elif args.cipher == 'vigenere':
            c = (c + 1) % len(args.key)
            try:
                char = caesar(letter, k * alph.index(args.key[c]))
            except ValueError:
                print("\nКодирование таким ключом не", end='')
                print("предусмотрено программой,", end='')
                print("используйте символы:\n" + alph)
                exit()
        elif args.cipher == 'vernam':
            c = (c + 1) % len(args.key)
            try:
                char = vernam(letter, alph.index(args.key[c]))
            except ValueError:
                print("\nКодирование таким ключом не", end='')
                print("предусмотрено программой,", end='')
                print("используйте символы:\n" + alph)
                exit()

        output_text += char

    return output_text


def endecode(args):
    if args.key is None or args.key == '':
        print('\nНеправильный ключ')
        exit()

    if args.cipher not in ['caesar', 'vigenere', 'vernam']:
        print("\nТакого шифра не предусмотрено", end='')
        print("(используйте caesar, vigenere, vernam)")
        exit()

    # входная строка
    input_text = txt_in(args.input_file)

    # выходная строка
    output_text = endecryption(input_text, args)

    # вывод
    txt_out(output_text, args.output_file)


def train(args):
    if args.model_file == '' or args.model_file is None:
        print('Не задано имя файла модели')
        exit()

    input_text = txt_in(args.text_file)

    model_dict = set_dict()

    find_freq(input_text, model_dict)

    with open(args.model_file + '.pickle', 'wb') as output_file:
        pickle.dump(model_dict, output_file)


def hack(args):

    #  словарь "правильных" частот
    with open(args.model_file + '.pickle', 'rb') as input_file:
        model_dict = pickle.load(input_file)

    #  входная строка
    input_text = txt_in(args.input_file)

    if input_text == '':
        exit()

    #  изначально предполагаем что input_text закодирован шифром Цезаря
    #  а для взлома шифра Вернама с помощью индексов нам понадобится версия
    #  input_textv, в которой не будет относительных смещений по длине ключа
    #  и эту версию мы сможем также взломать как и input_text с помощью
    #  гистограммы: возьмем набиольшее совпадение с гистограммой из
    #  input_text и input_textv
    input_textv = find_txtv(input_text)

    #  находим ключ с помощью гистограммы
    #  в result_list[0] будет искомый ключ
    #  в result_list[1] будет True если смещен input_text
    #  и False если смещен input_textv
    result_list = find_res_list(input_text, input_textv, model_dict)

    #  вывод
    output_text = ''
    for i in range(len(input_text)):

        if result_list[1]:
            letter = input_text[i]
        else:
            letter = input_textv[i]

        char = letter

        if letter in alph:
            char = alph[(alph.index(letter) - result_list[0]) % len(alph)]

        output_text += char
    txt_out(output_text, args.output_file)


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='encrypt_type')

# encode
encode_parser = subparsers.add_parser('encode')
encode_parser.add_argument('--cipher', type=str)
encode_parser.add_argument('--key', type=str)
encode_parser.add_argument('--input-file', type=str)
encode_parser.add_argument('--output-file', type=str)
encode_parser.set_defaults(func=endecode)

# decode
decode_parser = subparsers.add_parser('decode')
decode_parser.add_argument('--cipher', type=str)
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


def main():
    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        print("encode, decode, train, hack")


if __name__ == '__main__':
    main()
