import csv
import random
from datetime import datetime, timedelta

def create_sample_csv():
    """Örnek CSV dosyası oluşturur"""
    
    # Örnek veriler
    names = ["Ahmet Yılmaz", "Fatma Demir", "Mehmet Kaya", "Ayşe Çelik", "Mustafa Öz", 
             "Zeynep Akar", "Ali Şahin", "Hatice Yıldız", "İbrahim Koç", "Emine Arslan"]
    
    cities = ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Konya", "Gaziantep", "Kayseri"]
    
    departments = ["IT", "İnsan Kaynakları", "Pazarlama", "Satış", "Muhasebe", "Üretim"]
    
    # CSV dosyası oluştur
    with open('ornek_calisanlar.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Başlıklar
        writer.writerow(['ad_soyad', 'departman', 'maas', 'sehir', 'ise_baslama_tarihi', 'aktif'])
        
        # 50 örnek kayıt
        for i in range(50):
            name = random.choice(names)
            department = random.choice(departments)
            salary = random.randint(5000, 25000)
            city = random.choice(cities)
            start_date = (datetime.now() - timedelta(days=random.randint(30, 1095))).strftime('%Y-%m-%d')
            active = random.choice([True, False])
            
            writer.writerow([name, department, salary, city, start_date, active])
    
    print("Örnek CSV dosyası 'ornek_calisanlar.csv' oluşturuldu!")
    print("Bu dosyayı test etmek için kullanabilirsiniz.")

if __name__ == "__main__":
    create_sample_csv()
