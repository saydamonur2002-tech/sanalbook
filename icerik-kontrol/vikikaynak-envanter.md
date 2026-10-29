# Vikikaynak envanteri

Tarama tarihi: 29 Ekim 2026. Kaynak: tr.wikisource.org MediaWiki API (`https://tr.wikisource.org/w/api.php`). İsteklerde User-Agent `SanalbookBot/1.0 (public-domain literary archive inventory; https://sanalbook.saydamonur2002.workers.dev)` kullanıldı. İstekler arasında en az 1,05 saniye bırakıldı.

Bu dosya site içeriği değildir. `src/` ve `public/` dışında durur. Astro derlemesi onu `dist/` içine kopyalamaz.

## Ad alanı

Yazar sayfaları **Kişi:** ad alanındadır (numara 100, kanonik ad `Kişi`). **Yazar:** ad alanı bu vikide yoktur. `Yazar:Ömer Seyfettin` sorgusu sayfa döndürmedi. Tarama `allpages` ile `apnamespace=100` ve yönlendirme olmayan sayfalar üzerinden yapıldı.

## Kimler listelendi

440 Kişi sayfasının tamamı okundu.

| Durum | Sayı |
|---|---|
| Ölüm yılı ayıklanabildi ve 1955 veya daha eski | 235 |
| Ölüm yılı ayıklanamadı (boş, `?`, yüzyıl, "günümüz" veya alan yok) | 167 |
| Ölüm yılı 1956 veya daha yeni | 38 |

Tabloda bu 235 kişinin hepsi vardır. Tamamlanmış eseri 0 olan 92 kişi de listenin sonundadır. 1956 ve sonrası ile yılı okunamayanlar tabloda yoktur.

Ölüm yılı `{{Kişi}}` şablonundaki `ölümyılı` alanından alındı. O alan boşsa `ölüm tarihi` veya `ölüm` alanına bakıldı. Bunlar da boşsa ve `tarih` bir aralık ise aralığın son yılı kullanıldı. Milattan önceki yıllar eşiğin altında sayıldı. "16. yüzyıl" gibi ifadeler yıl kabul edilmedi.

1956 ve sonrası örnekleri: Reşat Nuri Güntekin (1956), Yahya Kemal Beyatlı (1958), Nâzım Hikmet (1963), Âşık Veysel (1973), Necip Fazıl Kısakürek (1983), Aziz Nesin (1995), Yaşar Kemal (2015).

## Eser sayımı

Tamamlanmış metin: yazar sayfasındaki eser listesinden ana ad alanına giden, yönlendirmesi çözülmüş, şablon ve kaynakça ayıklandıktan sonra en az 20 kelime kalan sayfa. `{{taslak}}`, `{{eksik}}` ve `{{kontrol edilmemiş}}` şablonu taşıyan sayfa bu sayıya girmez. Bu taramada böyle şablon 0 sayfada görüldü.

Listeye alınan bağlantılar, `*` ve `#` satırları ile satırı tek başına dolduran `[[bağlantı]]` satırlarıdır. Hakkında, dış bağlantılar, kaynakça, kendisine hitaben ve uyarlanan başlıklarının altı atlandı. `Dizin:`, `Kategori:`, `Dosya:` ve `w:` bağlantıları eser sayılmadı.

Tür, bağlantının durduğu başlıktan okundu: hikâye veya öykü, roman, şiir (türkü başlıkları şiire yazıldı), tiyatro veya oyun, makale, deneme, mektup, yazı veya düzyazı. Başlık yalnızca "Eserleri" veya "Kitapları" ise tür **diğer**dir. Roman ve tiyatro sütunları bu yüzden, metin o türde olsa bile başlık söylemiyorsa düşük kalır.

