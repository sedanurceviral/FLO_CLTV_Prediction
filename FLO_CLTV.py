# Libraries
# pip install lifetimes
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter
from lifetimes.plotting import plot_period_transactions
from sklearn.preprocessing import MinMaxScaler

# Settings
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.set_option('display.width', 1000)
pd.options.mode.chained_assignment = None

# Data Collection
df_ = pd.read_csv(r'C:\Users\seda\Desktop\FLO CLTV\DATA\flo_data_20k.csv')
df = df_.copy()

# Creating a function to suppress outliers
def outlier_thresholds(dataframe, variable):
    quartile1 = dataframe[variable].quantile(0.01)
    quartile3 = dataframe[variable].quantile(0.99)
    interquantile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquantile_range
    low_limit = quartile1 - 1.5 * interquantile_range
    return low_limit, up_limit

# Replacing outliers with threshold values, rounding to integers
def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    dataframe.loc[(dataframe[variable] < low_limit), variable] = round(low_limit, 0)
    dataframe.loc[(dataframe[variable] > up_limit), variable] = round(up_limit, 0)

# Replacing outliers in the following variables: "order_num_total_ever_online", "order_num_total_ever_offline", "customer_value_total_ever_offline", "customer_value_total_ever_online"
columns = ["order_num_total_ever_online", "order_num_total_ever_offline", "customer_value_total_ever_offline",
           "customer_value_total_ever_online"]

for col in columns:
    replace_with_thresholds(df, col)
df.head()

# Creating new columns for each customer's total number of purchases and spending
df['customer_value_total'] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]
df['order_num_total'] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]

# Changing the data type of date variables from object to datetime
df.info()
date_columns = df.columns[df.columns.str.contains("date")]
df[date_columns] = df[date_columns].apply(pd.to_datetime)

# Setting the analysis date (2 days after the last purchase date)
df['last_order_date'].max()
today_date = dt.datetime(2021, 6, 1)

# Step 2: Creating a new CLTV dataframe containing customer_id, recency_cltv_weekly, T_weekly, frequency, and monetary_cltv_avg values
# The monetary value is calculated as the average value per purchase, and recency and tenure values are calculated on a weekly basis
cltv = pd.DataFrame()
cltv['customer_id'] = df["master_id"]
cltv['recency_cltv_weekly'] = (df["last_order_date"] - df["first_order_date"]).dt.days / 7
cltv['T_weekly'] = (today_date - df["first_order_date"]).dt.days / 7
cltv['frequency'] = df["order_num_total"]
cltv['monetary_cltv_avg'] = df["customer_value_total"] / df["order_num_total"]

cltv.head(10)

# Fitting the BG/NBD and Gamma-Gamma models
# Fitting the BG/NBD model
bgf = BetaGeoFitter(penalizer_coef=0.001)

bgf.fit(cltv["frequency"],
        cltv["recency_cltv_weekly"],
        cltv["T_weekly"])

# Adding expected purchases for the next 3 months as 'exp_sales_3_month'
cltv['exp_sales_3_month'] = bgf.predict(12, cltv["frequency"],
                                        cltv["recency_cltv_weekly"],
                                        cltv["T_weekly"])

# Adding expected purchases for the next 6 months as 'exp_sales_6_month'
cltv['exp_sales_6_month'] = bgf.predict(24, cltv["frequency"],
                                        cltv["recency_cltv_weekly"],
                                        cltv["T_weekly"])
cltv[['exp_sales_3_month', 'exp_sales_6_month']]

# Listing the top 10 customers with the highest prediction for 3 and 6 months
cltv.sort_values("exp_sales_3_month", ascending=False)[:10]
cltv.sort_values("exp_sales_6_month", ascending=False)[:10]

# Fitting the Gamma-Gamma model
ggf = GammaGammaFitter(penalizer_coef=0.01)
ggf.fit(cltv["frequency"], cltv["monetary_cltv_avg"])

# Predicting the average amount customers will spend and adding it to the dataframe as 'exp_average_value'
cltv['exp_average_value'] = ggf.conditional_expected_average_profit(cltv['frequency'],
                                                                    cltv['T_weekly'])

# Calculating 6-month CLTV and adding it to the dataframe
cltv['cltv'] = ggf.customer_lifetime_value(bgf,
                                           cltv['frequency'],
                                           cltv['recency_cltv_weekly'],
                                           cltv['T_weekly'],
                                           cltv['T_weekly'],
                                           time=6,
                                           freq='W',
                                           discount_rate=0.01)

# Listing the top 20 customers with the highest CLTV values
cltv.sort_values(by='cltv', ascending=False).head(20)

# Creating customer segments based on CLTV

# Dividing all customers into 4 segments based on 6-month CLTV and adding segment names to the dataframe
cltv["segment"] = pd.qcut(cltv['cltv'], 4, labels=['D', 'C', 'B', 'A'])
cltv.head(20)

# Analyzing the total CLTV for each segment to understand the expected CLTV per segment
cltv.groupby('segment').sum(numeric_only=True).sort_values(by='cltv', ascending=False).head(10)
