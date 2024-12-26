import matplotlib.pyplot as plt
from io import BytesIO
import base64


class ChartGenerator:
    @staticmethod
    def generate_bar_chart(data, title, xlabel, ylabel):
        plt.figure(figsize=(8, 4))
        plt.bar(range(len(data["labels"])), data["values"], color="skyblue")
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.xticks(range(len(data["labels"])), data["labels"], rotation=45)
        plt.tight_layout()

        img_buffer = BytesIO()
        plt.savefig(img_buffer, format="png")
        plt.close()
        img_buffer.seek(0)
        return "data:image/png;base64," + base64.b64encode(img_buffer.read()).decode("utf-8")

    @staticmethod
    def generate_line_chart(data, title, xlabel, ylabel):
        plt.figure(figsize=(8, 4))
        plt.plot(data["labels"], data["values"], marker="o")
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.xticks(rotation=45)
        plt.tight_layout()

        img_buffer = BytesIO()
        plt.savefig(img_buffer, format="png")
        plt.close()
        img_buffer.seek(0)
        return "data:image/png;base64," + base64.b64encode(img_buffer.read()).decode("utf-8")
