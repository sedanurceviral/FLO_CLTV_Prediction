# Kütüphaneler
# pip install lifetimes
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter
from lifetimes.plotting import plot_period_transactions
from sklearn.preprocessing import MinMaxScaler

# Ayarlar
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.set_option('display.width', 1000)
pd.options.mode.chained_assignment = None

# Verinin Çekilmesi
df_ = pd.read_csv(r'C:\Users\seda\Desktop\FLO CLTV\DATA\flo_data_20k.csv')
df = df_.copy()


# Aykırı değerleri baskılamak için fonksiyon oluşturuyoruz
def outlier_thresholds(dataframe, variable):
    quartile1 = dataframe[variable].quantile(0.01)
    quartile3 = dataframe[variable].quantile(0.99)
    interquantile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquantile_range
    low_limit = quartile1 - 1.5 * interquantile_range
    return low_limit, up_limit


# Aykırı değerlerin yerine yerleştireceğimiz değerlerde integar sonuç elde etmek için round() ile yuvarlıyoruz
def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    dataframe.loc[(dataframe[variable] < low_limit), variable] = round(low_limit, 0)
    dataframe.loc[(dataframe[variable] > up_limit), variable] = round(up_limit, 0)


# "order_num_total_ever_online", "order_num_total_ever_offline", "customer_value_total_ever_offline",
# "customer_value_total_ever_online" değişkenlerinin aykırı değerleri varsa baskılıyoruz.
columns = ["order_num_total_ever_online", "order_num_total_ever_offline", "customer_value_total_ever_offline",
           "customer_value_total_ever_online"]

for col in columns:
    replace_with_thresholds(df, col)
df.head()

# Her müşterinin toplam alışveriş sayısı ve harcaması için yeni kolonlar oluşturuyoruz.
df['customer_value_total'] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]
df['order_num_total'] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]

# Değişken tiplerini incelediğimizde tarih değişkenleri object olduğu için bu değişkenlerin tiplerini değiştiriyoruz
df.info()
date_columns = df.columns[df.columns.str.contains("date")]
df[date_columns] = df[date_columns].apply(pd.to_datetime)

# Analiz tarihini belirliyoruz(son alışveriş tarihinden 2 gün sorası olacak şekilde)
df['last_order_date'].max()
today_date = dt.datetime(2021, 6, 1)

# Adım 2: customer_id, recency_cltv_weekly, T_weekly, frequency ve monetary_cltv_avg değerlerinin yer aldığı/
# yeni bir cltv dataframei oluşturuyoruz(monetary değeri satın alma başına ortalama değer olarak, recency ve tenure değerleri ise haftalık olacak)
cltv = pd.DataFrame()
cltv['customer_id'] = df["master_id"]
cltv['recency_cltv_weekly'] = (df["last_order_date"] - df["first_order_date"]).dt.days / 7
cltv['T_weekly'] = (today_date - df["first_order_date"]).dt.days / 7
cltv['frequency'] = df["order_num_total"]
cltv['monetary_cltv_avg'] = df["customer_value_total"] / df["order_num_total"]

cltv.head(10)

# BG/NBD, Gamma-Gamma modellerini kuruyoruz
# BG/NBD modelini fit ediyoruz.
bgf = BetaGeoFitter(penalizer_coef=0.001)

bgf.fit(cltv["frequency"],
        cltv["recency_cltv_weekly"],
        cltv["T_weekly"])

# 3 ay içerisinde müşterilerden beklenen satın almaları 'exp_sales_3_month' olarak ekliyoruz
cltv['exp_sales_3_month'] = bgf.predict(12, cltv["frequency"],
                                        cltv["recency_cltv_weekly"],
                                        cltv["T_weekly"])

# 6 ay içerisinde müşterilerden beklenen satın almaları 'exp_sales_6_month' olarak ekliyoruz
cltv['exp_sales_6_month'] = bgf.predict(24, cltv["frequency"],
                                        cltv["recency_cltv_weekly"],
                                        cltv["T_weekly"])
cltv[['exp_sales_3_month', 'exp_sales_6_month']]

# 3 ve 6 aylık süreçte en yüksek tahmine sahip 10 müşteri listesi
cltv.sort_values("exp_sales_3_month", ascending=False)[:10]
cltv.sort_values("exp_sales_6_month", ascending=False)[:10]

# Gamma-Gamma modelini fit ediyoruz.
ggf = GammaGammaFitter(penalizer_coef=0.01)
ggf.fit(cltv["frequency"], cltv["monetary_cltv_avg"])

# Müşterilerin ortalama bırakacakları değeri tahminleyip exp_average_value olarak cltv dataframe'ine ekliyoruz.
cltv['exp_average_value'] = ggf.conditional_expected_average_profit(cltv['frequency'],
                                                                    cltv['T_weekly'])

# 6 aylık CLTV hesaplayıp dataframe'e ekliyoruz.
cltv['cltv'] = ggf.customer_lifetime_value(bgf,
                                           cltv['frequency'],
                                           cltv['recency_cltv_weekly'],
                                           cltv['T_weekly'],
                                           cltv['T_weekly'],
                                           time=6,
                                           freq='W',
                                           discount_rate=0.01)

# CLTV değeri yüksekliği açısınden TOP 20
cltv.sort_values(by='cltv', ascending=False).head(20)

# CLTV değerine göre segmentleri oluşturuyoruz

# 6 aylık CLTV'ye göre tüm müşterileri 4 segmente ayırıp segment isimlerini dataframe'e ekleyelim.
cltv["segment"] = pd.qcut(cltv['cltv'], 4, labels=['D', 'C', 'B', 'A'])
cltv.head(20)

# 6 aylık CLTV'de toplama göre segmentlerin üzerinde bekletimizi inceliyoruz
cltv.groupby('segment').sum(numeric_only=True).sort_values(by='cltv', ascending=False).head(10)