| Ölçü | Sayı |
|---|---|
| Benzersiz eser bağlantısı | 1279 |
| Ana ad alanında var olan sayfa | 927 |
| Kırmızı (olmayan) bağlantı | 352 |
| Tamamlanmış benzersiz sayfa | 637 |
| Yazarlara dağıtılmış eser sayısı (Eser sütunu toplamı) | 644 |
| 20 kelimenin altında kaldığı için elenen mevcut sayfa | 290 |
| En az bir tamamlanmış eseri olan kişi | 143 |
| Tamamlanmış eseri 0 olan kişi | 92 |

644 ile 637 arasındaki fark, aynı sayfanın birden fazla kişi sayfasında geçmesidir.

Kaynak baskı: `{{eser başlığı}}` içindeki notlar veya kaynak alanında ilk yayım, bir yıl, mecmua, gazete, matbaa, yayınevi veya basım geçmesi; ya da en az 8 kelimelik bir Kaynakça bölümü. Yalnızca "kalın yazı" gibi dizgi notu kaynak baskı sayılmadı.

Sadeleştirme sütunu, sayfada "sadeleştiren", "sadeleştirme" veya "günümüz Türkçesi" geçen tamamlanmış eserleri sayar. Üç sayfa bu ifadeyi taşıyor:

- Ahmedî, *İskendernâme*. Künyede, transkripsiyona günümüz Türkçesi karşılıkları eklendiği yazılı.
- Kaytazzade Mehmet Nazım, *Gazel-i Hamaset*. Notta "Günümüz Türkçesindeki adı: Yiğitlik Gazeli" geçiyor.
- Osman Gazi, *Osman Gazi'nin Orhan Gazi'ye vasiyeti*. Sayfada "Günümüz Türkçesiyle" başlığı var.

Bu üçünde sadeleştirenin ölüm yılı ayrıca çıkarılmadı. Sadeleştirme de türev bir emektir. Sadeleştirenin ölümü üzerinden 70 yıl dolmadan metin Türkiye'de serbest sayılmaz.

## Çeviri uyarısı

Türkiye'de koruma, hem eser sahibinin hem çevirenin ölüm yılının sonundan itibaren 70 yıldır. Eser, her iki süre de dolduktan sonra, ölüm yılı artı 71 yılının 1 Ocak'ından itibaren serbesttir. 1955'te ölen biri için bu tarih 1 Ocak 2026'dır. Tablodaki kişiler bu eşikte veya daha eskidir. Çeviri sütunu, metnin ayrıca incelenmesi gerektiğini söyler. Çevirenin ölüm yılı eser sayfasında çoğunlukla yoktur. Yıl uydurulmadı.

Çeviri sayılanlar: künyedeki çevirmen, mütercim, aktaran, çeviren veya sadeleştiren alanı dolu olanlar ile kişi sayfasında "Çevirileri" başlığı altında listelenenler. `Kullanıcı:` ile yazılmış çevirmen, Vikikaynak'ta hesabı olan birinin çevirisidir. Bu çağdaş bir çeviridir. Kullanıcının ölüm yılı bilinmez. Metin serbest kabul edilmez. Gövde metnindeki rastgele "çeviri" kelimesi sayılmadı.

Sütun toplamı 15'tir. Bu, 13 ayrı sayfanın bazı kişilerde iki kez sayılmasıdır. *Kur'an* hem Muhammed hem Muhammed Hamdi Yazır satırında, *Proleter Devrim ve Dönek Kautsky* hem Lenin hem Haydar Rifat Yorulmaz satırında durur.

