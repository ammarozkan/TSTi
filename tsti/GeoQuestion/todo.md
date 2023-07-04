- [x] Kütüphanenin daha düzenli baştan yazılması.
- [x] Daha sistematik ve düzenli bir üçgen sistemi.
- [x] Döndürme sistemi
- [x] Sadece 3 nokta ile açı belirtmek.
- [x] Hata deteksiyonu
- [x] "distance A B" gibi "A ile B arasındaki uzaklık" anlamında bir uzaklık komudu.
- [x] Bazı verilerin değişkenlere atanması.
    Örneğin:
    big_angle = angleoftriangle ABC A // ABC üçgenindeki A açısı big_angle değişkenine atandı.

    line a
    line b
    line c
    b cut c A
    a cut c B
    a cut b C
    A,B,C triangle
    ABC median A m1
    m1 cut a E
    median_length = distance A E // ABC üçgeninin A kenarortayının uzunluğu alındı
- [x] Açı ortay, kenar ortay gibi şeyleri "ABC A median A_Median_ABC" gibi bir komutla belirtmek.
    Kullanımları:
    line a
    line b
    line c
    b cut c A
    a cut c B
    a cut b C
    A,B,C triangle
    ABC median A m1
    m1 cut a E

    Bu sayede kenarortayın, başka bir kenarda kestiği nokta belirlenebilir.

- [x] README for geometric language explanation.

- [x] Convert draw functions to class to handle that visual variables, parameters easily.

- [x] Beautiful setting for beutiful shapes.

- [x] Görüntü için alan tarama.

- [ ] Noktalarin ismini hic cizgi olmayan bir yere yazma. Bu renk kontrolu ile saglanabilir.

- [ ] Aynı yeri belirten açıları 2 kez yazmamak.

- [ ] "dot around a A" gibi "a doğrusunda bir A noktası" anlamında bir komut.
