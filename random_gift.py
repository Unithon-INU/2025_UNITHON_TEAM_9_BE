import pandas as pd
import random

with open('data.csv') as file:
    tels = file.read().split('\n')

print(random.choice(tels))