| Eser | Uyarı |
|---|---|
| Proleter Devrim ve Dönek Kautsky | Künye çevirmeni Haydar Rıfat. Kişi sayfasında Haydar Rifat Yorulmaz 1942, Lenin 1924. İki yıl da 1955 eşiğinin altındadır. Bu bir hukuk görüşü değil, sayfadaki yılların yan yana konmasıdır. |
| Sağduyu Tanrısızlığın İlmihali | Abdullah Cevdet'in Çeviriler bölümünde. Abdullah Cevdet 1932. Sayfa ayrıca Jean Meslier (1729) ve d'Holbach (1789) kişi sayfalarına bağlı. |
| Mesnevi (Konuk) | Künye çevirmeni Ahmed Avni Konuk (kişi sayfası 1938). Özgün yazar Mevlânâ (1273). |
| Kur'an | Künye çevirmeni Muhammed Hamdi Yazır (kişi sayfası 1942). Sayılan kelime, surelerin dizin sayfasıdır. Sure alt sayfaları toplanmadı. |
| Milletler Cemiyeti'ne Karşı Çıkan Senatörlerin Sorunu | Notta çeviren bir Vikikaynak kullanıcısı. Özgün yazar Gilbert M. Hitchcock'un kişi sayfası 1934'tür. Türkçe metin çağdaş çeviridir. |
| Türkistan; Ural (şiir); Oral Tavı | Magcan Cumabay (1938). Notta Kazakçadan çeviren bir Vikikaynak kullanıcısı. |
| 28 Nisan; Su ve Rüzgâr; Telefon sohbeti; Yine o bağ olaydı | Mikayıl Müşfik (1938). Çevirmen alanı bir Vikikaynak kullanıcısı. |
| Kıblegâhımdır Ali | Seyyid Nesimi (1417). Çevirmen alanına bir Vikikaynak kullanıcısı yazılmış. Şablon yanlış doldurulmuş olabilir. Kullanıcıya ait bir ölüm yılı olmadığı için uyarı duruyor. |

## Bu taramada okunmadan bırakılanlar

Kelime sayıları ve tamamlanmış metin kararı, eser sayfasının kendi vikimetninden üretildi. Aşağıdakiler okunmadı. Eldeki tarama burada kesildi. `Sayfa:` ad alanına başlanan devam çekimi yarıda durduruldu ve aşağıdaki sayılara katılmadı.

`<pages index="…">` ile gömülen tarama sayfaları okunmadı. Benzersiz `Sayfa:` hedefi yaklaşık 880, etiket sayısı 127'dir. Vikimetni kısa olduğu için bu eserlerin bir kısmı 20 kelime eşiğinin altında kaldı ve kişi satırında 0 göründü. En geniş aralıklar:

- *İstiklâl Harbimizin Esasları*, 208 sayfa
- *Kürk Mantolu Madonna* (Sabahattin Ali, ölüm 1948), 180 sayfa. Kişi satırında eser 0'dır. Sayfa neredeyse yalnızca djvu gömüsüdür.
- *Türk Sazı*, 132 sayfa
- *Ebedi Şefimiz Atatürkün İstanbul ve Ankaradaki Cenaze Töreni Albümü*, 100 sayfa
- *İstanbul'da Semai Kahveleri ve Meydan Şairleri*, 33 sayfa
- *Antigone*, 26 sayfa. Dizin dosyasının adı `Sophokles - Antigone çev. Sabahattin Ali.pdf`. Metin okunmadığı için Sofokles satırına yazılmadı. Çeviri olduğu dosya adından bellidir. Sabahattin Ali'nin kişi sayfasındaki ölüm yılı 1948'dir. Bu da hukuk görüşü değil, dosya adı ile kişi sayfasının yan yana konmasıdır.

Yazar sayfasında ayrı satır olmayan alt sayfalar toplanmadı. *Kur'an/Fâtiha Suresi*, *Rübâb-ı Şikeste* alt sayfaları ve *Kuyucaklı Yusuf/Birinci Kısım* bu gruptadır. *Kuyucaklı Yusuf* bir içindekiler sayfasıdır ve eser sayısına girmez.

Mehmet Rauf (1931) satırı 0'dır. Hikâyeleri, Romanları ve Tiyatro Oyunları altındaki 34 bağlantının hepsi kırmızıdır.

