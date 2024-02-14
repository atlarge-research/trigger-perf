import yaml
import random

def read_config(file):
    with open('config.yaml', 'r') as file:
        yload = yaml.safe_load(file)

    param1 = yload['rest']['url']
    print(param1)

def generate_rand_bytes(size):
    return str(bytes(random.choices(range(256), k=size)))


def main():
    read_config('test.yaml')

    pass

if __name__ == "__main__":
    main()