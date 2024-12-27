import matplotlib.pyplot as plt
from io import BytesIO
import base64


class ChartGenerator:
    @staticmethod
    def generate_bar_chart(labels, values, title, xlabel, ylabel, rotation=45, color="skyblue"):
        plt.figure(figsize=(10, 6))
        plt.bar(labels, values, color=color)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.xticks(rotation=rotation, ha="right")
        plt.tight_layout()

        img_buffer = BytesIO()
        plt.savefig(img_buffer, format="png")
        plt.close()
        img_buffer.seek(0)
        return "data:image/png;base64," + base64.b64encode(img_buffer.read()).decode("utf-8")

    @staticmethod
    def generate_line_chart(labels, values, title, xlabel, ylabel, marker="o", rotation=45):
        plt.figure(figsize=(10, 6))
        plt.plot(labels, values, marker=marker, linestyle="-", color="skyblue")
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.xticks(rotation=rotation)
        plt.tight_layout()

        img_buffer = BytesIO()
        plt.savefig(img_buffer, format="png")
        plt.close()
        img_buffer.seek(0)
        return "data:image/png;base64," + base64.b64encode(img_buffer.read()).decode("utf-8")

    @staticmethod
    def generate_pie_chart(labels, sizes, title, autopct="%1.1f%%"):
        plt.figure(figsize=(8, 8))
        plt.pie(sizes, labels=labels, autopct=autopct, startangle=140)
        plt.title(title)
        plt.tight_layout()

        img_buffer = BytesIO()
        plt.savefig(img_buffer, format="png")
        plt.close()
        img_buffer.seek(0)
        return "data:image/png;base64," + base64.b64encode(img_buffer.read()).decode("utf-8")

    @staticmethod
    def generate_scatter_plot(x, y, title, xlabel, ylabel):
        plt.figure(figsize=(10, 6))
        plt.scatter(x, y, color="skyblue", alpha=0.7)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.tight_layout()

        img_buffer = BytesIO()
        plt.savefig(img_buffer, format="png")
        plt.close()
        img_buffer.seek(0)
        return "data:image/png;base64," + base64.b64encode(img_buffer.read()).decode("utf-8")

    @staticmethod
    def generate_histogram(data, bins, title, xlabel, ylabel):
        plt.figure(figsize=(10, 6))
        plt.hist(data, bins=bins, color="skyblue", edgecolor="black")
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.tight_layout()

        img_buffer = BytesIO()
        plt.savefig(img_buffer, format="png")
        plt.close()
        img_buffer.seek(0)
        return "data:image/png;base64," + base64.b64encode(img_buffer.read()).decode("utf-8")