Roman sütunu toplamı 0, tiyatro sütunu toplamı 0'dır. "Romanları" başlığı altındaki bağlantılar ya yoktur ya da vikimetni 20 kelimenin altındadır. Başlığı "Eserleri" olan uzun metinler **diğer** sütunundadır.

Köşeli parantezle bağlanmamış düz ad listeleri sayılamadı. Rudyard Kipling sayfasındaki kitap adları böyledir.

`Dizin:` PDF dizinleri eser sayılmadı.

## Tablo

Eser sayısına göre azalan, eşitlikte yazar adına göre sıralı. Eser, tamamlanmış metin sayısıdır. Kaynak baskılı, sadeleştirme ve çeviri uyarısı bu tamamlanmış metinlerin içindedir. Taslak/eksik, eşiğin dışında ayrıca sayılmıştır.

| Yazar | Ölüm | Eser | Hikâye | Roman | Şiir | Tiyatro | Makale | Diğer | Kaynak baskılı | Sadeleştirme | Taslak/eksik | Çeviri uyarısı |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ömer Seyfettin | 1920 | 64 | 64 | 0 | 0 | 0 | 0 | 0 | 12 | 0 | 0 | 0 |
| Ahmet Haşim | 1933 | 51 | 0 | 0 | 37 | 0 | 14 | 0 | 4 | 0 | 0 | 0 |
| Mehmet Âkif Ersoy | 1936 | 48 | 0 | 0 | 48 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| Yunus Emre | 1321 | 42 | 0 | 0 | 0 | 0 | 0 | 42 | 0 | 0 | 0 | 0 |
| Mustafa Kemal Atatürk | 1938 | 38 | 0 | 0 | 0 | 0 | 8 | 30 | 9 | 0 | 0 | 0 |
| Fuzûlî | 1556 | 30 | 0 | 0 | 0 | 0 | 5 | 25 | 2 | 0 | 0 | 0 |
| Kanuni Sultan Süleyman | 1566 | 19 | 0 | 0 | 10 | 0 | 1 | 8 | 4 | 0 | 0 | 0 |
| Karacaoğlan | 1689 | 15 | 0 | 0 | 12 | 0 | 0 | 3 | 0 | 0 | 0 | 0 |
| Bâkî | 1600 | 14 | 0 | 0 | 0 | 0 | 0 | 14 | 0 | 0 | 0 | 0 |
| Nâbi | 1718 | 13 | 0 | 0 | 13 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Nedim | 1730 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 |
| Seyyid Nesimi | 1417 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 1 | 0 | 0 | 1 |
| Abdülaziz | 1876 | 8 | 0 | 0 | 0 | 0 | 0 | 8 | 6 | 0 | 0 | 0 |
| Ali Ekrem Bolayır | 1937 | 8 | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Sıdkı Baba | 1928 | 8 | 0 | 0 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 0 |
| Eşrefoğlu Rumî | 1469 | 7 | 0 | 0 | 0 | 0 | 0 | 7 | 0 | 0 | 0 | 0 |
| Necati | 1509 | 7 | 0 | 0 | 0 | 0 | 0 | 7 | 0 | 0 | 0 | 0 |
| Celâl Sahir Erozan | 1935 | 6 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Harabi | 1917 | 6 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 |
| Namık Kemal | 1889 | 6 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Tevfik Fikret | 1915 | 6 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 |
| Şeyhî | 1431 | 6 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 |
| Abdülhak Hamit Tarhan | 1937 | 5 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Aleksandr Aleksandrov | 1946 | 5 | 0 | 0 | 0 | 0 | 0 | 5 | 5 | 0 | 0 | 0 |
| Kaytazzade Mehmet Nazım | 1924 | 5 | 0 | 0 | 4 | 0 | 0 | 1 | 0 | 1 | 0 | 0 |
| Süleyman Nazif | 1927 | 5 | 0 | 0 | 0 | 0 | 4 | 1 | 5 | 0 | 0 | 0 |
| Tevhide Hanım | 1901 | 5 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 |
| Ziya Gökalp | 1924 | 5 | 0 | 0 | 5 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| Fıtnat Hanım | 1780 | 4 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 |
| Kadı Burhaneddin | 1398 | 4 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 |
| Magcan Cumabay | 1938 | 4 | 0 | 0 | 4 | 0 | 0 | 0 | 3 | 0 | 0 | 3 |
| Mikayıl Müşfik | 1938 | 4 | 0 | 0 | 0 | 0 | 0 | 4 | 4 | 0 | 0 | 4 |
| Nebîl | 1890 | 4 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 |
| Rüştü Onur | 1944 | 4 | 0 | 0 | 0 | 0 | 0 | 4 | 3 | 0 | 0 | 0 |
| Vladimir İlyiç Lenin | 1924 | 4 | 0 | 0 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 1 |
| Ziya Paşa | 1880 | 4 | 0 | 0 | 0 | 0 | 1 | 3 | 0 | 0 | 0 | 0 |
| Âşık Elesker | 1926 | 4 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 |
| II. Abdülhamid | 1918 | 4 | 0 | 0 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 0 |
| Bursalı Âşık Yunus | 1439 | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 |
| Erzurumlu İbrahim Hakkı | 1780 | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 |
| Hatice Nakiye Hanım | 1899 | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 |
| Leylâ Hanım | 1936 | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 |
| Osman Gazi | 1326 | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 1 | 1 | 0 | 0 |
| Yavuz Sultan Selim | 1520 | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 |
| Âdile Sultan | 1899 | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 |
| II. Mehmed | 1481 | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 1 | 0 | 0 | 0 |
| Şeref Hanım | 1861 | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 |
| Abdülmecit | 1861 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| Abraham Lincoln | 1865 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| Agahi | 1921 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| Ahmed Cevad | 1937 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| Aşık Dertli | 1846 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| Enderunlu Vasıf | 1824 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| Erbabi | 1884 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| Hayretî | 1534 | 2 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| İsmail Hakkı Bey | 1927 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| Josef Stalin | 1953 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 2 | 0 | 0 | 0 |
| Kâtip Çelebi | 1657 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 1 | 0 | 0 | 0 |
| Mahmut Esat Bozkurt | 1943 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 1 | 0 | 0 | 0 |
| Mevlânâ Celâleddîn-i Rûmî | 1273 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| Mihrî Hatun | 1506 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| Rahmî | 1752 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| Recaizade Mahmut Ekrem | 1914 | 2 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Rifat Bey | 1888 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| Rıza Tevfik Bölükbaşı | 1949 | 2 | 0 | 0 | 2 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| Süleyman Çolpan | 1938 | 2 | 0 | 0 | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| Sümmani | 1915 | 2 | 0 | 0 | 2 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| Zati Arca | 1943 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| Âşık Ömer | 1707 | 2 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| I. Ahmet | 1617 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| II. Bayezid | 1566 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| II. Mahmud | 1839 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| II. Murat | 1451 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 1 | 0 | 0 | 0 |
| II. Selim | 1574 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 2 | 0 | 0 | 0 |
| Şeyh Galip | 1799 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| Şâkir | 1745 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| Abdullah Cevdet | 1932 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 |
| Adolf Hitler | 1945 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| Ahmed Avni Konuk | 1938 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 |
| Ahmed Sadık Zîver Paşa | 1862 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Ahmed Yesevi | 1166 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Ahmedî | 1413 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 |
| Ahmet Rasim | 1932 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Albert Einstein | 1955 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Antepli Aynî | 1837 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Buhurizade Mustafa Itri | 1712 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Cenab Şahabeddin | 1934 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| Cevrî | 1654 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Dionisos Solomos | 1857 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 |
| Dziga Vertov | 1954 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Eleftherios Venizelos | 1936 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| Feride Hanım | 1903 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Gilbert M. Hitchcock | 1934 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 |
| Hafız Ahmet Paşa | 1632 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Haydar Rifat Yorulmaz | 1942 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 1 |
| Hipokrat | MÖ 377 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| İbrahim Alâeddin Gövsa | 1949 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| İbrahim Şinâsî | 1871 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| İzzeddin Hasanoğlu | 1260 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 |
| Jean Meslier | 1729 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| John Keats | 1821 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Kemalettin Kamu | 1948 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 |
| Kâşgarlı Mahmud | 1105 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Lala Mustafa Paşa | 1580 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 |
| Lavrenti Beria | 1953 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 |
| Lev Troçki | 1940 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 |
| Lâmekânî | 1625 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 |
| Mahmud Şevket Paşa | 1913 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Mehmed Dâniş | 1837 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Mehmet Ali Bey | 1895 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 |
| Mehmet Ali Ertekin | 1948 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Mehmet Şerif Avcıoğlu | 1929 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Mezâkî | 1676 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Muhammed | 632 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 |
| Muhammed Hamdi Yazır | 1942 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 |
| Muhlis Sabahattin Ezgi | 1947 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 |
| Muhyiddin Abdal | 1529 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Nefi | 1635 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Niyâzî-i Mısrî | 1694 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Orhan Gazi | 1362 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 |
| Paul Henri Thiry d'Holbach | 1789 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Reşit Galip | 1934 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 |
| Süleyman Senîh Efendi | 1900 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 |
| Süleyman Çelebi | 1422 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Thomas Aquinas | 1274 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 |
| Vasıf Osman Bey | 1824 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Virginia Woolf | 1941 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| William Blake | 1827 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Yunus Nadi Abalıoğlu | 1945 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Âşık Mesleki | 1939 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Âşık Necef Daşkentli | 1919 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Âşık Şenlik | 1913 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Ömer Bedrettin Uşaklı | 1946 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Üsküdarlı Nûri Mehmed Efendi | 1721 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| I. Abdülhamit | 1789 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| I. Mahmud | 1754 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 |
| I. Murat | 1389 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| IV. Mehmet | 1693 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| IV. Murat | 1640 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| III. Mehmed | 1603 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| III. Murad | 1595 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| III. Mustafa | 1774 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| III. Selim | 1808 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Abdî | 1769 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Abdürrezzâk Nevres | 1762 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Ahmed Paşa | 1497 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Ahmet Refik Altınay | 1937 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Ak Aşık | 1860 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Ani Hatun | 1710 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Arthur James Balfour | 1930 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Arşî | 1562 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Askerî | 1591 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Aziz Samih İlter | 1948 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Balım Sultan | 1516 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Barbaros Hayreddin Paşa | 1546 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Bağdadlı Rûhî | 1605 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Cemil Bilsel | 1949 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Cengiz Han | 1227 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Daniel Defoe | 1731 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Enver Paşa | 1922 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Ezop | MÖ 560 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Fazli | 1605 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Firedrich Schiller | 1805 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Francis Walsingham | 1590 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Friedrich Engels | 1895 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| George Washington | 1799 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Halid Ziya Uşaklıgil | 1945 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Hayalî | 1557 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Husrev | 1595 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Hüseyin Dâniş | 1943 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Hüseynî | 1621 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| İbnürrefik Ahmet Nuri | 1935 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| James Young Simpson | 1870 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Jean de La Fontaine | 1695 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Jean-François Champollion | 1832 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Kalender Çelebi | 1528 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Karl Marx | 1883 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Kemani Serkis Efendi | 1944 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Kul Hasan | 1736 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Kânî | 1791 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Kâzım Karabekir | 1948 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Maksim Gorki | 1936 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Matsuo Basho | 1694 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Matthías Jochumsson | 1920 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Mazhar Müfit Kansu | 1948 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Mehmed Talat | 1921 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Mehmet Emin Yurdakul | 1944 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Mehmet Rauf | 1931 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Memduh Şevket Esendal | 1952 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Muhyî-i Gülşenî | 1605 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Nemayî | 1596 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Neyzen Tevfik | 1953 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Orhan Veli Kanık | 1950 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Oscar Wilde | 1900 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Osman Cemal Kaygılı | 1945 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Rabindranth Tagore | 1941 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Rudyard Kipling | 1936 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Ruhsatî | 1911 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Sabahattin Ali | 1948 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Sadettin Nüzhet Ergun | 1946 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Sekula Drljević | 1945 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Senih Efendi | 1900 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Sergey Vitte | 1915 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Sermed | 1787 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Sersem Ali Baba | 1569 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Seydi Ali Reis | 1562 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Sofokles | 406 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Sâmih Rifat | 1932 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Sânî | 1586 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Sürûrî | 1591 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Timur | 1405 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| V. Mehmet | 1918 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| V. Murad | 1904 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Vahdeti Baba | 1598 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| VI. Mehmed | 1926 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| William Shakespeare | 1616 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Yetim Ali Çelebi | 1552 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Yusuf Has Hacib | 1077 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Yıldırım Bayezit | 1403 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Zekeriyazade Yahya | 1644 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Zâtî | 1546 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| I. Ferdinand (Bulgaristan) | 1948 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| I. İbrahim | 1648 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| I. Mehmet | 1421 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| I. Mustafa | 1639 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| IV. Mustafa | 1808 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| II. Ahmet | 1695 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| II. Mustafa | 1703 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| II. Osman | 1622 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| II. Süleyman | 1691 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| III. Ahmet | 1736 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| III. Osman | 1757 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Şeref Aykut | 1939 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Şeyh Edebali | 1326 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Şinasi | 1871 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **Toplam** | — | 644 | 64 | 0 | 176 | 0 | 35 | 369 | 92 | 3 | 0 | 15 |

