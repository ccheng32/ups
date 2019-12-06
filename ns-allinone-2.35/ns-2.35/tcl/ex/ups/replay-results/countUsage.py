import sys

if __name__ == "__main__":

    count = [0,0,0,0,0,0,0,0]

    with open(sys.argv[1],'r') as f:
        for line in f.readlines():
            count[int(line)-1] += 1

    print(count)
