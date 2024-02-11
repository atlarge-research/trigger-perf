import yaml

def read_config(file):
    with open('test.yaml', 'r') as file:
        yload = yaml.safe_load(file)

    param1 = yload['rest']['url']
    print(param1)


def main():
    read_config('test.yaml')

    pass

if __name__ == "__main__":
    main()