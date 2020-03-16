from functools import reduce
from operator import mul

def find_fold_number(n):
    return 1 + find_fold_number(reduce(mul, [int(d) for d in str(n)])) if n >= 10 else 0

def rle(string):
    cnt = 1
    string += '$'
    ans = ''
    a = string[0]
    for i in range(1, len(string)):
        if string[i] == a:
            cnt += 1
        else:
            if cnt == 1:
                ans += a
            else:
                ans += a + str(cnt)
            a = string[i]
            cnt = 1
    return ans

test_rle_str = 'ffffbbbbbbbbbbbbbsssssssssssssgggggggggggggggeeeeeeeeeeeellllllllllllllllllooooooooooooffffiiiiiirrrrrrrrrrrrrruuuuuuuummmmmiiiiiiiiiiiiiiiqqqxxxxxxxxxxxxxxxxxzzzzzzwwwwzzzzzzzzzzzzzzzzzzzoooooookkkkkkkkkkiiiiiiiiiiiiiiiizzzzzzzzzzzzzzzzhhhhhhhooooooooooccccccccccccccrrrrrrrkkkxxxxxxxxxxxxxxxxxkkssssssssmcccdddddddddddppppppppppppppnnnnnnnnnnnnnnssssssssssssbbbbbraaaaaasjjjjjjjjjjkkkkkkkkkrrrrrrrrryyyyyyyyyyyyaaaaaaaaaaauuuuuuuuuuuuwwwwwwwwwwgggggggglllllllllvvvvvvvvvvvbbgggggggggggggggqqqqqqlllllllllllllllxxxxxxxxxxaaaaaeeeeeeeeeeeeevvvvvvvvvvvvvdddddddddddpccccddddddddddddddddpppppppppppppppssssssssssssddddddddddddddddddzzzzzzzzzzzzzzzzzzzaaaaaaaaaaaaaaaaaaabfffffffffkkkkkxxxxxwwwwwhhhhhhhhhhhhtttttttttrrrrrrrrrrrrrrrrrroooooooooooooooooooccccccccccccccccppphhhhhhhhhhhhuuuuuurrrrrrrrrrrrrrrrrrryyyyyyyyyyyyyyyyyjjjjjjjjjjjjjjjjjjjjjjjjgggaaaxxxxxxxxxxxlllllllluuuuuuuuuummmmmmmmmmffffffmmmmmmmmmmmmmmmmmmggggggggggggggtttjjjjjjjjjjjjjjjjjjj'
