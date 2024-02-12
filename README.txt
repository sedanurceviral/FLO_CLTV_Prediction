FLO_CLTV_PREDICTION
-Veri Toplama
CLTV tahmini yapmak için öncelikle FLO mağazasının veri tabanından gerekli bilgileri çekmek gereklidir.

-Veri Ön İşleme
Verileri topladıktan sonra verileri ön işlemeye tabi tutmak gerekir. Ön işleme adımları arasında: verilerin temizlenmesi, eksik verilerin doldurulması ve verilerin yeni özelliklerinin oluşturulması yer almaktadır. 
Veri öncesinde temizlendiği için aykırı verileri baskılamak yeterli oldu. Aynı zamanda CLTV veri yapısını oluşturmak için recancy, tenure değerleri haftalık, monetary değeri satın alma başına ortalama olarak hesaplandı.

-BG/NBD Modeli Kurulması ve Satın Alma Tahmini
BG/NBD model insanların satın alma davranışlarının olasılık dağılımının beklenen değerini bireyler özelinde biçimlendirerek her bir birey için beklenen işlem sayısını tahminlendirir
bu da müşterilerin satın alma alışkanlıklarını ve değerlerini belirlemeye yardımcı olur.

-Gamma Gamma Submodel Kurulması ve Kar Tahmini
Bir müşterinin işlemlerinin parasal değeri işlem oranı etrafında rastgele dağılır ortalama işlem oranı zaman içinde kullanıcılar arasında değişebilir ama tek bir kullanıcı
için değişmez. Bu sayede müşteri başına bırakılan parasal değer hesaplanabilir.

-BG/NBD ve Gamma Gamma Submodel ile CLTV'nin Hesaplanması
İki modelin çarpımı ile zaman projeksiyonlu olasılıksal olarak müşteri yaşam boyu değerini bulabiliriz.

-Müşteri Segmentasyonu
CLTV hesaplandıktan sonra, müşteriler segmentlere ayrılabilir. Bu segmentler, müşterilerin satın alma davranışlarını ve değerlerini incelememizi sağlar.

-Müşteri Yaşam Boyu Değeri Tahmini Sonuçlarının Yorumlanması
 Sonuçların yorumlanması, müşterilerin satın alma alışkanlıklarını ve değerlerini anlamamızı sağlar. Bu inceleme ile müşterilerin ihtiyaçlarını belirleyip müşteri memnuniyetini artırmaya dayalı aksiyonlar almaya yardımcı olur.

-Sonuç
Bu belge FLO mağazasının online/offline satın alşveriş verilerini kullanarak CLTV tahmini için gerekli adımları içerir. Bu adımlar, basit bir CLTV projesinin geliştirilmesi sürecinde gereklidir.