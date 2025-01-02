import matplotlib.pyplot as plt
from io import BytesIO
import base64


class ChartGenerator:
    # Bar grafiği oluşturur
    @staticmethod
    def generate_bar_chart(labels, values, title, xlabel, ylabel, rotation=45, color="skyblue"):
        # Grafik boyutunu ayarlar
        plt.figure(figsize=(10, 6))
        # Bar grafiğini çizer
        plt.bar(labels, values, color=color)
        # X ve Y eksenlerini etiketler
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        # Grafiğe başlık ekler
        plt.title(title)
        # X ekseni etiketlerini döndürür
        plt.xticks(rotation=rotation, ha="right")
        # Grafiği sıkı yerleşimle ayarlar
        plt.tight_layout()

        # Görüntüyü belleğe kaydeder
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format="png")
        plt.close()
        img_buffer.seek(0)
        # Görüntüyü base64 formatında döner pdf export fonksiyonu için
        return "data:image/png;base64," + base64.b64encode(img_buffer.read()).decode("utf-8")

    # Çizgi grafiği oluşturur
    @staticmethod
    def generate_line_chart(labels, values, title, xlabel, ylabel, marker="o", rotation=45):
        # Grafik boyutunu ayarlar
        plt.figure(figsize=(10, 6))
        # Çizgi grafiğini çizer
        plt.plot(labels, values, marker=marker, linestyle="-", color="skyblue")
        # X ve Y eksenlerini etiketler
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        # Grafiğe başlık ekler
        plt.title(title)
        # X ekseni etiketlerini döndürür
        plt.xticks(rotation=rotation)
        # Grafiği sıkı yerleşimle ayarlar
        plt.tight_layout()

        # Görüntüyü belleğe kaydeder
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format="png")
        plt.close()
        img_buffer.seek(0)
        # Görüntüyü base64 formatında döner pdf export fonksiyonu için
        return "data:image/png;base64," + base64.b64encode(img_buffer.read()).decode("utf-8")

    # Pie Chart oluşturur
    @staticmethod
    def generate_pie_chart(labels, sizes, title, autopct="%1.1f%%"):
        # Grafik boyutunu ayarlar
        plt.figure(figsize=(8, 8))
        # Pie Chart çizer
        plt.pie(sizes, labels=labels, autopct=autopct, startangle=140)
        # Grafiğe başlık ekler
        plt.title(title)
        # Grafiği sıkı yerleşimle ayarlar
        plt.tight_layout()

        # Görüntüyü belleğe kaydeder
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format="png")
        plt.close()
        img_buffer.seek(0)
        # Görüntüyü base64 formatında döner pdf export fonksiyonu için
        return "data:image/png;base64," + base64.b64encode(img_buffer.read()).decode("utf-8")

    # Dağılım grafiği oluşturur
    @staticmethod
    def generate_scatter_plot(x, y, title, xlabel, ylabel):
        # Grafik boyutunu ayarlar
        plt.figure(figsize=(10, 6))
        # Dağılım grafiğini çizer
        plt.scatter(x, y, color="skyblue", alpha=0.7)
        # X ve Y eksenlerini etiketler
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        # Grafiğe başlık ekler
        plt.title(title)
        # Grafiği sıkı yerleşimle ayarlar
        plt.tight_layout()

        # Görüntüyü belleğe kaydeder
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format="png")
        plt.close()
        img_buffer.seek(0)
        # Görüntüyü base64 formatında döner pdf export fonksiyonu için
        return "data:image/png;base64," + base64.b64encode(img_buffer.read()).decode("utf-8")

    # Histogram oluşturur
    @staticmethod
    def generate_histogram(data, bins, title, xlabel, ylabel):
        # Grafik boyutunu ayarlar
        plt.figure(figsize=(10, 6))
        # Histogramı çizer
        plt.hist(data, bins=bins, color="skyblue", edgecolor="black")
        # X ve Y eksenlerini etiketler
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        # Grafiğe başlık ekler
        plt.title(title)
        # Grafiği sıkı yerleşimle ayarlar
        plt.tight_layout()

        # Görüntüyü belleğe kaydeder
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format="png")
        plt.close()
        img_buffer.seek(0)
        # Görüntüyü base64 formatında döner pdf export fonksiyonu için
        return "data:image/png;base64," + base64.b64encode(img_buffer.read()).decode("utf-8")
