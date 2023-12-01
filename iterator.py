import pandas as pd
   
# проход по данным
def next_data(df: pd.DataFrame, index: int) -> tuple[str]:
    if index < len(df):
        return tuple(df.iloc[index]) #возвращает строки по целочисленным значениям
    return None

# Итератор
class Iterator:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.counter = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.counter < len(self.df):
            result = tuple(self.df.iloc[self.counter])
            self.counter += 1
            return result
        else:
            raise StopIteration    