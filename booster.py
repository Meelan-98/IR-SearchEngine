def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def boost_field(phrase):

    boost_array = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,1]

    if (isEnglish(phrase)):
        for field in range(0,4):
            boost_array[field] = 2
    else:
        for field in range(4,13):
            boost_array[field] = 2

    print(boost_array)

    return boost_array
