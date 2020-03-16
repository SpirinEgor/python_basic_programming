from functools import reduce
from operator import mul
import numpy as np

def find_fold_number(n):
    if (n < 0):
        return find_fold_number(-n)
    if (n < 10):
        return 0
    newN = np.prod([int(c) for c in str(n)])
    return find_fold_number(newN) + 1

def rle(string):
    ans = ''
    cur = ''
    cou = 0
    for i in range(len(string)):
        if (i == 0):
            cur = string[i]
            cou = 1
            continue
        if (cur == string[i]):
            cou += 1
        else:
            ans += cur
            if (cou > 1):
                ans += str(cou)
            cou = 1
            cur = string[i]
    ans += cur
    if (cou > 1):
        ans += str(cou)
    return ans

test_rle_str = 'ffffbbbbbbbbbbbbbsssssssssssssgggggggggggggggeeeeeeeeeeeellllllllllllllllllooooooooooooffffiiiiiirrrrrrrrrrrrrruuuuuuuummmmmiiiiiiiiiiiiiiiqqqxxxxxxxxxxxxxxxxxzzzzzzwwwwzzzzzzzzzzzzzzzzzzzoooooookkkkkkkkkkiiiiiiiiiiiiiiiizzzzzzzzzzzzzzzzhhhhhhhooooooooooccccccccccccccrrrrrrrkkkxxxxxxxxxxxxxxxxxkkssssssssmcccdddddddddddppppppppppppppnnnnnnnnnnnnnnssssssssssssbbbbbraaaaaasjjjjjjjjjjkkkkkkkkkrrrrrrrrryyyyyyyyyyyyaaaaaaaaaaauuuuuuuuuuuuwwwwwwwwwwgggggggglllllllllvvvvvvvvvvvbbgggggggggggggggqqqqqqlllllllllllllllxxxxxxxxxxaaaaaeeeeeeeeeeeeevvvvvvvvvvvvvdddddddddddpccccddddddddddddddddpppppppppppppppssssssssssssddddddddddddddddddzzzzzzzzzzzzzzzzzzzaaaaaaaaaaaaaaaaaaabfffffffffkkkkkxxxxxwwwwwhhhhhhhhhhhhtttttttttrrrrrrrrrrrrrrrrrroooooooooooooooooooccccccccccccccccppphhhhhhhhhhhhuuuuuurrrrrrrrrrrrrrrrrrryyyyyyyyyyyyyyyyyjjjjjjjjjjjjjjjjjjjjjjjjgggaaaxxxxxxxxxxxlllllllluuuuuuuuuummmmmmmmmmffffffmmmmmmmmmmmmmmmmmmggggggggggggggtttjjjjjjjjjjjjjjjjjjj'
