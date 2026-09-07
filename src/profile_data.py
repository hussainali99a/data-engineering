import pandas as pd

data = pd.read_csv("D:\\taxi-data-engineering\\data\\ncr_ride_bookings.csv")

print("\n=====DATASET SHAPE=========")
print(data.shape)


print("\n=====COLUMNS=========")
print(data.columns.tolist())


print("\n=====DATA TYPES=========")
print(data.dtypes)



print("\n=====FIRST  5 ROWS=========")
print(data.head(5))



print("\n=====MISSING VALUES=========")
print(data.isnull().sum())

print("\n===== DUPLICATE ROWS =====")
print(data.duplicated().sum())

print("\n===== BASIC STATISTICS =====")
print(data.describe(include="all"))