## Kelime sayısı en yüksek 10 eser

Kelime, eser sayfasının kendi vikimetnidir. Şablonlar, ref etiketleri ve Kaynakça / Dipnotlar / Notlar bölümleri çıkarılmıştır. `<pages>` gömüleri ve alt sayfalar eklenmemiştir. Bu yüzden tarama olarak duran romanlar bu listede yoktur. *Kürk Mantolu Madonna* buna örnektir.

| Sıra | Eser | Bağlı kişi sayfaları | Tür | Kelime | Çeviri uyarısı |
|---|---|---|---|---|---|
| 1 | Proleter Devrim ve Dönek Kautsky | Haydar Rifat Yorulmaz; Vladimir İlyiç Lenin | diğer | 26130 | Haydar Rıfat |
| 2 | Sefâretnâme-i Şâhî | Mehmed Dâniş | diğer | 6344 | — |
| 3 | Kütük | Ömer Seyfettin | hikâye | 4452 | — |
| 4 | Bomba | Ömer Seyfettin | hikâye | 4417 | — |
| 5 | Dîvânü Lugâti't-Türk | Kâşgarlı Mahmud | diğer | 3943 | — |
| 6 | Zeytin Ekmek | Ömer Seyfettin | hikâye | 3776 | — |
| 7 | Sağduyu Tanrısızlığın İlmihali | Abdullah Cevdet; Jean Meslier; Paul Henri Thiry d'Holbach | diğer | 3648 | Çeviriler bölümünde listelendi |
| 8 | Atatürk'ün İzmir İktisad Kongresi Konuşması | Mustafa Kemal Atatürk | diğer | 3298 | — |
| 9 | Fon Sadriştayn’ın Oğlu | Ömer Seyfettin | hikâye | 3158 | — |
| 10 | Fon Sadriştayn’ın Karısı | Ömer Seyfettin | hikâye | 3118 | — |
